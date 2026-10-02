"""联赛日程规则与日志保留期的回归测试（F-82）。

锁定实现既有语义：
- `rounds`（局数）创建后不可修改：`ScheduleUpdate` 不含该字段（Pydantic 忽略传入值），DB 另有 CHECK 1-3；
- `round_results` 长度必须等于 `rounds`，取值限 `win/lose/draw/pending`；
- `profession_config` 覆盖：职业须合法（须为目标人数 0-60 的整数）；
- 日志保留：`LOG_RETENTION_DAYS` 默认 90，`clear_old_logs` 只删除早于保留期的记录，返回删除条数。
"""
from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.database import Base
from app.models.guild import Guild
from app.models.operation_log import OperationLog
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleUpdate
from app.services import log_service, schedule_service
from app.services.schedule_service import ScheduleServiceError


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="日程规则测试")
        self.session.add(guild)
        await self.session.flush()
        self.gid = guild.id
        self.schedule = Schedule(guild_id=self.gid, opponent="对手",
                                 match_time=datetime.now(timezone.utc), rounds=2)
        self.session.add(self.schedule)
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()


class ScheduleRulesTest(_Base):
    def test_rounds_is_not_updatable_field(self) -> None:
        self.assertNotIn("rounds", ScheduleUpdate.model_fields,
                         "更新模型不得暴露 rounds（文档：创建后不可修改）")

    async def test_round_results_length_must_match_rounds(self) -> None:
        with self.assertRaises(ScheduleServiceError):
            await schedule_service.update_schedule(
                self.session, self.gid, self.schedule.id,
                ScheduleUpdate(round_results=["win", "lose", "pending"]))
        await self.session.rollback()
        updated = await schedule_service.update_schedule(
            self.session, self.gid, self.schedule.id,
            ScheduleUpdate(round_results=["win", "pending"]))
        self.assertEqual(updated.round_results, ["win", "pending"])

    async def test_round_results_value_whitelist(self) -> None:
        with self.assertRaises(ScheduleServiceError):
            await schedule_service.update_schedule(
                self.session, self.gid, self.schedule.id,
                ScheduleUpdate(round_results=["win", "赚了"]))
        await self.session.rollback()

    async def test_profession_config_bounds(self) -> None:
        with self.assertRaises(ScheduleServiceError):
            await schedule_service.update_profession_config(self.session, self.gid, self.schedule.id,
                                                            {"铁衣": 61})
        await self.session.rollback()
        with self.assertRaises(ScheduleServiceError):
            await schedule_service.update_profession_config(self.session, self.gid, self.schedule.id,
                                                            {"不存在职业": 3})
        await self.session.rollback()
        ok = await schedule_service.update_profession_config(self.session, self.gid, self.schedule.id,
                                                            {"铁衣": 60})
        self.assertEqual(ok.profession_config, {"铁衣": 60})

    def test_default_retention_days_is_90(self) -> None:
        self.assertEqual(settings.LOG_RETENTION_DAYS, 90, "默认保留天数应为 90（DEPLOY.md §四）")

    async def test_clear_old_logs_keeps_recent(self) -> None:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        self.session.add_all([
            OperationLog(username="u", module="other", action="update", method="PUT", path="/x",
                         level="info", created_at=now - timedelta(days=91)),
            OperationLog(username="u", module="other", action="update", method="PUT", path="/x",
                         level="info", created_at=now - timedelta(days=89)),
        ])
        await self.session.commit()
        with patch.object(log_service, "async_session_factory", self.maker):
            deleted = await log_service.clear_old_logs(90)
        self.assertEqual(deleted, 1, "只应删除超出保留期的记录")
        left = (await self.session.execute(select(func.count()).select_from(OperationLog))).scalar()
        self.assertEqual(left, 1)


if __name__ == "__main__":
    unittest.main()
"""出勤/录屏写入路径与数据库约束的兼容性回归测试（F-79 反向验证）。

背景：2026-10-03 为补人补上了数据库级部分唯一索引（迁移 p0q1r2s3t4u5）。
必须确认既有业务路径**不会因此抛 IntegrityError**：
- 重复导入成员 → 应「跳过已存在」而非报错；
- 重复添加补人 → 应给出**业务友好错误**（AttendanceServiceError），而非数据库异常；
- 录屏占位重复初始化（ensure_recordings 二次调用）→ 应复用既有记录、不新增；
- 正常状态超过 60 人上限 → 应按文档给出业务错误。
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.member import Member
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.services import attendance_service, recording_service
from app.services.attendance_service import AttendanceServiceError
from app.utils import attendance_import


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="导入路径测试")
        self.session.add(guild)
        await self.session.flush()
        self.gid = guild.id
        self.schedule = Schedule(guild_id=self.gid, opponent="对手",
                                 match_time=datetime.now(timezone.utc), rounds=1)
        self.session.add(self.schedule)
        await self.session.flush()
        self.sid = self.schedule.id

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _add_members(self, n: int, status: str = "formal") -> list[Member]:
        members = [Member(guild_id=self.gid, name=f"成员{i:02d}", main_profession="铁衣", status=status)
                   for i in range(n)]
        self.session.add_all(members)
        await self.session.commit()
        return members


class AttendanceImportPathsTest(_Base):
    async def test_import_formal_twice_is_idempotent(self) -> None:
        await self._add_members(3)
        first = await attendance_import.import_formal(self.session, self.gid, self.sid)
        second = await attendance_import.import_formal(self.session, self.gid, self.sid)
        self.assertEqual(first["imported"], 3)
        self.assertEqual(second["imported"], 0, "重复导入不应新增")
        self.assertEqual(second["skipped"], 3, "重复导入应全部跳过")
        total = (await self.session.execute(
            select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.schedule_id == self.sid)
        )).scalar()
        self.assertEqual(total, 3, "出勤行数应保持 3")

    async def test_import_members_twice_is_idempotent(self) -> None:
        members = await self._add_members(2)
        ids = [m.id for m in members]
        first = await attendance_import.import_members(self.session, self.gid, self.sid, ids)
        second = await attendance_import.import_members(self.session, self.gid, self.sid, ids)
        self.assertEqual(first["imported"], 2)
        self.assertEqual(second["imported"], 0)

    async def test_duplicate_filler_is_business_error(self) -> None:
        await attendance_service.add_filler(self.session, self.gid, self.sid, "补人甲", "铁衣")
        with self.assertRaises(AttendanceServiceError):
            await attendance_service.add_filler(self.session, self.gid, self.sid, "补人甲", "素问")
        await self.session.rollback()
        total = (await self.session.execute(
            select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.schedule_id == self.sid)
        )).scalar()
        self.assertEqual(total, 1)

    async def test_ensure_recordings_twice_does_not_duplicate(self) -> None:
        await self._add_members(2)
        await attendance_import.import_formal(self.session, self.gid, self.sid)
        records = (await self.session.execute(
            select(AttendanceRecord).where(AttendanceRecord.schedule_id == self.sid)
        )).scalars().all()
        await recording_service.ensure_recordings(self.session, self.schedule, list(records))
        await recording_service.ensure_recordings(self.session, self.schedule, list(records))
        total = (await self.session.execute(
            select(func.count()).select_from(Recording).where(Recording.schedule_id == self.sid)
        )).scalar()
        self.assertEqual(total, 2 * self.schedule.rounds, "每人每局一条，二次调用不得新增")

    async def test_normal_capacity_limit_enforced(self) -> None:
        """文档：正常状态人数上限 60 人（应用层校验）。"""
        await self._add_members(61)
        with self.assertRaises(AttendanceServiceError):
            await attendance_import.import_formal(self.session, self.gid, self.sid)
        await self.session.rollback()


if __name__ == "__main__":
    unittest.main()

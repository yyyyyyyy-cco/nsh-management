"""赛程级联删除的回归测试（F-75）。

背景：`database-design.md §3.2` 规定删除赛程时按
recordings → match_data → squad_adjustments → attendance_records → lineups → schedules 顺序清理。
2026-10-03 发现实现漏删 `squad_adjustments`（Schedule 与该表之间没有 ORM relationship，
FK 也未声明 ondelete="CASCADE"，故 ORM/DB 都不会级联）——删赛程后留下孤儿行；
又因未启用 `sqlite_autoincrement`，`schedules.id` 可能被复用，新赛程会"继承"旧分析调整。
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.match_data import MatchData
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.models.squad_adjustment import SquadAdjustment
from app.services import schedule_service


class ScheduleCascadeTest(unittest.TestCase):
    """删除赛程必须清空全部从表（含 squad_adjustments）。"""

    def _run(self, coro):
        import asyncio

        return asyncio.run(coro)

    def test_delete_schedule_removes_all_children(self) -> None:
        async def scenario() -> None:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            maker = async_sessionmaker(engine, expire_on_commit=False)
            async with maker() as session:
                guild = Guild(name="级联测试帮会")
                session.add(guild)
                await session.flush()
                schedule = Schedule(guild_id=guild.id, opponent="对手",
                                    match_time=datetime.now(timezone.utc), rounds=1)
                session.add(schedule)
                await session.flush()
                sid = schedule.id
                session.add_all([
                    SquadAdjustment(schedule_id=sid, data={"甲": "0:0"}),
                    AttendanceRecord(schedule_id=sid, member_name="甲", profession="铁衣", status="normal"),
                    Lineup(schedule_id=sid, data=[]),
                    Recording(schedule_id=sid, member_name="甲", round_number=1, status="pending"),
                    MatchData(schedule_id=sid, player_name="甲", camp="己方", round_no=1),
                ])
                await session.commit()

                await schedule_service.delete_schedule(session, guild.id, sid)

                for model, label in ((SquadAdjustment, "squad_adjustments"), (AttendanceRecord, "attendance_records"),
                                     (Lineup, "lineups"), (Recording, "recordings"), (MatchData, "match_data")):
                    left = (await session.execute(
                        select(func.count()).select_from(model).where(model.schedule_id == sid)
                    )).scalar()
                    self.assertEqual(left, 0, f"删除赛程后 {label} 仍残留 {left} 行（级联删除不完整）")
                left_sched = (await session.execute(
                    select(func.count()).select_from(Schedule).where(Schedule.id == sid)
                )).scalar()
                self.assertEqual(left_sched, 0, "赛程本身应已删除")
            await engine.dispose()

        self._run(scenario())


if __name__ == "__main__":
    unittest.main()

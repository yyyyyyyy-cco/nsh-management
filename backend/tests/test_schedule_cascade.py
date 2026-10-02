"""赛程级联删除的回归测试（F-75）。

背景：`database-design.md §3.2` 规定删除赛程时按
recordings → match_data → squad_adjustments → attendance_records → lineups → schedules 顺序清理。
2026-10-03 发现实现漏删 `squad_adjustments`（Schedule 与该表之间没有 ORM relationship，
FK 也未声明 ondelete="CASCADE"，故 ORM/DB 都不会级联）——删赛程后留下孤儿行；
又因未启用 `sqlite_autoincrement`，`schedules.id` 可能被复用，新赛程会"继承"旧分析调整。
"""
from __future__ import annotations

import unittest
from datetime import UTC, datetime

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
                                    match_time=datetime.now(UTC), rounds=1)
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


class GuildCascadeTest(unittest.TestCase):
    """删除帮会必须清空全部关联数据（含 squad_adjustments）。F-77。"""

    def test_delete_guild_removes_schedule_children_and_guild_rows(self) -> None:
        import asyncio

        from app.models.guild import Guild
        from app.models.member import Member
        from app.models.profession import ProfessionConfig
        from app.models.user import User
        from app.services import guild_service

        async def scenario() -> None:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            maker = async_sessionmaker(engine, expire_on_commit=False)
            async with maker() as session:
                guild = Guild(name="待删帮会")
                session.add(guild)
                await session.flush()
                gid = guild.id
                schedule = Schedule(guild_id=gid, opponent="对手",
                                    match_time=datetime.now(UTC), rounds=1)
                session.add(schedule)
                await session.flush()
                sid = schedule.id
                session.add_all([
                    SquadAdjustment(schedule_id=sid, data={"甲": "0:0"}),
                    AttendanceRecord(schedule_id=sid, member_name="甲", profession="铁衣", status="normal"),
                    Lineup(schedule_id=sid, data=[]),
                    Recording(schedule_id=sid, member_name="甲", round_number=1, status="pending"),
                    MatchData(schedule_id=sid, player_name="甲", camp="己方", round_no=1),
                    Member(guild_id=gid, name="甲", main_profession="铁衣", status="active"),
                    ProfessionConfig(guild_id=gid, profession="铁衣", target_count=3),
                ])
                await session.commit()

                await guild_service.delete_guild(session, gid)

                for model, label in ((SquadAdjustment, "squad_adjustments"), (AttendanceRecord, "attendance_records"),
                                     (Lineup, "lineups"), (Recording, "recordings"), (MatchData, "match_data"),
                                     (Schedule, "schedules"), (Member, "members"),
                                     (ProfessionConfig, "profession_configs")):
                    left = (await session.execute(select(func.count()).select_from(model))).scalar()
                    self.assertEqual(left, 0, f"删除帮会后 {label} 仍残留 {left} 行")
                left_guild = (await session.execute(
                    select(func.count()).select_from(Guild).where(Guild.id == gid))).scalar()
                self.assertEqual(left_guild, 0, "帮会本身应已删除")
                # users 表：developer 不绑定帮会，故按 guild_id 统计即可
                left_users = (await session.execute(
                    select(func.count()).select_from(User).where(User.guild_id == gid))).scalar()
                self.assertEqual(left_users, 0, "该帮会账号应已删除")
            await engine.dispose()

        asyncio.run(scenario())


class MemberDetachTest(unittest.TestCase):
    """删除成员后：历史行保留但解除成员引用（防主键复用误关联）。F-78。"""

    def test_delete_member_nulls_history_references(self) -> None:
        import asyncio

        from app.models.guild import Guild
        from app.models.member import Member
        from app.services import member_service

        async def scenario() -> None:
            engine = create_async_engine("sqlite+aiosqlite:///:memory:")
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            maker = async_sessionmaker(engine, expire_on_commit=False)
            async with maker() as session:
                guild = Guild(name="解绑测试帮会")
                session.add(guild)
                await session.flush()
                gid = guild.id
                member = Member(guild_id=gid, name="甲", main_profession="铁衣", status="active")
                session.add(member)
                await session.flush()
                mid = member.id
                schedule = Schedule(guild_id=gid, opponent="对手",
                                    match_time=datetime.now(UTC), rounds=1)
                session.add(schedule)
                await session.flush()
                sid = schedule.id
                session.add_all([
                    AttendanceRecord(schedule_id=sid, member_id=mid, member_name="甲",
                                     profession="铁衣", status="normal"),
                    Recording(schedule_id=sid, member_id=mid, member_name="甲", round_number=1,
                              status="pending"),
                ])
                await session.commit()

                await member_service.delete_member(session, gid, mid)

                left_att = (await session.execute(
                    select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.schedule_id == sid)
                )).scalar()
                left_rec = (await session.execute(
                    select(func.count()).select_from(Recording).where(Recording.schedule_id == sid)
                )).scalar()
                self.assertEqual(left_att, 1, "出勤历史行应保留（姓名快照）")
                self.assertEqual(left_rec, 1, "录屏历史行应保留")
                dangling_att = (await session.execute(
                    select(func.count()).select_from(AttendanceRecord).where(AttendanceRecord.member_id == mid)
                )).scalar()
                dangling_rec = (await session.execute(
                    select(func.count()).select_from(Recording).where(Recording.member_id == mid)
                )).scalar()
                self.assertEqual(dangling_att, 0, "出勤行的 member_id 应已置空（防主键复用误关联）")
                self.assertEqual(dangling_rec, 0, "录屏行的 member_id 应已置空")
            await engine.dispose()

        asyncio.run(scenario())


if __name__ == "__main__":
    unittest.main()

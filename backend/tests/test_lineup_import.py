"""排表「导入历史排表」语义的回归测试（F-81）。

锁定实现既有语义（并在 database-design §2.7 补记为显式规则）：
- 不能从当前赛程导入自身；
- 来源赛程必须属于本帮会（否则按不存在处理）；
- 来源没有排表数据 -> 404 业务错误；
- 只保留当前候选池（出勤正常）中出现的成员：正式按 member_id、补人按姓名；
- 不在候选池的成员 -> 槽位留空（member_id=None、member_name=""）；
- 成员改名后，用**出勤库当前姓名**替换历史排表里的旧名快照。
"""
from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.schedule import Schedule
from app.services import lineup_service
from app.services.lineup_service import LineupServiceError, empty_lineup_data


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="排表导入测试")
        self.session.add(guild)
        await self.session.flush()
        self.gid = guild.id
        self.src = Schedule(guild_id=self.gid, opponent="来源", match_time=datetime.now(UTC), rounds=1)
        self.dst = Schedule(guild_id=self.gid, opponent="目标", match_time=datetime.now(UTC), rounds=1)
        self.session.add_all([self.src, self.dst])
        await self.session.flush()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _attend(self, schedule_id: int, name: str, member_id: int | None) -> None:
        self.session.add(AttendanceRecord(schedule_id=schedule_id, member_id=member_id, member_name=name,
                                          profession="铁衣", status="normal", is_filler=member_id is None))
        await self.session.commit()

    async def _source_lineup(self, slots: list[dict]) -> None:
        data = empty_lineup_data()
        # 仅填第一队前若干槽位，便于断言
        for i, s in enumerate(slots):
            data[0]["slots"][i] = {**data[0]["slots"][i], **s}
        self.session.add(Lineup(schedule_id=self.src.id, data=data, title_remark="", groups_remark={}))
        await self.session.commit()

    @staticmethod
    def _key(team: dict) -> str:
        return f"{team['category']}:{team['team_index']}"

    async def _import(self, keys=None):
        default_keys = [self._key(empty_lineup_data()[0])]
        return await lineup_service.import_lineup(self.session, self.gid, self.dst.id, self.src.id,
                                                 keys or default_keys)


class LineupImportTest(_Base):
    async def test_cannot_import_from_self(self) -> None:
        with self.assertRaises(LineupServiceError):
            await lineup_service.import_lineup(self.session, self.gid, self.dst.id, self.dst.id,
                                                 [self._key(empty_lineup_data()[0])])

    async def test_source_without_lineup_is_404(self) -> None:
        with self.assertRaises(LineupServiceError) as ctx:
            await self._import()
        self.assertEqual(ctx.exception.status_code, 404)

    async def test_only_pool_members_are_kept(self) -> None:
        await self._attend(self.dst.id, "在池甲", 11)
        # 补人（member_id=None）也可作为候选池成员按姓名保留
        await self._attend(self.dst.id, "补人乙", None)
        await self._source_lineup([
            {"member_id": 11, "member_name": "在池甲"},
            {"member_id": 99, "member_name": "不在池"},
            {"member_id": None, "member_name": "补人乙"},
        ])
        lineup, imported = await self._import()
        slots = lineup.data[0]["slots"]
        self.assertEqual(imported, 2, "只有候选池中的两条应被导入")
        self.assertEqual(slots[0]["member_id"], 11)
        self.assertEqual(slots[1]["member_name"], "", "不在候选池的成员应留空")
        self.assertIsNone(slots[1]["member_id"])
        self.assertEqual(slots[2]["member_name"], "补人乙", "补人按姓名保留")

    async def test_rename_uses_current_attendance_name(self) -> None:
        await self._attend(self.dst.id, "新名字", 21)
        await self._source_lineup([{"member_id": 21, "member_name": "旧名字"}])
        lineup, imported = await self._import()
        self.assertEqual(imported, 1)
        self.assertEqual(lineup.data[0]["slots"][0]["member_name"], "新名字",
                         "导入时应以出勤库当前姓名为准（替换历史快照）")

    async def test_unselected_teams_are_untouched(self) -> None:
        await self._attend(self.dst.id, "在池甲", 31)
        await self._source_lineup([{"member_id": 31, "member_name": "在池甲"}])
        existing = empty_lineup_data()
        existing[1]["slots"][0] = {**existing[1]["slots"][0], "member_id": None, "member_name": "目标队自有"}
        self.session.add(Lineup(schedule_id=self.dst.id, data=existing, title_remark="", groups_remark={}))
        await self.session.commit()
        lineup, _ = await self._import([self._key(empty_lineup_data()[0])])
        self.assertEqual(lineup.data[1]["slots"][0]["member_name"], "目标队自有",
                         "未选中的小队应保持原样")


if __name__ == "__main__":
    unittest.main()

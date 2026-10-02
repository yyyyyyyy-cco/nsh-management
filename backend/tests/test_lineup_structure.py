"""排表结构校验的回归测试（F-85）。

`_validate_structure` 此前**没有任何测试**；本轮补上，并锁定新增规则：
- 结构必须为固定布局：进攻1×3、进攻2×3、防守1×2、防守2×2 = 10 队，每队 6 槽，槽位序号 0..5；
- **同一成员不得占用多个槽位**（正式按 `member_id`、补人按姓名分别去重）；
- 反向：正式成员与补人**同名**是合法的（与出勤库补人唯一性口径一致），不得被误拒。
"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.schedule import Schedule
from app.services import lineup_service
from app.services.lineup_service import LineupServiceError, empty_lineup_data
from app.utils.constants import LINEUP_LAYOUT, SLOTS_PER_TEAM


def _valid() -> list[dict]:
    return empty_lineup_data()


class StructureValidationTest(unittest.TestCase):
    def test_empty_lineup_matches_documented_layout(self) -> None:
        data = _valid()
        self.assertEqual(len(data), sum(c for _, c in LINEUP_LAYOUT))
        self.assertEqual(
            [(t["category"], t["team_index"]) for t in data],
            [(cat, idx) for cat, count in LINEUP_LAYOUT for idx in range(count)],
        )
        for team in data:
            self.assertEqual(len(team["slots"]), SLOTS_PER_TEAM)
            self.assertEqual([s["slot_index"] for s in team["slots"]], list(range(SLOTS_PER_TEAM)))
        lineup_service._validate_structure(data)  # 不抛错

    def test_team_count_must_be_ten(self) -> None:
        for bad in (_valid()[:-1], _valid() + [_valid()[0]]):
            with self.assertRaises(LineupServiceError):
                lineup_service._validate_structure(bad)

    def test_category_order_is_fixed(self) -> None:
        data = _valid()
        data[0], data[1] = data[1], data[0]
        with self.assertRaises(LineupServiceError):
            lineup_service._validate_structure(data)

    def test_slots_per_team_is_six(self) -> None:
        data = _valid()
        data[0]["slots"] = data[0]["slots"][:-1]
        with self.assertRaises(LineupServiceError):
            lineup_service._validate_structure(data)

    def test_slot_index_must_be_sequential(self) -> None:
        data = _valid()
        data[0]["slots"][0]["slot_index"] = 3
        with self.assertRaises(LineupServiceError):
            lineup_service._validate_structure(data)

    def test_duplicate_member_id_rejected(self) -> None:
        """F-85：同一正式成员出现在两个槽位应被拒绝。"""
        data = _valid()
        data[0]["slots"][0].update({"member_id": 7, "member_name": "甲"})
        data[1]["slots"][0].update({"member_id": 7, "member_name": "甲"})
        with self.assertRaises(LineupServiceError):
            lineup_service._validate_structure(data)

    def test_duplicate_filler_name_rejected(self) -> None:
        """F-85：同一补人（按姓名）出现在两个槽位应被拒绝（含首尾空白归一）。"""
        data = _valid()
        data[0]["slots"][0].update({"member_id": None, "member_name": "补人乙"})
        data[2]["slots"][3].update({"member_id": None, "member_name": " 补人乙 "})
        with self.assertRaises(LineupServiceError):
            lineup_service._validate_structure(data)

    def test_regular_and_filler_with_same_name_allowed(self) -> None:
        """反向用例：正式成员与补人同名合法（按 id / 按姓名分维度去重）。"""
        data = _valid()
        data[0]["slots"][0].update({"member_id": 9, "member_name": "同名"})
        data[1]["slots"][0].update({"member_id": None, "member_name": "同名"})
        lineup_service._validate_structure(data)  # 不抛错


class StructureValidationThroughSaveTest(unittest.IsolatedAsyncioTestCase):
    """确认校验确实接在保存路径上（而不只是一个孤立函数）。"""

    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        self.session.add(Guild(id=1, name="排表结构测试"))
        self.session.add(Schedule(id=1, guild_id=1, opponent="对手", rounds=1, match_time=datetime.now(UTC)))
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def test_save_rejects_duplicate_filler(self) -> None:
        data = _valid()
        data[0]["slots"][0].update({"member_id": None, "member_name": "重复补人"})
        data[5]["slots"][2].update({"member_id": None, "member_name": "重复补人"})
        with self.assertRaises(LineupServiceError):
            await lineup_service.save_lineup(self.session, 1, 1, data)
        await self.session.rollback()

    async def test_save_accepts_valid_structure(self) -> None:
        data = _valid()
        data[0]["slots"][0].update({"member_id": None, "member_name": "补人丙"})
        lineup = await lineup_service.save_lineup(self.session, 1, 1, data)
        self.assertEqual(lineup.data[0]["slots"][0]["member_name"], "补人丙")
        stored = (await self.session.execute(select(Lineup).where(Lineup.schedule_id == 1))).scalars().first()
        self.assertIsNotNone(stored, "首次保存应插入记录")


if __name__ == "__main__":
    unittest.main()

"""补人唯一性（部分唯一索引）的回归测试。F-79。

文档（database-design §2.6/§2.8）要求：
- attendance_records：补人按 `(schedule_id, member_name, is_filler=1)` 每场一条；
- recordings：补人按 `(schedule_id, member_name, round_number)` 每局一条。
历史上仅由应用层查重，数据库无约束；本测试锁定数据库级约束（部分唯一索引）。
"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.recording import Recording
from app.models.schedule import Schedule


class FillerUniquenessTest(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="补人唯一性测试")
        self.session.add(guild)
        await self.session.flush()
        schedule = Schedule(guild_id=guild.id, opponent="对手", match_time=datetime.now(UTC), rounds=1)
        self.session.add(schedule)
        await self.session.flush()
        self.sid = schedule.id
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    def _filler(self, name: str) -> AttendanceRecord:
        return AttendanceRecord(
            schedule_id=self.sid, member_id=None, member_name=name, profession="铁衣", status="normal", is_filler=True
        )

    async def test_duplicate_filler_name_rejected(self) -> None:
        self.session.add(self._filler("补人甲"))
        await self.session.commit()
        self.session.add(self._filler("补人甲"))
        with self.assertRaises(IntegrityError):
            await self.session.commit()
        await self.session.rollback()

    async def test_same_name_as_regular_member_allowed(self) -> None:
        """正选（有 member_id）与补人（member_id NULL）同名互不冲突——两条约束维度不同。"""
        self.session.add(
            AttendanceRecord(
                schedule_id=self.sid,
                member_id=1,
                member_name="同名",
                profession="铁衣",
                status="normal",
                is_filler=False,
            )
        )
        self.session.add(self._filler("同名"))
        await self.session.commit()  # 不应抛错

    async def test_duplicate_filler_recording_rejected(self) -> None:
        self.session.add(
            Recording(schedule_id=self.sid, member_id=None, member_name="补人乙", round_number=1, status="pending")
        )
        await self.session.commit()
        self.session.add(
            Recording(schedule_id=self.sid, member_id=None, member_name="补人乙", round_number=1, status="pending")
        )
        with self.assertRaises(IntegrityError):
            await self.session.commit()
        await self.session.rollback()

    async def test_filler_recording_other_round_allowed(self) -> None:
        self.session.add(
            Recording(schedule_id=self.sid, member_id=None, member_name="补人丙", round_number=1, status="pending")
        )
        self.session.add(
            Recording(schedule_id=self.sid, member_id=None, member_name="补人丙", round_number=2, status="pending")
        )
        await self.session.commit()  # 不同局应允许


if __name__ == "__main__":
    unittest.main()

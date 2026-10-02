"""录屏审核状态机的回归测试（F-80）。

锁定实现既有语义（并在 database-design §2.8 补记为显式规则）：
- 未提交链接（url 为空）时不允许通过或驳回（业务错误）；
- 提交链接后可通过 / 可驳回，并记录 remark 与 reviewed_at；
- 帮众重新提交链接会把状态**重置为 pending** 并清空 remark/reviewed_at（覆盖既有审核结论）；
- 跨赛程的 recording_id 视为不存在（404 语义）。
"""
from __future__ import annotations

import unittest
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.guild import Guild
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.services import recording_service
from app.services.recording_service import RecordingServiceError


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="录屏状态测试")
        self.session.add(guild)
        await self.session.flush()
        self.gid = guild.id
        self.s1 = Schedule(guild_id=self.gid, opponent="对手甲",
                           match_time=datetime.now(UTC), rounds=1)
        self.s2 = Schedule(guild_id=self.gid, opponent="对手乙",
                           match_time=datetime.now(UTC), rounds=1)
        self.session.add_all([self.s1, self.s2])
        await self.session.flush()
        self.rid = None

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _make_recording(self, url: str | None = None) -> Recording:
        rec = Recording(schedule_id=self.s1.id, member_name="甲", round_number=1,
                        status="pending", url=url)
        self.session.add(rec)
        await self.session.commit()
        self.rid = rec.id
        return rec


class RecordingReviewStateTest(_Base):
    async def test_approve_without_url_is_business_error(self) -> None:
        await self._make_recording()
        with self.assertRaises(RecordingServiceError):
            await recording_service.approve_recording(self.session, self.gid, self.s1.id, self.rid)
        await self.session.rollback()

    async def test_reject_without_url_is_business_error(self) -> None:
        await self._make_recording()
        with self.assertRaises(RecordingServiceError):
            await recording_service.reject_recording(self.session, self.gid, self.s1.id, self.rid, "没交")
        await self.session.rollback()

    async def test_approve_then_resubmit_resets_to_pending(self) -> None:
        await self._make_recording(url="https://www.bilibili.com/video/BV1xx")
        approved = await recording_service.approve_recording(
            self.session, self.gid, self.s1.id, self.rid, "通过")
        self.assertEqual(approved.status, "approved")
        self.assertIsNotNone(approved.reviewed_at)
        # 帮众重新提交：状态回到 pending，审核痕迹被清空
        resubmitted = await recording_service.submit_recording(
            self.session, self.gid, self.s1.id, self.rid, "https://youtu.be/abcdefg")
        self.assertEqual(resubmitted.status, "pending", "重新提交应回到待审核")
        self.assertIsNone(resubmitted.review_remark, "重新提交应清空审核备注")
        self.assertIsNone(resubmitted.reviewed_at, "重新提交应清空审核时间")

    async def test_rejected_can_be_approved_after_resubmit(self) -> None:
        await self._make_recording(url="https://youtu.be/abcdefg")
        await recording_service.reject_recording(self.session, self.gid, self.s1.id, self.rid, "画质差")
        await recording_service.submit_recording(self.session, self.gid, self.s1.id, self.rid, "https://youtu.be/hijklmn")
        again = await recording_service.approve_recording(self.session, self.gid, self.s1.id, self.rid, "补交合格")
        self.assertEqual(again.status, "approved")

    async def test_cross_schedule_recording_is_not_found(self) -> None:
        await self._make_recording(url="https://youtu.be/abcdefg")
        with self.assertRaises(RecordingServiceError):
            await recording_service.approve_recording(self.session, self.gid, self.s2.id, self.rid)
        await self.session.rollback()

    async def test_batch_approve_skips_unsubmitted(self) -> None:
        r1 = await self._make_recording(url="https://youtu.be/abcdefg")
        r2 = Recording(schedule_id=self.s1.id, member_name="乙", round_number=1, status="pending", url=None)
        self.session.add(r2)
        await self.session.commit()
        count = await recording_service.batch_approve(self.session, self.gid, self.s1.id, [r1.id, r2.id])
        self.assertEqual(count, 1, "批量通过应跳过未提交链接的行")


if __name__ == "__main__":
    unittest.main()

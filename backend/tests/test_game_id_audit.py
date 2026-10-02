"""游戏 ID 改名审核的语义回归测试。

锁定 `memory-bank/design-game-id-change.md:147` 与 `design-document-v2.md §4.7` 明确写下的规则：
- 通过时**同一事务**更新 `members.name` 并写入 approved 关联记录（两表一次 commit）；
- **重复审核 409**，且**不覆盖首位审核人**（条件更新原子占用申请）；
- 驳回不改动 `members.name`；
- 目标成员已删除时不允许通过（409）；
- 管理员直接在常驻库改名：同一事务失效待审申请并记录一条 approved 关联（操作人快照）。
"""
from __future__ import annotations

import unittest
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.game_id_request import MemberGameIdRequest
from app.models.guild import Guild
from app.models.member import Member
from app.models.schedule import Schedule  # noqa: F401  (触发元数据注册)
from app.models.user import User
from app.schemas.game_id_request import GameIdRequestAudit
from app.services import member_service
from app.services.game_id_request_service import GameIdRequestError, audit_request


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        guild = Guild(name="审核测试帮会")
        self.session.add(guild)
        await self.session.flush()
        self.guild_id = guild.id
        member = Member(guild_id=self.guild_id, name="旧名", main_profession="铁衣", status="active")
        self.session.add(member)
        await self.session.flush()
        self.member_id = member.id
        admin = User(guild_id=self.guild_id, username="admin1", password_hash="x", role="admin",
                     status="active")
        self.session.add(admin)
        await self.session.flush()
        self.admin = admin

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _add_request(self, old="旧名", new="新名", member_id=None) -> MemberGameIdRequest:
        req = MemberGameIdRequest(
            guild_id=self.guild_id,
            member_id=self.member_id if member_id is None else member_id,
            old_game_id=old,
            new_game_id=new,
            requester_username="member-shared",
            status="pending",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.session.add(req)
        await self.session.commit()
        return req

    async def _member_name(self) -> str:
        return (await self.session.execute(select(Member.name).where(Member.id == self.member_id))).scalar_one()


class GameIdAuditTest(_Base):
    async def test_approve_updates_member_and_records_reviewer(self) -> None:
        req = await self._add_request()
        await audit_request(self.session, self.guild_id, req.id, self.admin,
                            GameIdRequestAudit(action="approve", review_remark=None, identity_confirmed=True))
        self.assertEqual(await self._member_name(), "新名", "通过后应同步常驻库名称")
        row = (await self.session.execute(
            select(MemberGameIdRequest).where(MemberGameIdRequest.id == req.id))).scalar_one()
        self.assertEqual(row.status, "approved")
        self.assertEqual(row.reviewer_username, "admin1", "应记录审核人快照")

    async def test_second_review_is_409_and_does_not_overwrite_reviewer(self) -> None:
        req = await self._add_request()
        await audit_request(self.session, self.guild_id, req.id, self.admin,
                            GameIdRequestAudit(action="approve", review_remark=None, identity_confirmed=True))
        with self.assertRaises(GameIdRequestError) as ctx:
            await audit_request(self.session, self.guild_id, req.id, self.admin,
                                GameIdRequestAudit(action="reject", review_remark="重复审核"))
        self.assertEqual(ctx.exception.status_code, 409, "重复审核必须 409")
        row = (await self.session.execute(
            select(MemberGameIdRequest).where(MemberGameIdRequest.id == req.id))).scalar_one()
        self.assertEqual(row.status, "approved", "重复审核不得改写已处理结果")
        self.assertEqual(row.reviewer_username, "admin1", "不得覆盖首位审核人")

    async def test_reject_keeps_member_name(self) -> None:
        req = await self._add_request()
        await audit_request(self.session, self.guild_id, req.id, self.admin,
                            GameIdRequestAudit(action="reject", review_remark="身份不符"))
        self.assertEqual(await self._member_name(), "旧名", "驳回不得改动常驻库名称")
        row = (await self.session.execute(
            select(MemberGameIdRequest).where(MemberGameIdRequest.id == req.id))).scalar_one()
        self.assertEqual(row.status, "rejected")

    async def test_approve_after_member_deleted_is_409(self) -> None:
        """成员被删除（走正规路径，detach_member 会置空引用并使待审失效）后，该申请不得被通过。"""
        req = await self._add_request()
        await member_service.delete_member(self.session, self.guild_id, self.member_id)
        with self.assertRaises(GameIdRequestError) as ctx:
            await audit_request(self.session, self.guild_id, req.id, self.admin,
                                GameIdRequestAudit(action="approve", review_remark=None, identity_confirmed=True))
        self.assertEqual(ctx.exception.status_code, 409, "成员已删除时不允许通过")

    async def test_reject_without_reason_is_schema_error(self) -> None:
        """驳回必须填写原因（schema 级控制，见 GameIdRequestAudit）。"""
        with self.assertRaises(ValueError):
            GameIdRequestAudit(action="reject", review_remark="")


class AdminRenameTest(_Base):
    async def test_admin_rename_invalidates_pending_and_records_association(self) -> None:
        from app.schemas.member import MemberUpdate

        req = await self._add_request()
        await member_service.update_member(self.session, self.guild_id, self.member_id,
                                          MemberUpdate(name="管理员改名"), self.admin)
        # 待审申请应失效
        pending = (await self.session.execute(
            select(MemberGameIdRequest).where(MemberGameIdRequest.id == req.id))).scalar_one()
        self.assertEqual(pending.status, "invalidated", "管理员改名应失效该成员的待审申请")
        # 应新增一条 approved 关联（old → new，操作人快照）
        approved = (await self.session.execute(
            select(func.count()).select_from(MemberGameIdRequest)
            .where(MemberGameIdRequest.guild_id == self.guild_id,
                   MemberGameIdRequest.status == "approved",
                   MemberGameIdRequest.old_game_id == "旧名",
                   MemberGameIdRequest.new_game_id == "管理员改名")
        )).scalar()
        self.assertEqual(approved, 1, "应记录一条已确认的新旧 ID 关联")
        self.assertEqual(await self._member_name(), "管理员改名")


if __name__ == "__main__":
    unittest.main()

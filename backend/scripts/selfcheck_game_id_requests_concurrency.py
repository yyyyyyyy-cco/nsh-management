"""游戏 ID 改名申请并发回归：隔离的临时文件 SQLite + 独立连接，验证事务与唯一约束。

运行：backend/.venv/Scripts/python.exe backend/scripts/selfcheck_game_id_requests_concurrency.py
说明：不使用共享单连接内存库，避免"伪并发"；所有数据写入系统临时目录的独立库文件。
"""
import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.game_id_request import MemberGameIdRequest
from app.models.guild import Guild
from app.models.member import Member
from app.models.user import User
from app.schemas.game_id_request import GameIdRequestAudit, GameIdRequestCreate
from app.services import game_id_request_service
from app.services.game_id_request_service import GameIdRequestError
from app.services.member_service import update_member
from app.schemas.member import MemberUpdate


class ConcurrencyTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="nsh_gameid_check_")
        self.db_path = Path(self._tmp.name) / "check.db"
        # 独立文件库 + 每请求独立 Session（独立连接），WAL 由 database.py 事件设置，此处手动补齐
        self.engine = create_async_engine(f"sqlite+aiosqlite:///{self.db_path}", connect_args={"timeout": 30})
        self.factory = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with self.factory() as session:
            session.add_all([Guild(id=1, name="帮会甲"), Guild(id=2, name="帮会乙")])
            await session.flush()
            for uid, role, gid in [(1, "admin", 1), (2, "admin", 1), (3, "member", 1)]:
                session.add(User(id=uid, username=f"actor{uid}", role=role, guild_id=gid, password_hash="unused"))
            session.add_all(
                [
                    Member(id=1, guild_id=1, name="甲", main_profession="神相", status="formal"),
                    Member(id=2, guild_id=1, name="乙", main_profession="素问", status="formal"),
                ]
            )
            await session.commit()

    async def asyncTearDown(self):
        await self.engine.dispose()
        self._tmp.cleanup()

    async def _new_session(self):
        return self.factory()

    async def _submit(self, member_id: int, old: str, new: str):
        """独立连接提交申请；返回 (结果, 错误状态码)。"""
        async with await self._new_session() as session:
            user = await session.get(User, 3)
            body = GameIdRequestCreate(expected_old_game_id=old, new_game_id=new)
            try:
                record = await game_id_request_service.create_request(session, 1, member_id, user, body)
                return record.id, None
            except GameIdRequestError as exc:
                return None, exc.status_code

    async def _audit(self, request_id: int, action: str, reviewer_id: int = 1):
        async with await self._new_session() as session:
            reviewer = await session.get(User, reviewer_id)
            body = GameIdRequestAudit(action=action, identity_confirmed=True, review_remark=None if action == "approve" else "并发驳回")
            try:
                record = await game_id_request_service.audit_request(session, 1, request_id, reviewer, body)
                return record.status, None
            except GameIdRequestError as exc:
                return None, exc.status_code

    async def _pending_count(self) -> int:
        async with await self._new_session() as session:
            return await session.scalar(
                select(func.count())
                .select_from(MemberGameIdRequest)
                .where(MemberGameIdRequest.status == "pending")
            )

    async def _member_name(self, member_id: int = 1) -> str:
        async with await self._new_session() as session:
            return (await session.get(Member, member_id)).name

    async def _latest_request_id(self) -> int:
        async with await self._new_session() as session:
            return await session.scalar(select(func.max(MemberGameIdRequest.id)))

    # ---- 并发用例 ----

    async def test_concurrent_duplicate_submit(self):
        results = await asyncio.gather(self._submit(1, "甲", "甲改"), self._submit(1, "甲", "甲改"))
        created = [r[0] for r in results if r[0] is not None]
        errors = [r[1] for r in results if r[1] is not None]
        self.assertEqual(len(created), 1)
        self.assertTrue(all(code in (409, 503) for code in errors), errors)
        self.assertEqual(await self._pending_count(), 1)
        self.assertEqual(await self._member_name(), "甲")

    async def test_concurrent_approve_single_winner(self):
        rid, _ = await self._submit(1, "甲", "甲改")
        results = await asyncio.gather(self._audit(rid, "approve", 1), self._audit(rid, "approve", 2))
        winners = [r for r in results if r[0] == "approved"]
        losers = [r[1] for r in results if r[1] is not None]
        self.assertEqual(len(winners), 1)
        self.assertTrue(all(code in (409, 503) for code in losers), losers)
        self.assertEqual(await self._member_name(), "甲改")
        async with await self._new_session() as session:
            record = await session.get(MemberGameIdRequest, rid)
            self.assertEqual(record.status, "approved")
            self.assertIn(record.reviewer_username, ("actor1", "actor2"))

    async def test_concurrent_approve_and_reject(self):
        rid, _ = await self._submit(1, "甲", "甲改")
        results = await asyncio.gather(self._audit(rid, "approve", 1), self._audit(rid, "reject", 2))
        final = [r for r in results if r[0] is not None]
        self.assertEqual(len(final), 1)  # 只能有一个决定生效
        async with await self._new_session() as session:
            record = await session.get(MemberGameIdRequest, rid)
            name = await session.get(Member, 1)
            if record.status == "approved":
                self.assertEqual(name.name, "甲改")
            else:
                self.assertEqual((record.status, name.name), ("rejected", "甲"))

    async def test_concurrent_competition_same_new_id(self):
        rid1, _ = await self._submit(1, "甲", "同名")
        rid2, _ = await self._submit(2, "乙", "同名")
        results = await asyncio.gather(self._audit(rid1, "approve", 1), self._audit(rid2, "approve", 2))
        approved = [r for r in results if r[0] == "approved"]
        self.assertEqual(len(approved), 1)
        async with await self._new_session() as session:
            names = sorted((await session.execute(select(Member.name))).scalars().all())
        self.assertEqual(names.count("同名"), 1)
        self.assertEqual(len(names), 2)

    async def test_concurrent_direct_rename_and_approve(self):
        rid, _ = await self._submit(1, "甲", "甲改")

        async def direct_rename():
            async with await self._new_session() as session:
                try:
                    operator = await session.get(User, 1)
                    await update_member(session, 1, 1, MemberUpdate(name="甲直接改"), operator)
                    return "renamed"
                except Exception:  # noqa: BLE001 并发下允许写锁失败
                    return None

        results = await asyncio.gather(direct_rename(), self._audit(rid, "approve"))
        rename_result, audit_result = results[0], results[1]
        async with await self._new_session() as session:
            member = await session.get(Member, 1)
            record = await session.get(MemberGameIdRequest, rid)
            # 并发下最后写入者不定：名称可能是「甲」（两者都失败）、「甲改」（审核生效）或
            # 「甲直接改」（直接改名生效，含「审核通过 → 管理员再次直接改名」这一合法交错）
            self.assertIn(member.name, ("甲", "甲改", "甲直接改"))
            if record.status == "approved" and rename_result is None:
                # 直接改名未生效时审核是最后写入者，没有后续写入，名称必然等于申请的新 ID
                self.assertEqual(member.name, record.new_game_id)
            elif record.status == "approved":
                # 审核通过后又被直接改名：名称必为直接改名结果（审核之后无其他写入者）
                self.assertEqual(member.name, "甲直接改")
            if record.status == "invalidated":
                # 直接改名抢先失效待审申请：名称必为直接改名结果，审核不得改写
                self.assertEqual(member.name, "甲直接改")
            if rename_result == "renamed":
                # 直接改名必须留下一条已确认关联记录（个人战绩新旧 ID 合并依赖它）
                confirmed = (
                    await session.execute(
                        select(MemberGameIdRequest).where(
                            MemberGameIdRequest.member_id == 1,
                            MemberGameIdRequest.status == "approved",
                            MemberGameIdRequest.new_game_id == "甲直接改",
                        )
                    )
                ).scalars().all()
                self.assertTrue(confirmed)
        if rename_result is None and audit_result[0] is None:
            self.assertIn(audit_result[1], (409, 503))


if __name__ == "__main__":
    unittest.main(verbosity=2)

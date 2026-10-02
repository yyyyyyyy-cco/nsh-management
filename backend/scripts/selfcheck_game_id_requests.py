"""游戏 ID 改名申请回归：真实 JWT + ASGI 路由，仅用内存库，无第三方测试依赖。

运行：backend/.venv/Scripts/python.exe backend/scripts/selfcheck_game_id_requests.py
覆盖：角色矩阵 / 租户隔离 / 参数边界 / 重复待审 / 审核事务 / 失效联动 / 删除关联 / 响应脱敏。
"""
# 行数豁免（连续逻辑）：改名申请端到端回归：真实 JWT + ASGI 路由 + 内存库，认证夹具与库生命周期贯穿全过程｜登记见 .agent/rules/file-length-rule.md 豁免清单

# ---- 前置依赖探测（缺依赖时模块级跳过；见合规化计划 W2-2 与本文件被 pytest 收集的约定）----
import unittest as _unittest

try:  # noqa: SIM105
    import fastapi  # noqa: F401
    import sqlalchemy  # noqa: F401
except ImportError as _exc:  # pragma: no cover - 无依赖环境（如 Python 3.14 装不上 pydantic-core）
    raise _unittest.SkipTest(f"缺少运行依赖（FastAPI/SQLAlchemy），跳过本模块：{_exc}") from _exc

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1 import game_id_requests, members
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.game_id_request import MemberGameIdRequest
from app.models.guild import Guild
from app.models.member import Member
from app.models.user import User
from app.services.game_id_request_service import GameIdRequestError
from app.services.member_service import MemberServiceError


class GameIdRequestTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)()
        self.session.add_all([Guild(id=1, name="帮会甲"), Guild(id=2, name="帮会乙")])
        await self.session.flush()
        self.users = {}
        for uid, role, gid in [
            (1, "admin", 1),
            (2, "developer", None),
            (3, "member", 1),
            (4, "admin", 2),
            (5, "member", 2),
        ]:
            user = User(id=uid, username=f"actor{uid}", role=role, guild_id=gid, password_hash="unused")
            self.session.add(user)
            self.users[uid] = user
        self.session.add_all(
            [
                Member(id=1, guild_id=1, name="甲", main_profession="神相", status="formal"),
                Member(id=2, guild_id=1, name="乙", main_profession="素问", status="formal"),
                Member(id=3, guild_id=2, name="丙", main_profession="铁衣", status="formal"),
            ]
        )
        await self.session.commit()

        self.app = FastAPI()
        for router in (game_id_requests.router, members.router):
            self.app.include_router(router)

        async def session_override():
            yield self.session

        async def business_error(request, exc):
            return JSONResponse({"message": exc.message}, status_code=exc.status_code)

        self.app.dependency_overrides[get_db] = session_override
        for error in (GameIdRequestError, MemberServiceError):
            self.app.add_exception_handler(error, business_error)

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def request(self, method, path, body=None, actor=3):
        payload = json.dumps(body).encode() if body is not None else b""
        headers = [(b"content-type", b"application/json")]
        if actor is not None:
            user = self.users[actor]
            token = create_access_token(user.id, user.role, user.token_version)
            headers.append((b"authorization", f"Bearer {token}".encode()))
        pure_path, _, query = path.partition("?")
        scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": method,
            "scheme": "http",
            "path": pure_path,
            "raw_path": pure_path.encode(),
            "query_string": query.encode(),
            "root_path": "",
            "headers": headers,
            "server": ("test", 80),
            "client": ("127.0.0.1", 1),
        }
        events = []

        async def receive():
            return {"type": "http.request", "body": payload, "more_body": False}

        async def send(message):
            events.append(message)

        await self.app(scope, receive, send)
        status = next(e["status"] for e in events if e["type"] == "http.response.start")
        content = b"".join(e.get("body", b"") for e in events if e["type"] == "http.response.body")
        return status, json.loads(content) if content else {}

    def submit_body(self, old="甲", new="甲改"):
        return {"expected_old_game_id": old, "new_game_id": new}

    async def _pending_count(self, member_id=1):
        return await self.session.scalar(
            select(func.count())
            .select_from(MemberGameIdRequest)
            .where(MemberGameIdRequest.member_id == member_id, MemberGameIdRequest.status == "pending")
        )

    async def _member_name(self, member_id=1):
        return (await self.session.get(Member, member_id)).name

    # ---- 提交 ----

    async def test_member_submit_success_without_touching_members(self):
        status, data = await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        self.assertEqual(status, 201)
        self.assertEqual(data["status"], "pending")
        self.assertEqual(data["old_game_id"], "甲")
        self.assertNotIn("requester_username", data)  # 帮众响应脱敏
        self.assertEqual(await self._member_name(), "甲")
        self.assertEqual(await self._pending_count(), 1)

    async def test_short_and_long_ids(self):
        status, _ = await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="X"))
        self.assertEqual(status, 201)
        status, _ = await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="表" * 32))
        self.assertEqual(status, 409)  # 已有待审
        for bad in ["", " ", "行\n换", "\t", "表" * 33]:
            status, _ = await self.request("POST", "/members/2/game-id-requests", self.submit_body(old="乙", new=bad))
            self.assertEqual(status, 422, bad)

    async def test_submit_rejections(self):
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(old="旧")))[0], 409
        )
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="甲")))[0], 422
        )
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="乙")))[0], 409
        )
        self.assertEqual((await self.request("POST", "/members/3/game-id-requests", self.submit_body()))[0], 404)
        body = {**self.submit_body(), "guild_id": 2}
        self.assertEqual((await self.request("POST", "/members/1/game-id-requests", body))[0], 422)
        body = {**self.submit_body(), "status": "approved"}
        self.assertEqual((await self.request("POST", "/members/1/game-id-requests", body))[0], 422)

    async def test_role_matrix(self):
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(), actor=1))[0], 403
        )
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(), actor=2))[0], 403
        )
        self.assertEqual(
            (await self.request("POST", "/members/1/game-id-requests", self.submit_body(), actor=None))[0], 401
        )
        self.assertEqual((await self.request("GET", "/members/game-id-options", actor=1))[0], 403)
        self.assertEqual((await self.request("GET", "/members/game-id-options", actor=2))[0], 403)
        status, data = await self.request("GET", "/members/game-id-options")
        self.assertEqual((status, data["total"]), (200, 2))
        self.assertNotIn("remark", data["items"][0])
        self.assertEqual((await self.request("GET", "/members/game-id-requests", actor=3))[0], 403)
        status, data = await self.request("GET", "/members/game-id-requests", actor=1)
        self.assertEqual((status, data["total"]), (200, 0))

    async def test_duplicate_pending_and_shared_account_scope(self):
        self.assertEqual((await self.request("POST", "/members/1/game-id-requests", self.submit_body()))[0], 201)
        self.assertEqual((await self.request("POST", "/members/1/game-id-requests", self.submit_body()))[0], 409)
        # 共享账号可为不同成员分别提交
        self.assertEqual(
            (await self.request("POST", "/members/2/game-id-requests", self.submit_body(old="乙", new="乙改")))[0], 201
        )

    # ---- 审核 ----

    async def test_audit_approve_and_replay(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        rid = (await self.session.scalar(select(MemberGameIdRequest.id))).__int__()
        status, _ = await self.request("PUT", f"/members/game-id-requests/{rid}/audit", {"action": "approve"}, actor=1)
        self.assertEqual(status, 422)  # 未确认身份
        status, data = await self.request(
            "PUT",
            f"/members/game-id-requests/{rid}/audit",
            {"action": "approve", "identity_confirmed": True, "review_remark": " 已核实 "},
            actor=1,
        )
        self.assertEqual(status, 200)
        self.assertEqual(data["status"], "approved")
        self.assertEqual(data["reviewer_username"], "actor1")
        self.assertEqual(data["current_game_id"], "甲改")
        self.assertEqual(await self._member_name(), "甲改")
        # 重放：不能覆盖首位审核人
        status, _ = await self.request(
            "PUT",
            f"/members/game-id-requests/{rid}/audit",
            {"action": "reject", "review_remark": "改主意"},
            actor=4,
        )
        self.assertEqual(status, 404)  # 跨帮会不可见
        status, _ = await self.request(
            "PUT",
            f"/members/game-id-requests/{rid}/audit",
            {"action": "approve", "identity_confirmed": True},
            actor=1,
        )
        self.assertEqual(status, 409)
        record = await self.session.get(MemberGameIdRequest, rid)
        await self.session.refresh(record)
        self.assertEqual((record.reviewer_username, record.status), ("actor1", "approved"))

    async def test_audit_reject_then_resubmit(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        rid = await self.session.scalar(select(MemberGameIdRequest.id))
        self.assertEqual(
            (await self.request("PUT", f"/members/game-id-requests/{rid}/audit", {"action": "reject"}, actor=1))[0], 422
        )
        status, data = await self.request(
            "PUT",
            f"/members/game-id-requests/{rid}/audit",
            {"action": "reject", "review_remark": "请核实原 ID"},
            actor=1,
        )
        self.assertEqual((status, data["status"]), (200, "rejected"))
        self.assertEqual(await self._member_name(), "甲")
        self.assertEqual((await self.request("POST", "/members/1/game-id-requests", self.submit_body()))[0], 201)

    async def test_audit_conflicts(self):
        # 名称占用：另一个成员先占用了目标名
        await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="乙改"))
        rid = await self.session.scalar(select(MemberGameIdRequest.id))
        await self.request("PUT", "/members/2", {"name": "乙改"}, actor=1)
        status, data = await self.request(
            "PUT",
            f"/members/game-id-requests/{rid}/audit",
            {"action": "approve", "identity_confirmed": True},
            actor=1,
        )
        self.assertEqual(status, 409)
        self.assertIn("已存在", data["message"])
        record = await self.session.get(MemberGameIdRequest, rid)
        await self.session.refresh(record)
        self.assertEqual(record.status, "pending")  # 事务回滚
        self.assertEqual(await self._member_name(), "甲")

    async def test_two_members_compete_same_new_id(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body(new="同名"))
        await self.request("POST", "/members/2/game-id-requests", self.submit_body(old="乙", new="同名"))

        async def rid_of(member_id: int) -> int:
            return await self.session.scalar(
                select(MemberGameIdRequest.id).where(MemberGameIdRequest.member_id == member_id)
            )

        first, second = await rid_of(1), await rid_of(2)
        self.assertEqual(
            (
                await self.request(
                    "PUT",
                    f"/members/game-id-requests/{first}/audit",
                    {"action": "approve", "identity_confirmed": True},
                    actor=1,
                )
            )[0],
            200,
        )
        status, _ = await self.request(
            "PUT",
            f"/members/game-id-requests/{second}/audit",
            {"action": "approve", "identity_confirmed": True},
            actor=1,
        )
        self.assertEqual(status, 409)

    async def test_direct_rename_invalidates_pending(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        rid = await self.session.scalar(select(MemberGameIdRequest.id))
        # 只改职业不触发失效
        await self.request("PUT", "/members/1", {"main_profession": "素问"}, actor=1)
        record = await self.session.get(MemberGameIdRequest, rid)
        await self.session.refresh(record)
        self.assertEqual(record.status, "pending")
        # 直接改名 → pending 失效
        await self.request("PUT", "/members/1", {"name": "甲新"}, actor=1)
        await self.session.refresh(record)
        self.assertEqual((record.status, record.invalidated_reason), ("invalidated", "member_renamed"))
        # 直接改名自动记录一条 approved 关联（操作管理员为提交/审核人，备注标注来源）
        auto = (
            await self.session.execute(
                select(MemberGameIdRequest).where(
                    MemberGameIdRequest.member_id == 1,
                    MemberGameIdRequest.status == "approved",
                )
            )
        ).scalar_one()
        self.assertEqual((auto.old_game_id, auto.new_game_id), ("甲", "甲新"))
        self.assertEqual((auto.requester_username, auto.reviewer_username), ("actor1", "actor1"))
        self.assertIsNotNone(auto.reviewed_at)
        self.assertIn("自动记录", auto.review_remark or "")
        self.assertEqual(
            (
                await self.request(
                    "PUT",
                    f"/members/game-id-requests/{rid}/audit",
                    {"action": "approve", "identity_confirmed": True},
                    actor=1,
                )
            )[0],
            409,
        )
        self.assertEqual(await self._member_name(), "甲新")

    async def test_member_delete_detaches_and_invalidates(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        rid = await self.session.scalar(select(MemberGameIdRequest.id))
        await self.request("DELETE", "/members/1", actor=1)
        record = await self.session.get(MemberGameIdRequest, rid)
        await self.session.refresh(record)
        self.assertEqual(
            (record.status, record.invalidated_reason, record.member_id), ("invalidated", "member_deleted", None)
        )
        self.assertEqual(
            (
                await self.request(
                    "PUT",
                    f"/members/game-id-requests/{rid}/audit",
                    {"action": "approve", "identity_confirmed": True},
                    actor=1,
                )
            )[0],
            409,
        )

    async def test_history_visibility_and_admin_list(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        status, data = await self.request("GET", "/members/1/game-id-requests", actor=3)
        self.assertEqual((status, len(data["items"])), (200, 1))
        self.assertNotIn("requester_username", data["items"][0])
        self.assertEqual(data["member"]["name"], "甲")
        status, data = await self.request("GET", "/members/1/game-id-requests", actor=1)
        self.assertEqual(data["items"][0]["requester_username"], "actor3")
        self.assertEqual(data["items"][0]["current_game_id"], "甲")
        self.assertEqual((await self.request("GET", "/members/3/game-id-requests", actor=3))[0], 404)
        status, data = await self.request("GET", "/members/game-id-requests?status=all", actor=1)
        self.assertEqual((status, data["total"]), (200, 1))
        self.assertEqual((await self.request("GET", "/members/game-id-requests?status=bogus", actor=1))[0], 422)

    async def test_account_delete_keeps_snapshot(self):
        await self.request("POST", "/members/1/game-id-requests", self.submit_body())
        rid = await self.session.scalar(select(MemberGameIdRequest.id))
        from app.services.account_service import delete_account

        await delete_account(self.session, 1, self.users[3].id)
        record = await self.session.get(MemberGameIdRequest, rid)
        await self.session.refresh(record)
        self.assertEqual((record.requester_id, record.requester_username, record.status), (None, "actor3", "pending"))
        # 快照仍可在管理员列表展示
        status, data = await self.request("GET", "/members/game-id-requests", actor=1)
        self.assertEqual((status, data["items"][0]["requester_username"]), (200, "actor3"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

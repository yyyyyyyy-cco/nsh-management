"""F-1/F-3/F-5 路由回归：真实 JWT 与依赖链，仅用内存库，无第三方测试依赖。
运行：backend/.venv/Scripts/python.exe backend/scripts/selfcheck_security_fixes.py
"""
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

from app.api.v1 import accounts, attendance, members, recording
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.guild import Guild
from app.models.member import Member
from app.models.user import User
from app.services.config_service import ConfigServiceError
from app.services.member_service import MemberServiceError


class SecurityFixTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)()
        self.session.add_all([Guild(id=1, name="测试帮会甲"), Guild(id=2, name="测试帮会乙")])
        await self.session.flush()
        self.users = {}
        for uid, role, gid in [(1, "admin", 1), (2, "developer", None), (3, "member", 1), (4, "admin", None)]:
            user = User(id=uid, username=f"actor{uid}", role=role, guild_id=gid, password_hash="unused")
            self.session.add(user)
            self.users[uid] = user
        await self.session.commit()
        self.app = FastAPI()
        for router in (accounts.router, members.router, attendance.router, recording.router):
            self.app.include_router(router)

        async def session_override():
            yield self.session

        async def business_error(request, exc):
            return JSONResponse({"message": exc.message}, status_code=exc.status_code)

        self.app.dependency_overrides[get_db] = session_override
        for error in (ConfigServiceError, MemberServiceError):
            self.app.add_exception_handler(error, business_error)

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    async def request(self, method, path, body=None, actor=1):
        """直接调用隔离 ASGI 应用；不会访问已启动的服务或生产数据库。"""
        payload = json.dumps(body).encode() if body is not None else b""
        headers = [(b"content-type", b"application/json")]
        if actor is not None:
            user = self.users[actor]
            token = create_access_token(user.id, user.role, user.token_version)
            headers.append((b"authorization", f"Bearer {token}".encode()))
        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                 "method": method, "scheme": "http", "path": path, "raw_path": path.encode(),
                 "query_string": b"", "root_path": "", "headers": headers,
                 "server": ("test", 80), "client": ("127.0.0.1", 1)}
        events = []

        async def receive():
            return {"type": "http.request", "body": payload, "more_body": False}

        async def send(message):
            events.append(message)

        await self.app(scope, receive, send)
        status = next(e["status"] for e in events if e["type"] == "http.response.start")
        content = b"".join(e.get("body", b"") for e in events if e["type"] == "http.response.body")
        return status, json.loads(content)

    def account_body(self, **kwargs):
        return {"username": "new_account", "password": "TestOnly123", "role": "admin", **kwargs}

    async def test_admin_cannot_create_in_other_guild(self):
        before = await self.session.scalar(select(func.count()).select_from(User))
        status, _ = await self.request("POST", "/config/accounts", self.account_body(guild_id=2))
        self.assertEqual(status, 403)
        self.assertEqual(await self.session.scalar(select(func.count()).select_from(User)), before)

    async def test_admin_omitted_or_own_guild_allowed(self):
        for gid in ("omitted", None, 1):
            body = self.account_body(username=f"own_{gid}")
            if gid != "omitted":
                body["guild_id"] = gid
            status, data = await self.request("POST", "/config/accounts", body)
            self.assertEqual(status, 200)
            self.assertEqual(data["guild_id"], 1)

    async def test_developer_target_guild_and_invalid_target(self):
        status, data = await self.request("POST", "/config/accounts", self.account_body(guild_id=2), 2)
        self.assertEqual((status, data["guild_id"]), (200, 2))
        for gid, expected in ((None, 400), (999, 404), (0, 422), (-1, 422)):
            status, _ = await self.request("POST", "/config/accounts", self.account_body(guild_id=gid), 2)
            self.assertEqual(status, expected)

    async def test_member_and_anonymous_cannot_create_accounts(self):
        for actor, expected in ((3, 403), (None, 401), (4, 403)):
            status, _ = await self.request("POST", "/config/accounts", self.account_body(), actor)
            self.assertEqual(status, expected)

    async def test_unbound_developer_cannot_create_member(self):
        status, _ = await self.request("POST", "/members", {"name": "测试成员", "main_profession": "铁衣"}, 2)
        self.assertEqual(status, 403)
        self.assertEqual(await self.session.scalar(select(func.count()).select_from(Member)), 0)

    async def test_batch_boundaries_rejected_before_business(self):
        cases = [
            ("POST", "/members/batch-delete", "ids", {}),
            ("POST", "/schedules/999/attendance/batch-status", "ids", {"status": "normal"}),
            ("POST", "/schedules/999/attendance/import-members", "member_ids", {}),
            ("POST", "/schedules/999/attendance/import-substitutes", "member_ids", {}),
            ("POST", "/schedules/999/recordings/batch-approve", "ids", {}),
        ]
        for method, path, field, extra in cases:
            for ids in ([], list(range(1, 502)), [0], [-1], [True], ["1"], [1.5]):
                with self.subTest(path=path, count=len(ids)):
                    status, _ = await self.request(method, path, {field: ids, **extra})
                    self.assertEqual(status, 422)

    async def test_batch_500_accepted_and_cross_guild_member_preserved(self):
        self.session.add_all([
            Member(id=1, guild_id=1, name="甲", main_profession="铁衣"),
            Member(id=2, guild_id=2, name="乙", main_profession="素问"),
        ])
        await self.session.commit()
        status, _ = await self.request("POST", "/members/batch-delete", {"ids": list(range(1, 501))})
        self.assertEqual(status, 200)
        remaining = list((await self.session.scalars(select(Member))).all())
        self.assertEqual([(r.id, r.guild_id) for r in remaining], [(2, 2)])

    def test_all_batch_models_accept_single_and_maximum(self):
        from app.schemas.attendance import BatchStatusUpdate, ImportSubstitutesRequest
        from app.schemas.member import BatchDeleteRequest
        from app.schemas.recording import BatchApproveRequest

        for model, field, extra in [(BatchDeleteRequest, "ids", {}), (BatchApproveRequest, "ids", {}),
                                    (BatchStatusUpdate, "ids", {"status": "normal"}),
                                    (ImportSubstitutesRequest, "member_ids", {})]:
            for size in (1, 500):
                self.assertEqual(len(getattr(model(**{field: list(range(1, size + 1)), **extra}), field)), size)


if __name__ == "__main__":
    unittest.main(verbosity=2)

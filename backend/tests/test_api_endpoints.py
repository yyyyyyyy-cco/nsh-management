# -*- coding: utf-8 -*-
"""接口级（端到端）用例 —— W2-2 收尾的最后一块缺口（原记录「组件级/接口级用例未写」）。

与既有用例的分工：
- `tests/support.py` 的服务层用例直接调函数；
- 本模块经 **TestClient 打完整链路**：CORS 中间件 → 审计中间件 → 依赖注入（JWT 解析 + 查库）→ 路由 →
  序列化 → 异常处理器。因此能覆盖单测覆盖不到的东西（真实状态码、响应体、CORS 响应头）。

错误响应体契约：本项目统一为 `{code, message, data}`（`main.py:error_response`），不是 FastAPI 默认的 `{detail}`。

覆盖：登录成功/失败、**登录失败锁定（含锁定后正确密码仍被拒）**、未知账号锁定、
受保护接口缺/坏令牌、**令牌版本吊销**、角色越权 403、CORS 预检、`/health`。

**DB 隔离（关键）**：内存库 + 覆盖 `get_db` 依赖；并把「自带 session 工厂」的三处模块
（`log_service`、`app.main` 的审计中间件、`api.v1.health`）也指向同一个工厂——
否则登录埋点与审计会写进**真实数据库文件**。

依赖缺失时模块级跳过（见 ai-checklist 第 32 条）。
"""
from __future__ import annotations

import asyncio
import unittest
from unittest import mock

try:
    import sqlalchemy  # noqa: F401
    from fastapi.testclient import TestClient
    from sqlalchemy import select
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    import app.main as main_module
    from app.api.v1 import health as health_module
    from app.core.config import settings
    from app.core.database import Base, get_db
    from app.core.security import create_access_token, hash_password
    from app.main import app
    from app.models.guild import Guild
    from app.models.user import User
    from app.services import auth_service, log_service
except ImportError as exc:  # pragma: no cover — 无依赖环境
    import unittest as _unittest

    raise _unittest.SkipTest(f"缺少运行依赖（FastAPI/SQLAlchemy/httpx2），跳过本模块：{exc}") from exc

PASSWORD = "pw-for-tests-123"
LOGIN = f"{settings.API_PREFIX}/auth/login"
ME = f"{settings.API_PREFIX}/auth/me"
MEMBERS = f"{settings.API_PREFIX}/members"
DEVELOPER_LOGS = f"{settings.API_PREFIX}/developer/logs"


class ApiEndpointTestCase(unittest.TestCase):
    """类级共享一个内存库；每个用例独立客户端与依赖覆盖。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        cls.factory = async_sessionmaker(cls.engine, expire_on_commit=False)
        asyncio.run(cls._prepare_db())

    @classmethod
    def tearDownClass(cls) -> None:
        asyncio.run(cls.engine.dispose())

    @classmethod
    async def _prepare_db(cls) -> None:
        async with cls.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with cls.factory() as session:
            session.add(Guild(id=1, name="测试帮会"))
            session.add_all(
                [
                    User(id=1, username="a_admin", role="admin", guild_id=1,
                         password_hash=hash_password(PASSWORD), status="active", token_version=0),
                    User(id=2, username="a_member", role="member", guild_id=1,
                         password_hash=hash_password(PASSWORD), status="active", token_version=0),
                    User(id=3, username="a_dev", role="developer", guild_id=None,
                         password_hash=hash_password(PASSWORD), status="active", token_version=0),
                    User(id=4, username="a_lockee", role="admin", guild_id=1,
                         password_hash=hash_password(PASSWORD), status="active", token_version=0),
                ]
            )
            await session.commit()

    def setUp(self) -> None:
        auth_service._unknown_login_failures.clear()
        # 用例必须与执行顺序无关：类级共享内存库，而锁定状态（failed_attempts / locked_until）是
        # **持久化在库里的**——不清零时，先跑的锁定用例会把后跑的用例一并锁死（本轮实测：字母序更早的
        # test_locked_account_… 把 test_login_wrong_password_… 的“还可尝试 N 次”断言打成了“已锁定”）。
        asyncio.run(self._reset_lock_state())

        async def _override_get_db():
            async with self.factory() as session:
                yield session

        app.dependency_overrides[get_db] = _override_get_db
        self._patches = [
            mock.patch.object(log_service, "async_session_factory", self.factory),
            mock.patch.object(main_module, "async_session_factory", self.factory),
            mock.patch.object(health_module, "async_session_factory", self.factory),
        ]
        for patch in self._patches:
            patch.start()
        # 刻意不用 `with TestClient(app)`：那会触发 lifespan（启动门禁 + 后台循环），
        # 启动门禁由 test_config_gate.py 单独覆盖，此处只测请求链路。
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.client.close()
        for patch in self._patches:
            patch.stop()
        app.dependency_overrides.clear()

    # ---------- 工具 ----------
    def _token(self, user_id: int, role: str, version: int = 0) -> str:
        return create_access_token(user_id, role, version)

    def _auth(self, token: str) -> dict:
        return {"Authorization": f"Bearer {token}"}

    def _login(self, username: str, password: str):
        return self.client.post(LOGIN, json={"username": username, "password": password})

    async def _bump_token_version(self, user_id: int) -> None:
        async with self.factory() as session:
            user = await session.get(User, user_id)
            user.token_version += 1
            await session.commit()

    async def _reset_lock_state(self) -> None:
        """清零种子账号的登录失败计数、锁定时间与令牌版本，保证用例与执行顺序无关。

        （令牌版本也会被吊销用例 +1，同样必须还原，否则后续用例拿 version=0 的令牌一律 401。）
        """
        async with self.factory() as session:
            for user in (await session.execute(select(User))).scalars():
                user.failed_attempts = 0
                user.locked_until = None
                user.token_version = 0
            await session.commit()

    # ---------- 登录 ----------
    def test_login_success_returns_token(self):
        resp = self._login("a_admin", PASSWORD)
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertTrue(body["access_token"])
        self.assertEqual(body["user"]["role"], "admin")
        self.assertEqual(body["user"]["guild_name"], "测试帮会")
        # 令牌可直接用于受保护接口（端到端串联）
        me = self.client.get(ME, headers=self._auth(body["access_token"]))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["username"], "a_admin")

    def test_login_wrong_password_reports_remaining_then_locks(self):
        for attempt in range(1, 5):
            resp = self._login("a_lockee", "wrong-password")
            self.assertEqual(resp.status_code, 401)
            body = resp.json()
            self.assertEqual(body["code"], 401)
            self.assertIn(f"还可尝试 {5 - attempt} 次", body["message"], f"第 {attempt} 次")

        locked = self._login("a_lockee", "wrong-password")
        self.assertEqual(locked.status_code, 401)
        locked_body = locked.json()
        self.assertIn("已锁定", locked_body["message"])
        # 锁定时 data 携带剩余秒数，供前端禁用表单并倒计时（main.py auth_error_handler）
        self.assertGreater(locked_body["data"]["remaining_seconds"], 0)

    def test_locked_account_rejects_even_correct_password(self):
        """锁定的核心价值：此后**正确密码也进不来**（否则锁定形同虚设）。"""
        for _ in range(5):
            self._login("a_lockee", "wrong-password")
        resp = self._login("a_lockee", PASSWORD)
        self.assertEqual(resp.status_code, 401)
        self.assertIn("已锁定", resp.json()["message"])

    def test_unknown_username_locks_after_max_failures(self):
        for _ in range(5):
            resp = self._login("no-such-user", "whatever")
            self.assertEqual(resp.status_code, 401)
        resp = self._login("no-such-user", "whatever")
        self.assertEqual(resp.status_code, 401)
        self.assertIn("已锁定", resp.json()["message"])

    # ---------- 令牌与权限 ----------
    def test_protected_endpoint_requires_token(self):
        self.assertEqual(self.client.get(ME).status_code, 401)
        self.assertEqual(self.client.get(ME, headers=self._auth("not-a-jwt")).status_code, 401)

    def test_token_version_bump_invalidates_old_token(self):
        token = self._token(1, "admin", version=0)
        self.assertEqual(self.client.get(ME, headers=self._auth(token)).status_code, 200)
        asyncio.run(self._bump_token_version(1))
        self.assertEqual(self.client.get(ME, headers=self._auth(token)).status_code, 401)

    def test_member_forbidden_on_admin_and_developer_endpoints(self):
        token = self._token(2, "member")
        for path in (MEMBERS, DEVELOPER_LOGS):
            with self.subTest(path=path):
                resp = self.client.get(path, headers=self._auth(token))
                self.assertEqual(resp.status_code, 403, f"{path} -> {resp.status_code}")

    def test_admin_allowed_on_admin_endpoint_but_not_developer_endpoint(self):
        token = self._token(1, "admin")
        self.assertEqual(self.client.get(MEMBERS, headers=self._auth(token)).status_code, 200)
        resp = self.client.get(DEVELOPER_LOGS, headers=self._auth(token))
        self.assertEqual(resp.status_code, 403)
        self.assertIn("仅开发者", resp.json()["message"])

    # ---------- CORS 与健康检查 ----------
    def test_cors_preflight_allows_dev_origin_and_rejects_unknown(self):
        allowed = self.client.options(
            LOGIN,
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(
            allowed.headers.get("access-control-allow-origin"), "http://localhost:5173"
        )
        denied = self.client.options(
            LOGIN,
            headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
        )
        self.assertIsNone(denied.headers.get("access-control-allow-origin"))

    def test_health_reports_ok_with_database(self):
        resp = self.client.get(f"{settings.API_PREFIX}/health")
        self.assertEqual(resp.status_code, 200, resp.text)
        body = resp.json()
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")
        self.assertEqual(body["app"], settings.APP_NAME)  # 探针同时回报应用名


if __name__ == "__main__":
    unittest.main(verbosity=2)
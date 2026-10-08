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

import pathlib
import tempfile
import unittest
from unittest import mock

try:
    import sqlalchemy  # noqa: F401
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
    from sqlalchemy.pool import NullPool

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
PASSWORD_CHANGE = f"{settings.API_PREFIX}/auth/password"
ME = f"{settings.API_PREFIX}/auth/me"
MEMBERS = f"{settings.API_PREFIX}/members"
DEVELOPER_LOGS = f"{settings.API_PREFIX}/developer/logs"


class ApiEndpointTestCase(unittest.TestCase):
    """类级共享一个**临时文件库**（不是内存库，原因见下），每个用例独立客户端与依赖覆盖。"""

    @classmethod
    def setUpClass(cls) -> None:
        # 为什么用文件库而不是 `:memory:`：TestClient 的请求可能在**新的事件循环**里执行，
        # 而 aiosqlite 的 `:memory:` 是 per-connection 的——新连接就是**空库**（本轮实测大面积
        # `no such table: users`）。文件库让任何连接都能看到同一份带表的数据。
        tmp_root = pathlib.Path(__file__).resolve().parents[2] / ".git" / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        cls._tmp = tempfile.TemporaryDirectory(dir=tmp_root, ignore_cleanup_errors=True)
        cls.db_file = pathlib.Path(cls._tmp.name) / "api-endpoints.db"

        engine = create_engine(f"sqlite:///{cls.db_file}")  # 同步引擎：建表与播种不需要事件循环
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(Guild.__table__.insert().values(id=1, name="测试帮会"))
            for uid, username, role, guild_id in (
                (1, "a_admin", "admin", 1),
                (2, "a_member", "member", 1),
                (3, "a_dev", "developer", None),
                (4, "a_lockee", "admin", 1),
                (5, "a_self", "member", 1),
                (6, "a_weak", "member", 1),  # 弱口令用例专用：其口令不被其它用例修改
            ):
                conn.execute(
                    User.__table__.insert().values(
                        id=uid,
                        username=username,
                        role=role,
                        guild_id=guild_id,
                        password_hash=hash_password(PASSWORD),
                        status="active",
                        token_version=0,
                    )
                )
        engine.dispose()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._tmp.cleanup()

    def setUp(self) -> None:
        # 用例隔离靠**专用账号**，不靠「清库状态」（见类文档：跨事件循环的库访问不可靠）。
        auth_service._unknown_login_failures.clear()

        def fresh_factory():
            """每次调用新建引擎**并返回 session**（跨事件循环安全；NullPool 用完即关）。"""
            return async_sessionmaker(
                create_async_engine(f"sqlite+aiosqlite:///{self.db_file}", poolclass=NullPool),
                expire_on_commit=False,
            )()

        async def _override_get_db():
            async with fresh_factory() as session:
                yield session

        app.dependency_overrides[get_db] = _override_get_db
        self._patches = [
            mock.patch.object(log_service, "async_session_factory", fresh_factory),
            mock.patch.object(main_module, "async_session_factory", fresh_factory),
            mock.patch.object(health_module, "async_session_factory", fresh_factory),
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
        """锁定的核心价值：此后**正确密码也进不来**（否则锁定形同虚设）。

        用 a_member（本用例专用账号）而非与上一个锁定用例共用 a_lockee——共享账号会按字母序互相污染。
        """
        for _ in range(5):
            self._login("a_member", "wrong-password")
        resp = self._login("a_member", PASSWORD)
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
        """管理员重置口令会 `token_version += 1` → 该账号**旧令牌立即失效**（ASVS 7.4.3）。

        用专用账号 a_dev（developer）以避免与其他用例共享账号；版本提升**经接口**完成，
        不在同步上下文里直连异步库。
        """
        token = self._token(3, "developer", version=0)
        self.assertEqual(self.client.get(ME, headers=self._auth(token)).status_code, 200)

        reset = self.client.put(
            f"{settings.API_PREFIX}/config/accounts/3",
            json={"password": "reset-Passw0rd-2026"},
            headers=self._auth(token),
        )
        self.assertEqual(reset.status_code, 200, reset.text)
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

    # ---------- 口令策略与自助改密（W4-10 / ASVS 6.2.2、6.2.3、6.2.5、6.2.11） ----------
    def test_self_service_password_change_invalidates_old_token(self):
        """自助改密：须提供当前口令；成功后旧令牌立即失效，新口令可登录。"""
        token = self._token(5, "member")
        new_password = "fresh-Passw0rd-2026"
        resp = self.client.post(
            PASSWORD_CHANGE,
            json={"current_password": PASSWORD, "new_password": new_password},
            headers=self._auth(token),
        )
        self.assertEqual(resp.status_code, 200, resp.text)

        # 旧令牌失效：改密使 token_version +1（ASVS 7.4.3）
        self.assertEqual(self.client.get(ME, headers=self._auth(token)).status_code, 401)
        # 新口令可登录
        login = self._login("a_self", new_password)
        self.assertEqual(login.status_code, 200, login.text)

    def test_password_change_requires_correct_current_password(self):
        token = self._token(5, "member")
        resp = self.client.post(
            PASSWORD_CHANGE,
            json={"current_password": "not-the-password", "new_password": "fresh-Passw0rd-2026"},
            headers=self._auth(token),
        )
        self.assertEqual(resp.status_code, 401)
        self.assertIn("当前密码不正确", resp.json()["message"])

    def test_password_change_requires_authentication(self):
        resp = self.client.post(
            PASSWORD_CHANGE, json={"current_password": PASSWORD, "new_password": "fresh-Passw0rd-2026"}
        )
        self.assertEqual(resp.status_code, 401)

    def test_weak_new_password_is_rejected(self):
        # 用 a_weak（专用账号）：自助改密用例会改掉 a_self 的口令并提升其 token_version，
        # 共享账号会让本用例拿到 401（依赖先于 body 校验）而不是期望的 422。
        token = self._token(6, "member")
        for weak in ("short1", "password"):
            with self.subTest(weak=weak):
                resp = self.client.post(
                    PASSWORD_CHANGE,
                    json={"current_password": PASSWORD, "new_password": weak},
                    headers=self._auth(token),
                )
                self.assertEqual(resp.status_code, 422, resp.text)

    def test_admin_create_account_accepts_composition_free_password(self):
        """ASVS 6.2.5：纯字母口令必须被接受（本轮删除「必须含字母和数字」规则的端到端证据）。"""
        admin = self._token(1, "admin")
        ok = self.client.post(
            f"{settings.API_PREFIX}/config/accounts",
            json={"username": "newbie01", "password": "abcdefgh"},
            headers=self._auth(admin),
        )
        self.assertEqual(ok.status_code, 200, ok.text)

        weak = self.client.post(
            f"{settings.API_PREFIX}/config/accounts",
            json={"username": "newbie02", "password": "12345678"},
            headers=self._auth(admin),
        )
        self.assertEqual(weak.status_code, 422, weak.text)

    # ---------- CORS 与健康检查 ----------
    def test_cors_preflight_allows_dev_origin_and_rejects_unknown(self):
        allowed = self.client.options(
            LOGIN,
            headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(allowed.headers.get("access-control-allow-origin"), "http://localhost:5173")
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

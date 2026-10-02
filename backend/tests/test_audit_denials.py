# -*- coding: utf-8 -*-
"""审计留痕回归（W4-9 / F-50、F-51）。

覆盖：
1. **带凭证的读请求被拒（401/403）必须落审计**（ASVS 5.0.0 16.3.2）——原先只有写方法留痕，读接口越权无痕；
2. **匿名 401 不落审计**（避免探测刷日志，属未认证访问而非授权失败）；
3. **写请求的拒绝只落一条**（扩展后不得重复记录）；
4. **日志控制字符转义**（ASVS 16.4.1 / F-51）：提交含换行的用户名后，落库行内不得出现真实换行。

**为什么用「文件库 + stdlib sqlite3 断言」**：中间件是 `asyncio.create_task` 异步落库，而内存库的
aiosqlite 连接绑定创建它的事件循环——用 TestClient 的测试循环去读会报「attached to a different loop」。
改用**临时文件库**：应用经 aiosqlite 写，断言用标准库 sqlite3 直接读同一文件，互不依赖事件循环，且可轮询等待。
"""
from __future__ import annotations

import asyncio
import pathlib
import sqlite3
import tempfile
import time
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
    from app.core.security import create_access_token
    from app.main import app
    from app.models.guild import Guild
    from app.models.user import User
    from app.services import alert_service, log_service
except ImportError as exc:  # pragma: no cover
    import unittest as _unittest

    raise _unittest.SkipTest(f"缺少运行依赖（FastAPI/SQLAlchemy/httpx2），跳过本模块：{exc}") from exc

ME = f"{settings.API_PREFIX}/auth/me"
MEMBERS = f"{settings.API_PREFIX}/members"
LOGIN = f"{settings.API_PREFIX}/auth/login"


async def _loop_stub() -> None:
    """lifespan 后台循环的替身：测试里不发真实请求，退出时由 lifespan 取消。"""
    await asyncio.sleep(3600)


class AuditDenialTests(unittest.TestCase):
    def setUp(self) -> None:
        # 临时库放 `.git/tmp`：**不能**落在仓库工作树里——测试若清理失败会留下 `backend/tmpXXXX/`
        # （`*.db` 被 .gitignore 覆盖，`git status` 看不见，属易漏的脏残留）。
        tmp_root = pathlib.Path(__file__).resolve().parents[2] / ".git" / "tmp"
        tmp_root.mkdir(parents=True, exist_ok=True)
        self._tmp = tempfile.TemporaryDirectory(dir=tmp_root, ignore_cleanup_errors=True)
        self.db_file = pathlib.Path(self._tmp.name) / "audit.db"

        engine = create_engine(f"sqlite:///{self.db_file}")
        Base.metadata.create_all(engine)
        with engine.begin() as conn:
            conn.execute(Guild.__table__.insert().values(id=1, name="测试帮会"))
            conn.execute(
                User.__table__.insert().values(
                    id=1, username="a_admin", role="admin", guild_id=1,
                    password_hash="unused", status="active", token_version=0,
                )
            )
            conn.execute(
                User.__table__.insert().values(
                    id=2, username="a_member", role="member", guild_id=1,
                    password_hash="unused", status="active", token_version=0,
                )
            )
        engine.dispose()

        async_url = f"sqlite+aiosqlite:///{self.db_file}"

        def fresh_factory():
            """每次调用新建引擎**并返回 session**：调用方写法是 `async with async_session_factory() as s`，
            所以替身必须与 `async_sessionmaker` 的**调用结果**一致（返回 session），否则报
            `'async_sessionmaker' object does not support the asynchronous context manager protocol`。
            NullPool 保证连接用完即关，避免跨事件循环复用。"""
            engine = create_async_engine(async_url, poolclass=NullPool)
            return async_sessionmaker(engine, expire_on_commit=False)()

        async def _override_get_db():
            async with fresh_factory() as session:
                yield session

        app.dependency_overrides[get_db] = _override_get_db
        self._patches = [
            mock.patch.object(log_service, "async_session_factory", fresh_factory),
            mock.patch.object(main_module, "async_session_factory", fresh_factory),
            mock.patch.object(health_module, "async_session_factory", fresh_factory),
            mock.patch.object(alert_service, "async_session_factory", fresh_factory),
            # 屏蔽 lifespan 的两个后台循环（否则测试里会真跑清理/告警并报「清理过期日志失败」噪音）
            mock.patch.object(main_module, "_alert_loop", _loop_stub),
            mock.patch.object(main_module, "_log_cleanup_loop", _loop_stub),
        ]
        for patch in self._patches:
            patch.start()

    def tearDown(self) -> None:
        for patch in self._patches:
            patch.stop()
        app.dependency_overrides.clear()
        self._tmp.cleanup()

    # ---------- 工具 ----------
    def _rows(self) -> list[dict]:
        with sqlite3.connect(self.db_file) as conn:
            conn.row_factory = sqlite3.Row
            return [dict(r) for r in conn.execute("SELECT * FROM operation_logs ORDER BY id")]

    def _wait_rows(self, minimum: int, timeout: float = 3.0) -> list[dict]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            rows = self._rows()
            if len(rows) >= minimum:
                return rows
            time.sleep(0.05)
        return self._rows()

    def _token(self, user_id: int, role: str, version: int = 0) -> str:
        return create_access_token(user_id, role, version)

    # ---------- 用例 ----------
    def test_authenticated_read_401_is_audited(self):
        """失效令牌读 `me` → 401 且必须留痕（原先读方法一律不留痕）。"""
        stale = self._token(1, "admin", version=99)  # 版本不符 → 401
        with TestClient(app) as client:
            resp = client.get(ME, headers={"Authorization": f"Bearer {stale}"})
            self.assertEqual(resp.status_code, 401)
            rows = self._wait_rows(1)
        self.assertEqual(len(rows), 1, rows)
        self.assertEqual(rows[0]["status_code"], 401)
        self.assertEqual(rows[0]["level"], "warning")
        self.assertEqual(rows[0]["module"], "auth")
        self.assertIn("凭证无效", rows[0]["detail"])

    def test_read_403_is_audited(self):
        """帮众读管理员接口 → 403 且留痕。"""
        member = self._token(2, "member")
        with TestClient(app) as client:
            resp = client.get(MEMBERS, headers={"Authorization": f"Bearer {member}"})
            self.assertEqual(resp.status_code, 403)
            rows = self._wait_rows(1)
        self.assertEqual(len(rows), 1, rows)
        self.assertEqual(rows[0]["status_code"], 403)
        self.assertIn("授权被拒", rows[0]["detail"])
        self.assertEqual(rows[0]["username"], "a_member")

    def test_anonymous_read_401_is_not_audited(self):
        """未携带凭证的 401 不落审计（匿名探测不计为授权失败）。"""
        with TestClient(app) as client:
            resp = client.get(ME)
            self.assertEqual(resp.status_code, 401)
            time.sleep(0.4)  # 给后台任务留出可能落库的时间，再断言「确实没有」
            rows = self._rows()
        self.assertEqual(rows, [], rows)

    def test_write_denial_logged_exactly_once(self):
        """写请求被拒只落一条（扩展后不得因 denied 分支重复记录）。"""
        member = self._token(2, "member")
        with TestClient(app) as client:
            resp = client.post(MEMBERS, json={"name": "x"}, headers={"Authorization": f"Bearer {member}"})
            self.assertEqual(resp.status_code, 403, resp.text)
            rows = self._wait_rows(1)
            time.sleep(0.3)
            rows = self._rows()
        self.assertEqual(len(rows), 1, rows)
        self.assertEqual(rows[0]["status_code"], 403)

    def test_log_injection_via_username_is_escaped(self):
        """登录失败埋点会记录提交的用户名：含换行的用户名不得在库中产生真实换行（F-51）。"""
        with TestClient(app) as client:
            resp = client.post(LOGIN, json={"username": "evil\ninject", "password": "x"})
            self.assertEqual(resp.status_code, 401, resp.text)
            rows = self._wait_rows(1)
        self.assertEqual(len(rows), 1, rows)
        stored = rows[0]["username"] or ""
        self.assertNotIn("\n", stored)
        self.assertIn(r"\x0a", stored)

    def test_escape_control_helper(self):
        """转义函数本体：控制字符转可见转义、可打印字符（含中文）保持不变。"""
        self.assertEqual(log_service.escape_control("张三"), "张三")
        self.assertEqual(log_service.escape_control("a\nb"), r"a\x0ab")
        self.assertEqual(log_service.escape_control("a\tb\r"), r"a\x09b\x0d")
        self.assertEqual(len(log_service.escape_control("x" * 100, 10)), 10)
        self.assertEqual(log_service.sanitize_detail("l1\nl2"), r"l1\x0al2")


if __name__ == "__main__":
    unittest.main(verbosity=2)
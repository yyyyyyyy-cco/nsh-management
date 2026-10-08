"""健康检查探针与 API 文档暴露面回归（合规化计划 W3-1 / W4-1）。

权威源：`backend/app/api/v1/health.py`（探针语义）、`backend/app/main.py`（文档开关接线）、
`docker-compose.yml`（healthcheck 探针路径）、OWASP Top 10:2025 A02（安全配置错误）。

需运行依赖（FastAPI/SQLAlchemy/httpx2），缺失时用例自动跳过——本地受限环境（Python 3.14
装不上 `pydantic-core`）由 CI 的 Python 3.11 覆盖；跳过是显式的，不会伪装成通过。
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

try:  # 运行依赖探测
    import sqlalchemy  # noqa: F401
    from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

    from app.api.v1 import health as health_module
    from app.core.database import Base

    HAS_RUNTIME = True
except ImportError:  # pragma: no cover
    HAS_RUNTIME = False

BACKEND_ROOT = Path(__file__).resolve().parents[1]
# 与 test_config_gate 一致的强密钥（仅用于子进程启动，不参与业务）
STRONG_MIXED_KEY = "Kj7#mQ2!vX9@bN4$wZ8%tR6^yU1&pL5*"


@unittest.skipUnless(HAS_RUNTIME, "缺少运行依赖（FastAPI/SQLAlchemy），跳过健康检查用例")
class HealthEndpointTests(unittest.IsolatedAsyncioTestCase):
    """探针语义：库通 → 200；库不通 → 503 且状态为 degraded（而非 500 崩溃）。"""

    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def asyncTearDown(self) -> None:
        await self.engine.dispose()

    async def test_health_ok_when_database_reachable(self):
        with mock.patch.object(health_module, "async_session_factory", self.factory):
            resp = await health_module.health()
        self.assertEqual(resp.status_code, 200)
        body = json.loads(resp.body)
        self.assertEqual(body["status"], "ok")
        self.assertEqual(body["database"], "ok")
        self.assertTrue(body["app"])

    async def test_health_degraded_with_503_when_database_unavailable(self):
        class BrokenSession:
            async def __aenter__(self):
                raise RuntimeError("database down")

            async def __aexit__(self, *exc):  # noqa: ANN002
                return False

        with mock.patch.object(health_module, "async_session_factory", lambda: BrokenSession()):
            resp = await health_module.health()
        self.assertEqual(resp.status_code, 503)
        body = json.loads(resp.body)
        self.assertEqual(body["status"], "degraded")
        self.assertEqual(body["database"], "error")


@unittest.skipUnless(HAS_RUNTIME, "缺少运行依赖，跳过 API 文档暴露面用例")
class ApiDocsSurfaceTests(unittest.TestCase):
    """生产环境必须关闭 `/docs`、`/redoc`、`/openapi.json`；本地开发保留（W4-1）。

    用子进程断言：应用在 import 时按环境决定文档开关，同进程内改环境无法复现。
    """

    def _app_surface(self, app_env: str) -> dict[str, str]:
        env = {k: v for k, v in os.environ.items() if k not in {"APP_ENV", "SECRET_KEY"}}
        env.update({"APP_ENV": app_env, "SECRET_KEY": STRONG_MIXED_KEY, "PYTHONIOENCODING": "utf-8"})
        code = "import app.main as m;print(m.app.openapi_url, m.app.docs_url, m.app.redoc_url, sep='|')"
        proc = subprocess.run(
            [sys.executable, "-c", code],
            cwd=BACKEND_ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=300,
        )
        self.assertEqual(proc.returncode, 0, f"应用导入失败：{proc.stderr}")
        keys = ("openapi_url", "docs_url", "redoc_url")
        return dict(zip(keys, proc.stdout.strip().split("|")))

    def test_production_disables_all_api_docs(self):
        for app_env in ("production", "prod"):
            with self.subTest(app_env=app_env):
                surface = self._app_surface(app_env)
                self.assertEqual(surface["openapi_url"], "None")
                self.assertEqual(surface["docs_url"], "None")
                self.assertEqual(surface["redoc_url"], "None")

    def test_development_keeps_api_docs(self):
        surface = self._app_surface("development")
        self.assertEqual(surface["openapi_url"], "/openapi.json")
        self.assertEqual(surface["docs_url"], "/docs")
        self.assertEqual(surface["redoc_url"], "/redoc")


@unittest.skipUnless(HAS_RUNTIME, "缺少运行依赖，跳过健康检查路由用例")
class HealthRoutingTests(unittest.TestCase):
    """路由接线：`/health` 与 `/api/v1/health` 都必须可命中。

    背景：本轮首次实现时 `include_router(..., name=...)` 在 FastAPI 0.142 不存在该参数，
    导致应用**导入即失败**；只调用路由函数的用例发现不了这类接线错误，故补此走真实路由的用例。
    刻意不进入 lifespan（避免在测试进程内触发启动门禁）；数据库层用桩替换，路由是本用例的关注点。
    """

    class _OkSession:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):  # noqa: ANN002
            return False

        async def execute(self, *args, **kwargs):  # noqa: ANN002
            return None

    def test_health_reachable_on_both_paths(self):
        from fastapi.testclient import TestClient

        from app.main import app

        client = TestClient(app)
        with mock.patch.object(health_module, "async_session_factory", lambda: self._OkSession()):
            for path in ("/health", "/api/v1/health"):
                with self.subTest(path=path):
                    resp = client.get(path)
                    self.assertEqual(resp.status_code, 200, f"{path} 应可达")
                    self.assertEqual(resp.json()["status"], "ok")

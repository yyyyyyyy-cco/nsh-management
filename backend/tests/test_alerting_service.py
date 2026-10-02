# -*- coding: utf-8 -*-
"""告警服务层回归（合规化计划 W4-6 / F-44）：窗口统计 + 一次检查的编排。

需运行依赖（SQLAlchemy / aiosqlite），缺失时整体跳过——本地受限环境由 CI 的 Python 3.11 覆盖；
跳过是显式的（`skipUnless`），不会伪装成通过。策略层用例见 `test_alerting_policy.py`（无需依赖）。
"""
import unittest
from datetime import UTC, datetime, timedelta
from unittest import mock

try:
    import sqlalchemy  # noqa: F401
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from support import DbTestCase

    from app.core.config import settings
    from app.models.operation_log import OperationLog
    from app.services import alert_service

    HAS_RUNTIME = True
except ImportError as exc:  # pragma: no cover — 本地无依赖环境（如 Python 3.14 装不上 pydantic-core）
    HAS_RUNTIME = False
    # 关键：**在模块级跳过**。若把 `from support import DbTestCase` 留在 try 之外，
    # 无依赖环境会在收集阶段直接 ImportError 报错（pytest 退出码 2），而不是干净地跳过。
    import unittest

    raise unittest.SkipTest(f"缺少运行依赖（SQLAlchemy/aiosqlite），跳过本模块：{exc}") from exc


@unittest.skipUnless(HAS_RUNTIME, "缺少运行依赖（SQLAlchemy/aiosqlite），跳过告警服务用例")
class CountRecentErrorsTests(DbTestCase):
    """窗口与级别过滤：只统计窗口内 `level='error'` 的行。"""

    async def _add_log(self, level: str, minutes_ago: int) -> None:
        self.session.add(
            OperationLog(
                module="test",
                action="smoke",
                method="POST",
                path="/api/v1/test",
                level=level,
                created_at=datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=minutes_ago),
            )
        )
        await self.session.commit()

    async def test_counts_only_errors_inside_window(self):
        await self._add_log("error", 5)      # 窗口内
        await self._add_log("error", 29)     # 窗口内（< 30）
        await self._add_log("error", 31)     # 窗口外
        await self._add_log("warning", 5)    # 级别不符
        await self._add_log("info", 3)       # 级别不符
        self.assertEqual(await alert_service.count_recent_errors(self.session, 30), 2)

    async def test_empty_table_counts_zero(self):
        self.assertEqual(await alert_service.count_recent_errors(self.session, 30), 0)


@unittest.skipUnless(HAS_RUNTIME, "缺少运行依赖（SQLAlchemy/aiosqlite），跳过告警服务用例")
class RunAlertCheckTests(DbTestCase):
    """编排行为：未达阈值不通知、达阈值通知、去重、禁用阈值、异常不外抛。"""

    async def asyncSetUp(self) -> None:
        """必须在 `asyncSetUp` 里取 `self.engine`：`IsolatedAsyncioTestCase` 的同步 `setUp()` 早于
        `DbTestCase.asyncSetUp()` 执行，那时引擎尚未创建（本用例首次真正执行即因此报
        `AttributeError: 'RunAlertCheckTests' object has no attribute 'engine'`）。
        """
        await super().asyncSetUp()
        alert_service.reset_dedup_state()
        self.factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def _seed_errors(self, count: int, minutes_ago: int = 1) -> None:
        stamp = datetime.now(UTC).replace(tzinfo=None) - timedelta(minutes=minutes_ago)
        for _ in range(count):
            self.session.add(
                OperationLog(
                    module="test",
                    action="smoke",
                    method="POST",
                    path="/api/v1/test",
                    level="error",
                    created_at=stamp,
                )
            )
        await self.session.commit()

    async def test_not_triggered_below_threshold(self):
        await self._seed_errors(3)
        with mock.patch.object(alert_service, "async_session_factory", self.factory), mock.patch.object(
            settings, "ALERT_ERROR_THRESHOLD", 20
        ):
            decision = await alert_service.run_alert_check(webhook_url="")
        self.assertEqual(decision.count, 3)
        self.assertFalse(decision.triggered)

    async def test_triggered_without_webhook_logs_only(self):
        await self._seed_errors(25)
        with mock.patch.object(alert_service, "async_session_factory", self.factory), mock.patch.object(
            settings, "ALERT_ERROR_THRESHOLD", 20
        ), mock.patch.object(alert_service, "post_json") as post:
            decision = await alert_service.run_alert_check(webhook_url="")
        self.assertTrue(decision.triggered)
        self.assertEqual(decision.count, 25)
        post.assert_not_called()  # 未配置 webhook：仅写日志

    async def test_triggered_pushes_webhook_once_within_dedup_window(self):
        await self._seed_errors(25)
        with mock.patch.object(alert_service, "async_session_factory", self.factory), mock.patch.object(
            settings, "ALERT_ERROR_THRESHOLD", 20
        ), mock.patch.object(alert_service, "post_json", return_value=200) as post:
            first = await alert_service.run_alert_check(webhook_url="https://hook.example/x")
            second = await alert_service.run_alert_check(webhook_url="https://hook.example/x")
        self.assertTrue(first.triggered)
        self.assertTrue(second.triggered)  # 判定仍为「已达阈值」
        self.assertEqual(post.call_count, 1)  # 但去重窗口内不重复推送

    async def test_threshold_disabled_never_triggers(self):
        await self._seed_errors(50)
        with mock.patch.object(alert_service, "async_session_factory", self.factory), mock.patch.object(
            settings, "ALERT_ERROR_THRESHOLD", 0
        ):
            decision = await alert_service.run_alert_check(webhook_url="")
        self.assertFalse(decision.triggered)

    async def test_database_failure_does_not_raise(self):
        class BrokenSession:
            async def __aenter__(self):
                raise RuntimeError("db down")

            async def __aexit__(self, *exc):  # noqa: ANN002
                return False

        with mock.patch.object(alert_service, "async_session_factory", lambda: BrokenSession()):
            decision = await alert_service.run_alert_check(webhook_url="")
        self.assertFalse(decision.triggered)
        self.assertEqual(decision.count, -1)  # -1 表示「统计失败」，用于区分 0 条
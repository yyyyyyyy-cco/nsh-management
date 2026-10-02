# -*- coding: utf-8 -*-
"""告警策略层回归（合规化计划 W4-6 / F-44）。

策略层（`app.core.alerting`）只依赖标准库，故本文件**不需要数据库/Web 框架**即可运行——
本地受限环境（Python 3.14 装不上 `pydantic-core`）也能验证判定、负载契约与发送行为。
服务层（查库与编排）另见 `test_alerting_service.py`。
"""
import json
import unittest
from datetime import datetime, timezone
from unittest import mock

from app.core.alerting import PAYLOAD_FIELDS, AlertDecision, build_payload, decide_alert, post_json


class DecideAlertTests(unittest.TestCase):
    """阈值判定：达到即触发；阈值 <=0 视为禁用。"""

    def test_triggers_at_and_above_threshold(self):
        self.assertFalse(decide_alert(19, 20))
        self.assertTrue(decide_alert(20, 20))
        self.assertTrue(decide_alert(21, 20))

    def test_zero_count_never_triggers_for_positive_threshold(self):
        self.assertFalse(decide_alert(0, 20))

    def test_threshold_zero_or_negative_disables_alerts(self):
        for threshold in (0, -1):
            with self.subTest(threshold=threshold):
                self.assertFalse(decide_alert(999, threshold))


class BuildPayloadTests(unittest.TestCase):
    """负载契约：字段集合稳定、时间与计数可断言。"""

    def test_payload_field_contract(self):
        decision = AlertDecision(count=25, threshold=20, window_minutes=30, triggered=True)
        payload = build_payload(
            decision, app_name="测试应用", now=datetime(2026, 10, 2, 12, 0, tzinfo=timezone.utc)
        )
        self.assertEqual(set(payload), set(PAYLOAD_FIELDS))
        self.assertEqual(payload["app"], "测试应用")
        self.assertEqual(payload["level"], "error")
        self.assertEqual(payload["count"], 25)
        self.assertEqual(payload["threshold"], 20)
        self.assertEqual(payload["window_minutes"], 30)
        self.assertEqual(payload["detected_at"], "2026-10-02T12:00:00+00:00")
        self.assertIn("25 条", payload["message"])
        self.assertIn("20", payload["message"])

    def test_payload_is_json_serializable(self):
        payload = build_payload(AlertDecision(1, 1, 5, True), app_name="app")
        json.dumps(payload, ensure_ascii=False)


class PostJsonTests(unittest.TestCase):
    """发送行为：POST + JSON 头 + 返回状态码（用桩替换 urlopen，不产生真实网络请求）。"""

    class _FakeResponse:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, *exc):  # noqa: ANN002
            return False

    def test_posts_json_and_returns_status(self):
        captured: dict = {}

        def fake_urlopen(request, timeout=None):
            captured["url"] = request.full_url
            captured["method"] = request.get_method()
            captured["content_type"] = request.headers.get("Content-type") or request.headers.get("Content-Type")
            captured["body"] = json.loads(request.data.decode("utf-8"))
            captured["timeout"] = timeout
            return self._FakeResponse()

        with mock.patch("urllib.request.urlopen", fake_urlopen):
            status = post_json("https://hook.example/x", {"a": 1, "中文": "值"}, timeout=3.5)

        self.assertEqual(status, 204)
        self.assertEqual(captured["url"], "https://hook.example/x")
        self.assertEqual(captured["method"], "POST")
        self.assertEqual(captured["body"], {"a": 1, "中文": "值"})  # 中文不被转义为 \uXXXX
        self.assertEqual(captured["timeout"], 3.5)
        self.assertIn("application/json", str(captured["content_type"]))

    def test_network_error_propagates_to_caller(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("boom")):
            with self.assertRaises(OSError):
                post_json("https://hook.example/x", {"a": 1})
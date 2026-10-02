# -*- coding: utf-8 -*-
"""错误率告警的**纯策略层**（合规化计划 W4-6 / F-44）。

分层理由：判定与负载构造只依赖标准库，因此可脱离数据库与 Web 框架被直接测试
（`alert_service` 负责数据库统计与编排）。`post_json` 用标准库 `urllib.request`，
**不引入新依赖**。

背景：审计日志此前「只写不告警」——错误落库了但无人被通知，对应
OWASP Top 10:2025 A09（Security Logging **and Alerting** Failures）的后半段。
"""
from __future__ import annotations

import json
import urllib.request
from dataclasses import dataclass
from datetime import UTC, datetime

# 告警负载的字段集合（稳定契约，便于对接任意 webhook；改字段需同步测试）
PAYLOAD_FIELDS = (
    "app",
    "level",
    "message",
    "count",
    "threshold",
    "window_minutes",
    "detected_at",
)


@dataclass(frozen=True)
class AlertDecision:
    """一次检查的判定结果（纯数据，便于断言与传递）。"""

    count: int
    threshold: int
    window_minutes: int
    triggered: bool


def decide_alert(count: int, threshold: int) -> bool:
    """条数达到阈值即触发；`threshold <= 0` 视为**禁用告警**（不触发）。"""
    if threshold <= 0:
        return False
    return count >= threshold


def build_payload(decision: AlertDecision, *, app_name: str, now: datetime | None = None) -> dict:
    """构造 webhook 负载（纯函数）。`detected_at` 为 UTC ISO 8601。"""
    stamp = (now or datetime.now(UTC)).isoformat()
    return {
        "app": app_name,
        "level": "error",
        "message": (
            f"最近 {decision.window_minutes} 分钟内错误日志 {decision.count} 条，"
            f"已达到阈值 {decision.threshold}"
        ),
        "count": decision.count,
        "threshold": decision.threshold,
        "window_minutes": decision.window_minutes,
        "detected_at": stamp,
    }


def post_json(url: str, payload: dict, timeout: float = 5.0) -> int:
    """把负载 POST 到 webhook，返回 HTTP 状态码；网络/HTTP 错误由调用方处理。"""
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(  # noqa: S310 — URL 来自运维配置（ALERT_WEBHOOK_URL），非用户输入
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310
        return int(getattr(response, "status", 0) or 0)
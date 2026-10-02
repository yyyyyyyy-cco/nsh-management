# -*- coding: utf-8 -*-
"""错误率告警的服务层：数据库统计 + 一次检查的编排（合规化计划 W4-6 / F-44）。

策略（判定/负载/发送）在 `app.core.alerting`；本模块只负责「查库 → 判定 → 通知」。

设计要点：
- **未配置 `ALERT_WEBHOOK_URL` 时仅写 WARNING 日志**：不静默——运维在容器日志里能看到；
  这保证「告警通道」在最小配置下即生效，配置 webhook 后升级为推送。
- **去重**：同一进程内、一个告警窗口内不重复发送（`_last_alert_at`），避免每轮检查刷屏；
  进程重启后去重状态丢失（可接受：最坏多发一条，不丢告警）。
- **失败不外抛**：统计失败或推送失败只记录异常，绝不因告警影响主服务（与 `clear_old_logs` 同风格）。
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.alerting import AlertDecision, build_payload, decide_alert, post_json
from app.core.config import settings
from app.core.database import async_session_factory
from app.models.operation_log import OperationLog

logger = logging.getLogger(__name__)

# 上次成功告警时间（UTC aware）；仅进程内状态
_last_alert_at: datetime | None = None


async def count_recent_errors(session: AsyncSession, window_minutes: int) -> int:
    """统计最近 `window_minutes` 分钟内 `level="error"` 的审计日志条数。

    时间口径：数据库存 **UTC naive**（见 `app/schemas/common.py`），故窗口边界也按 UTC naive 计算。
    """
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=window_minutes)
    result = await session.execute(
        select(func.count()).where(
            OperationLog.created_at >= cutoff,
            OperationLog.level == "error",
        )
    )
    return int(result.scalar_one())


async def run_alert_check(*, webhook_url: str | None = None, now: datetime | None = None) -> AlertDecision:
    """执行一次告警检查并返回判定结果（异常不外抛）。

    `webhook_url=None` 时取配置值；显式传空字符串可强制「仅写日志」路径（便于测试与排查）。
    """
    global _last_alert_at
    window = settings.ALERT_WINDOW_MINUTES
    threshold = settings.ALERT_ERROR_THRESHOLD
    url = settings.ALERT_WEBHOOK_URL if webhook_url is None else webhook_url
    stamp = now or datetime.now(timezone.utc)

    try:
        async with async_session_factory() as session:
            count = await count_recent_errors(session, window)
    except Exception:  # noqa: BLE001 — 告警检查不得影响主服务
        logger.exception("告警检查：统计错误日志失败（本轮跳过）")
        return AlertDecision(count=-1, threshold=threshold, window_minutes=window, triggered=False)

    decision = AlertDecision(
        count=count,
        threshold=threshold,
        window_minutes=window,
        triggered=decide_alert(count, threshold),
    )
    if not decision.triggered:
        return decision

    if _last_alert_at is not None and (stamp - _last_alert_at) < timedelta(minutes=window):
        logger.info(
            "告警检查：已达阈值（%d/%d）但处于去重窗口内（上次告警 %s），本轮不重复发送",
            count,
            threshold,
            _last_alert_at.isoformat(),
        )
        return decision

    payload = build_payload(decision, app_name=settings.APP_NAME, now=stamp)
    if not url:
        logger.warning("【告警】%s（未配置 ALERT_WEBHOOK_URL，仅写日志）", payload["message"])
        _last_alert_at = stamp
        return decision

    try:
        status = await asyncio.to_thread(post_json, url, payload)
        logger.warning("【告警】%s（已推送 webhook，HTTP %s）", payload["message"], status)
    except Exception:  # noqa: BLE001 — 推送失败不影响主服务
        logger.exception("告警 webhook 推送失败（url=%s）", url)
    _last_alert_at = stamp
    return decision


def reset_dedup_state() -> None:
    """清空去重状态（仅测试使用）。"""
    global _last_alert_at
    _last_alert_at = None
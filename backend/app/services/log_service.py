"""日志服务：审计日志落库、查询、统计与清理。

落库使用独立 session 且吞掉自身异常，保证日志失败不影响主流程。
"""
import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import async_session_factory
from app.models.operation_log import OperationLog
from app.models.user import User

# detail 中禁止落库的敏感字段名（小写比对）
SENSITIVE_KEYS = {"password", "plain_password", "token", "access_token", "authorization"}

# 模块白名单（路径首段），不在名单内的归为 other
MODULES = {
    "members", "schedules", "attendance", "lineups", "recordings",
    "match-data", "config", "developer", "auth", "squad-adjustments", "my-stats",
}

# 统计口径时区：用户均为北京时间，"今日"/按天分组按 UTC+8 计算
STATS_TZ = timezone(timedelta(hours=8))


def sanitize_detail(detail: dict | str | None) -> str | None:
    """detail 脱敏后序列化为 JSON 文本。"""
    if detail is None:
        return None
    if isinstance(detail, str):
        return detail[:2000]
    def _clean(obj):
        if isinstance(obj, dict):
            return {
                k: ("***" if str(k).lower() in SENSITIVE_KEYS else _clean(v))
                for k, v in obj.items()
            }
        if isinstance(obj, list):
            return [_clean(i) for i in obj]
        return obj
    try:
        return json.dumps(_clean(detail), ensure_ascii=False)[:2000]
    except (TypeError, ValueError):
        return None


async def record_log(
    *,
    module: str,
    action: str,
    level: str = "info",
    user: User | None = None,
    username: str | None = None,
    method: str | None = None,
    path: str | None = None,
    status_code: int | None = None,
    detail: dict | str | None = None,
    ip: str | None = None,
) -> None:
    """写入一条审计日志（独立 session，绝不抛出异常影响主流程）。"""
    try:
        async with async_session_factory() as session:
            session.add(
                OperationLog(
                    user_id=user.id if user else None,
                    username=username if username is not None else (user.username if user else None),
                    role=user.role if user else None,
                    guild_id=user.guild_id if user else None,
                    module=module[:32],
                    action=action[:32],
                    level=level,
                    method=(method or "")[:8],
                    path=(path or "")[:255],
                    status_code=status_code,
                    detail=sanitize_detail(detail),
                    ip=ip,
                )
            )
            await session.commit()
    except Exception:  # noqa: BLE001 日志写库失败静默，避免影响业务
        import logging

        logging.getLogger(__name__).exception("审计日志写库失败")


def module_from_path(path: str) -> str:
    """从 API 路径提取模块名：/api/v1/members/1 -> members。"""
    prefix = "/api/v1/"
    rest = path[len(prefix):] if path.startswith(prefix) else path.lstrip("/")
    first = rest.split("/", 1)[0]
    return first if first in MODULES else "other"


def action_from_method(method: str, path: str) -> str:
    """按方法与路径推断动作。"""
    if "import" in path:
        return "import"
    return {"POST": "create", "PUT": "update", "PATCH": "update", "DELETE": "delete"}.get(method, "other")


def _naive_utc(dt: datetime | None) -> datetime | None:
    """SQLite 读回时间为 naive，查询边界统一转为 naive UTC 以保证比较一致。"""
    if dt is None:
        return None
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    return dt.replace(tzinfo=None)


async def query_logs(
    session: AsyncSession,
    *,
    username: str | None = None,
    guild_id: int | None = None,
    module: str | None = None,
    level: str | None = None,
    start_time: datetime | None = None,
    end_time: datetime | None = None,
    page: int = 1,
    page_size: int = 20,
) -> tuple[int, list[OperationLog]]:
    """分页查询审计日志，按时间倒序。"""
    stmt = select(OperationLog)
    if username:
        stmt = stmt.where(OperationLog.username.like(f"%{username}%"))
    if guild_id is not None:
        stmt = stmt.where(OperationLog.guild_id == guild_id)
    if module:
        stmt = stmt.where(OperationLog.module == module)
    if level:
        stmt = stmt.where(OperationLog.level == level)
    start, end = _naive_utc(start_time), _naive_utc(end_time)
    if start:
        stmt = stmt.where(OperationLog.created_at >= start)
    if end:
        stmt = stmt.where(OperationLog.created_at <= end)

    total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (
        await session.execute(
            stmt.order_by(OperationLog.created_at.desc(), OperationLog.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
    ).scalars().all()
    return total, list(items)


async def get_log_stats(session: AsyncSession) -> dict:
    """概览统计：今日请求数、今日错误数、近 7 天错误分布（口径 = 北京时间）。"""
    now_bj = datetime.now(STATS_TZ).replace(tzinfo=None)  # 北京墙上时间（naive）
    today_start_bj = now_bj.replace(hour=0, minute=0, second=0, microsecond=0)
    # DB 存 UTC naive：北京时间边界前移 8 小时再查询
    today_start = today_start_bj - timedelta(hours=8)

    today_requests = (
        await session.execute(select(func.count()).where(OperationLog.created_at >= today_start))
    ).scalar_one()
    today_errors = (
        await session.execute(
            select(func.count()).where(
                OperationLog.created_at >= today_start, OperationLog.level == "error"
            )
        )
    ).scalar_one()

    week_start = today_start - timedelta(days=6)
    rows = (
        await session.execute(
            select(OperationLog.created_at)
            .where(OperationLog.created_at >= week_start, OperationLog.level == "error")
        )
    ).scalars().all()
    weekly = {day: 0 for day in [(today_start_bj - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]}
    for created_at in rows:
        # UTC 存储值加 8 小时映射回北京日期
        day = (created_at + timedelta(hours=8)).strftime("%Y-%m-%d")
        if day in weekly:
            weekly[day] += 1

    return {
        "today_requests": today_requests,
        "today_errors": today_errors,
        "weekly_errors": [{"date": d, "count": c} for d, c in weekly.items()],
    }


async def clear_old_logs(days: int | None = None) -> int:
    """清理超过保留期的日志，返回删除条数（独立 session）。"""
    days = days or settings.LOG_RETENTION_DAYS
    cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days)
    try:
        async with async_session_factory() as session:
            result = await session.execute(delete(OperationLog).where(OperationLog.created_at < cutoff))
            await session.commit()
            return result.rowcount or 0
    except Exception:  # noqa: BLE001
        import logging

        logging.getLogger(__name__).exception("清理过期日志失败")
        return 0

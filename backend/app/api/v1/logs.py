"""开发者日志接口：查询、统计、清理审计日志。"""

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_developer
from app.core.config import settings
from app.core.database import get_db
from app.models.user import User
from app.schemas.log import LogClearRequest, LogListOut, LogStatsOut, OperationLogOut
from app.services import log_service

router = APIRouter(prefix="/developer/logs", tags=["开发者"])


@router.get("", response_model=LogListOut)
async def list_logs(
    username: str | None = Query(None, description="账号名（模糊匹配）"),
    guild_id: int | None = Query(None),
    module: str | None = Query(None),
    level: str | None = Query(None, description="info / warning / error"),
    start_time: datetime | None = Query(None),
    end_time: datetime | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> LogListOut:
    """分页查询审计日志（仅开发者）。"""
    total, items = await log_service.query_logs(
        session,
        username=username,
        guild_id=guild_id,
        module=module,
        level=level,
        start_time=start_time,
        end_time=end_time,
        page=page,
        page_size=page_size,
    )
    return LogListOut(total=total, items=[OperationLogOut.model_validate(i) for i in items])


@router.get("/stats", response_model=LogStatsOut)
async def log_stats(
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> LogStatsOut:
    """日志概览统计（仅开发者）。"""
    return LogStatsOut(**await log_service.get_log_stats(session))


@router.delete("")
async def clear_logs(
    body: LogClearRequest,
    current_user: User = Depends(require_developer),
) -> dict:
    """清理保留期外的审计日志（仅开发者）。中间件豁免此路径，此处手动埋点带清理详情。"""
    deleted = await log_service.clear_old_logs(body.days)
    await log_service.record_log(
        module="developer",
        action="delete",
        level="info",
        user=current_user,
        method="DELETE",
        path=f"{settings.API_PREFIX}/developer/logs",
        status_code=200,
        detail=f"清理 {body.days} 天前日志，删除 {deleted} 条",
    )
    return {"message": f"已清理 {deleted} 条日志", "deleted": deleted}

"""健康检查（合规化计划 W3-1）。

探针语义（容器编排与负载均衡按状态码判定）：
- 进程可用且**数据库可查询** → `200 {"status":"ok","database":"ok"}`
- 数据库不可用 → `503 {"status":"degraded","database":"error"}`

设计取舍：数据库异常在探针内吞掉并转成 503，而不是抛异常——抛异常会返回 500，
对外表现为「应用崩溃」而非「依赖不可用」，不利于排查；同时 `SELECT 1` 只验证连通性，
不触碰业务表，避免探针在迁移未执行时把服务判死。
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core.config import settings
from app.core.database import async_session_factory

router = APIRouter(tags=["健康检查"])


@router.get("/health", summary="健康检查（含数据库连通性）")
async def health() -> JSONResponse:
    """返回 200 表示可服务；数据库不可查询时返回 503。"""
    database_ok = True
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:  # noqa: BLE001 — 探针需吞掉数据库层的任何异常并降级为 503
        database_ok = False

    return JSONResponse(
        status_code=200 if database_ok else 503,
        content={
            "status": "ok" if database_ok else "degraded",
            "database": "ok" if database_ok else "error",
            "app": settings.APP_NAME,
        },
    )

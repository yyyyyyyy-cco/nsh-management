"""常驻库接口：成员 CRUD、搜索筛选、批量删除、Excel 导入/导出、出勤率统计。"""
# 行数豁免（连续逻辑）：单资源薄路由（CRUD + 导入导出端点声明同质）｜登记见 .agent/rules/file-length-rule.md 豁免清单
import asyncio
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.guild import Guild
from app.models.user import User
from app.schemas.member import (
    AttendanceRateItem,
    BatchDeleteRequest,
    MemberCreate,
    MemberOut,
    MemberPage,
    MemberStats,
    MemberUpdate,
    ProfessionStat,
)
from app.services import member_service
from app.utils.excel_export import build_members_xlsx, member_export_filename
from app.utils.excel_import import MAX_FILE_SIZE, ExcelImportError, import_members
from app.utils.image_export import MAX_IMAGE_MEMBERS, draw_members_png

router = APIRouter(prefix="/members", tags=["常驻库"])


@router.get("", response_model=MemberPage)
async def list_members(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None, max_length=32),
    profession: str | None = Query(None, max_length=16),
    status: str | None = Query(None, max_length=16),
    sort_by: str | None = Query(None, description="排序字段：name/main_profession/status/created_at"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> MemberPage:
    items, total, stats = await member_service.list_members(
        session, current_user.guild_id, page, page_size, keyword, profession, status, sort_by, sort_order
    )
    return MemberPage(
        items=[MemberOut.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
        stats=MemberStats(**stats),
    )


@router.post("", response_model=MemberOut)
async def create_member(
    body: MemberCreate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> MemberOut:
    member = await member_service.create_member(session, current_user.guild_id, body)
    return MemberOut.model_validate(member)


@router.put("/{member_id}", response_model=MemberOut)
async def update_member(
    member_id: int,
    body: MemberUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> MemberOut:
    member = await member_service.update_member(session, current_user.guild_id, member_id, body, current_user)
    return MemberOut.model_validate(member)


@router.delete("/{member_id}")
async def delete_member(
    member_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await member_service.delete_member(session, current_user.guild_id, member_id)
    return {"message": "删除成功"}


@router.post("/batch-delete")
async def batch_delete(
    body: BatchDeleteRequest,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    count = await member_service.batch_delete(session, current_user.guild_id, body.ids)
    return {"message": f"已删除 {count} 名成员"}


@router.post("/import")
async def import_excel(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    # 文件类型校验：仅支持 .xlsx（openpyxl 可解析格式）
    if not (file.filename or "").lower().endswith(".xlsx"):
        raise ExcelImportError("仅支持 .xlsx 格式的 Excel 文件")
    # 文件大小校验：声明长度检查 + 读取后二次兕底（Content-Length 可能缺失或伪造）
    if file.size and file.size > MAX_FILE_SIZE:
        raise ExcelImportError("文件大小超过 5MB 限制")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ExcelImportError("文件大小超过 5MB 限制")
    result = await import_members(session, current_user.guild_id, content)
    return {"message": f"导入成功 {result['imported']} 条，跳过 {result['skipped']} 条", **result}


@router.get("/export")
async def export_members(
    keyword: str | None = Query(None, max_length=32),
    profession: str | None = Query(None, max_length=16),
    status: str | None = Query(None, max_length=16),
    sort_by: str | None = Query(None, description="排序字段：name/main_profession/status/created_at"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """一键导出成员 Excel（支持与列表一致的筛选/排序，不分页）。"""
    members = await member_service.export_members(
        session, current_user.guild_id, keyword, profession, status, sort_by, sort_order
    )
    # openpyxl 写表为 CPU 密集操作，放线程池避免阻塞事件循环
    guild = await session.get(Guild, current_user.guild_id) if current_user.guild_id else None
    guild_name = guild.name if guild else None
    content = await asyncio.to_thread(build_members_xlsx, members, guild_name, current_user.guild_id)
    date_tag = datetime.now(UTC).astimezone().strftime("%Y%m%d")
    # ASCII fallback + RFC 5987 编码中文文件名（均携带帮会来源）
    filename = f"members_{current_user.guild_id}_{date_tag}.xlsx"
    quoted = quote(member_export_filename(guild_name, date_tag, "xlsx"))
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}; filename*=UTF-8''{quoted}"},
    )


@router.get("/export-image")
async def export_image(
    keyword: str | None = Query(None, max_length=32),
    profession: str | None = Query(None, max_length=16),
    status: str | None = Query(None, max_length=16),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> Response:
    """一键导出成员长图 PNG（按主职业分区，供群内分享）。"""
    members = await member_service.export_members(
        session, current_user.guild_id, keyword, profession, status
    )
    # 长图内存占用随人数线性增长，超过上限提示分批导出（先于绘制拦截，避免内存峰值）
    if len(members) > MAX_IMAGE_MEMBERS:
        raise HTTPException(
            status_code=400,
            detail=f"成员数超过 {MAX_IMAGE_MEMBERS} 人长图上限，请按职业筛选后分批导出",
        )
    guild = await session.get(Guild, current_user.guild_id) if current_user.guild_id else None
    # PIL 绘制与 PNG 编码为 CPU 密集操作，放线程池避免阻塞事件循环
    content = await asyncio.to_thread(draw_members_png, members, guild.name if guild else None)
    date_tag = datetime.now(UTC).astimezone().strftime("%Y%m%d")
    quoted = quote(member_export_filename(guild.name if guild else None, date_tag, "png"))
    return Response(
        content=content,
        media_type="image/png",
        headers={"Content-Disposition": f"attachment; filename=members_{current_user.guild_id}_{date_tag}.png; filename*=UTF-8''{quoted}"},
    )


@router.get("/profession-stats", response_model=list[ProfessionStat])
async def profession_stats(
    formal_only: bool = Query(False, description="仅统计状态为正式的成员（缺少职业提示用）"),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """职业分布统计（首页仪表盘用，聚合查询）。"""
    return await member_service.profession_stats(session, current_user.guild_id, formal_only)


@router.get("/attendance-rate", response_model=list[AttendanceRateItem])
async def attendance_rate(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    return await member_service.attendance_rate(session, current_user.guild_id)


# 注意：动态路径 GET /{member_id} 必须注册在全部 GET 具体路径（/export、/export-image、
# /profession-stats、/attendance-rate）之后，否则具体路径会被 {member_id} 捕获报 422
@router.get("/{member_id}", response_model=MemberOut)
async def get_member_detail(
    member_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> MemberOut:
    """查询单个成员详情（成员详情页用）。"""
    member = await member_service.get_member(session, current_user.guild_id, member_id)
    return MemberOut.model_validate(member)

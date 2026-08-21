"""常驻库接口：成员 CRUD、搜索筛选、批量删除、Excel 导入、出勤率统计。"""
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
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
from app.utils.excel_import import MAX_FILE_SIZE, ExcelImportError, import_members

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
    member = await member_service.update_member(session, current_user.guild_id, member_id, body)
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
    # 文件大小校验：声明长度检查 + 读取后二次兜底（Content-Length 可能缺失或伪造）
    if file.size and file.size > MAX_FILE_SIZE:
        raise ExcelImportError("文件大小超过 5MB 限制")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise ExcelImportError("文件大小超过 5MB 限制")
    result = await import_members(session, current_user.guild_id, content)
    return {"message": f"导入成功 {result['imported']} 条，跳过 {result['skipped']} 条", **result}


@router.get("/profession-stats", response_model=list[ProfessionStat])
async def profession_stats(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[ProfessionStat]:
    """职业分布统计（首页仪表盘用，聚合查询）。"""
    return await member_service.profession_stats(session, current_user.guild_id)


@router.get("/attendance-rate", response_model=list[AttendanceRateItem])
async def attendance_rate(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[AttendanceRateItem]:
    return await member_service.attendance_rate(session, current_user.guild_id)

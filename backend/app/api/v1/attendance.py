"""出勤库接口：列表统计、导入正式/替补、添加补人、状态切换。"""
# 行数豁免（连续逻辑）：单资源薄路由（列表操作 + 导入端点声明同质）｜登记见 .agent/rules/file-length-rule.md 豁免清单
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.attendance import (
    AttendanceListResponse,
    AttendanceRecordOut,
    AttendanceStats,
    BatchStatusUpdate,
    FillerCreate,
    ImportSubstitutesRequest,
    ProfessionUpdate,
    RemarkUpdate,
    StatusUpdate,
    SubstituteCandidateOut,
)
from app.services import attendance_service
from app.utils import attendance_import

router = APIRouter(prefix="/schedules/{schedule_id}/attendance", tags=["出勤库"])


@router.get("", response_model=AttendanceListResponse)
async def list_attendance(
    schedule_id: int,
    current_user: User = Depends(get_current_user),  # 帮众可查看
    session: AsyncSession = Depends(get_db),
) -> AttendanceListResponse:
    records, stats = await attendance_service.list_attendance(session, current_user.guild_id, schedule_id)
    return AttendanceListResponse(
        items=[AttendanceRecordOut.model_validate(r) for r in records],
        stats=AttendanceStats(**stats),
    )


@router.post("/import-formal")
async def import_formal(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    result = await attendance_import.import_formal(session, current_user.guild_id, schedule_id)
    return {"message": f"导入正式成员 {result['imported']} 人（已存在跳过 {result['skipped']} 人）", **result}


@router.get("/substitute-candidates", response_model=list[SubstituteCandidateOut])
async def substitute_candidates(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[SubstituteCandidateOut]:
    members = await attendance_import.substitute_candidates(session, current_user.guild_id, schedule_id)
    for m in members:
        m.member_status = m.status  # 注入 member_status
    return [SubstituteCandidateOut.model_validate(m) for m in members]


@router.post("/import-substitutes")
async def import_substitutes(
    schedule_id: int,
    body: ImportSubstitutesRequest,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    result = await attendance_import.import_substitutes(session, current_user.guild_id, schedule_id, body.member_ids)
    return {"message": f"导入替补成员 {result['imported']} 人", **result}


@router.get("/member-candidates", response_model=list[SubstituteCandidateOut])
async def member_candidates(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[SubstituteCandidateOut]:
    """常驻库所有成员（正式+替补），已导入本场的排除。"""
    members = await attendance_import.all_member_candidates(session, current_user.guild_id, schedule_id)
    for m in members:
        m.member_status = m.status  # 注入 member_status
    return [SubstituteCandidateOut.model_validate(m) for m in members]


@router.post("/import-members")
async def import_members(
    schedule_id: int,
    body: ImportSubstitutesRequest,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """导入选中的常驻库成员（正式/替补均可）。"""
    result = await attendance_import.import_members(session, current_user.guild_id, schedule_id, body.member_ids)
    return {"message": f"导入成员 {result['imported']} 人（已存在跳过 {result['skipped']} 人）", **result}


@router.post("/fillers", response_model=AttendanceRecordOut)
async def add_filler(
    schedule_id: int,
    body: FillerCreate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AttendanceRecordOut:
    record = await attendance_service.add_filler(session, current_user.guild_id, schedule_id, body.name, body.profession)
    return AttendanceRecordOut.model_validate(record)


@router.put("/{record_id}/status", response_model=AttendanceRecordOut)
async def update_status(
    schedule_id: int,
    record_id: int,
    body: StatusUpdate,
    current_user: User = Depends(require_admin),  # 仅管理员可切换出勤状态（安全收紧）
    session: AsyncSession = Depends(get_db),
) -> AttendanceRecordOut:
    record = await attendance_service.update_status(
        session, current_user.guild_id, schedule_id, record_id, body.status
    )
    return AttendanceRecordOut.model_validate(record)


@router.put("/{record_id}/profession", response_model=AttendanceRecordOut)
async def update_profession(
    schedule_id: int,
    record_id: int,
    body: ProfessionUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AttendanceRecordOut:
    """更新出勤职业（主/副职业之一，管理员）。"""
    record = await attendance_service.update_record_profession(
        session, current_user.guild_id, schedule_id, record_id, body.profession
    )
    return AttendanceRecordOut.model_validate(record)


@router.put("/{record_id}/remark", response_model=AttendanceRecordOut)
async def update_remark(
    schedule_id: int,
    record_id: int,
    body: RemarkUpdate,
    current_user: User = Depends(require_admin),  # 仅管理员可修改出勤备注
    session: AsyncSession = Depends(get_db),
) -> AttendanceRecordOut:
    """更新出勤备注（留空清除）。导入时带出常驻库备注，此处可单独修改。"""
    record = await attendance_service.update_record_remark(
        session, current_user.guild_id, schedule_id, record_id, body.remark
    )
    return AttendanceRecordOut.model_validate(record)


@router.post("/batch-status")
async def batch_status(
    schedule_id: int,
    body: BatchStatusUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    count = await attendance_service.batch_update_status(
        session, current_user.guild_id, schedule_id, body.ids, body.status
    )
    return {"message": f"已更新 {count} 条出勤状态"}


@router.delete("/{record_id}")
async def delete_record(
    schedule_id: int,
    record_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await attendance_service.delete_record(session, current_user.guild_id, schedule_id, record_id)
    return {"message": "删除成功"}

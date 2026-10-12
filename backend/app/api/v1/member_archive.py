"""成员档案接口：出勤明细 / 录屏记录 / 排表历史（成员详情页档案 Tab，仅管理员）。

路由注册须先于 members.router（与 game_id_requests 同区防御性顺序），
设计依据见 memory-bank/design-member-archive.md §4。
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.member_archive import AttendanceHistoryOut, LineupHistoryOut, RecordingHistoryOut
from app.services import member_archive_service

router = APIRouter(prefix="/members", tags=["成员档案"])


@router.get("/{member_id}/attendance-history", response_model=list[AttendanceHistoryOut])
async def get_attendance_history(
    member_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AttendanceHistoryOut]:
    """该成员每场出勤明细（全量，按比赛时间倒序）。"""
    items = await member_archive_service.attendance_history(session, current_user.guild_id, member_id)
    return [AttendanceHistoryOut(**item) for item in items]


@router.get("/{member_id}/recording-history", response_model=list[RecordingHistoryOut])
async def get_recording_history(
    member_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[RecordingHistoryOut]:
    """该成员每场每局录屏记录（全量，含未提交行）。"""
    items = await member_archive_service.recording_history(session, current_user.guild_id, member_id)
    return [RecordingHistoryOut(**item) for item in items]


@router.get("/{member_id}/lineup-history", response_model=list[LineupHistoryOut])
async def get_lineup_history(
    member_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[LineupHistoryOut]:
    """该成员每场排表位置（全量）。"""
    items = await member_archive_service.lineup_history(session, current_user.guild_id, member_id)
    return [LineupHistoryOut(**item) for item in items]

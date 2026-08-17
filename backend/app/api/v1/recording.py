"""录屏审核接口：列表、提交、审核、批量审核、进度。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.recording import (
    BatchApproveRequest,
    RecordingListResponse,
    RecordingOut,
    RecordingReview,
    RecordingSubmit,
    RoundProgress,
)
from app.services import recording_service

router = APIRouter(prefix="/schedules/{schedule_id}/recordings", tags=["录屏审核"])


@router.get("", response_model=RecordingListResponse)
async def list_recordings(
    schedule_id: int,
    current_user: User = Depends(get_current_user),  # 帮众可查看
    session: AsyncSession = Depends(get_db),
) -> RecordingListResponse:
    recordings, progress = await recording_service.list_recordings(
        session, current_user.guild_id, schedule_id
    )
    return RecordingListResponse(
        items=[RecordingOut.model_validate(r) for r in recordings],
        progress=[RoundProgress(**p) for p in progress],
    )


@router.put("/{recording_id}/submit", response_model=RecordingOut)
async def submit_recording(
    schedule_id: int,
    recording_id: int,
    body: RecordingSubmit,
    current_user: User = Depends(get_current_user),  # 帮众可提交
    session: AsyncSession = Depends(get_db),
) -> RecordingOut:
    recording = await recording_service.submit_recording(
        session, current_user.guild_id, schedule_id, recording_id, body.url
    )
    return RecordingOut.model_validate(recording)


@router.put("/{recording_id}/approve", response_model=RecordingOut)
async def approve_recording(
    schedule_id: int,
    recording_id: int,
    body: RecordingReview = RecordingReview(),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RecordingOut:
    recording = await recording_service.approve_recording(
        session, current_user.guild_id, schedule_id, recording_id, body.remark
    )
    return RecordingOut.model_validate(recording)


@router.put("/{recording_id}/reject", response_model=RecordingOut)
async def reject_recording(
    schedule_id: int,
    recording_id: int,
    body: RecordingReview = RecordingReview(),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> RecordingOut:
    recording = await recording_service.reject_recording(
        session, current_user.guild_id, schedule_id, recording_id, body.remark
    )
    return RecordingOut.model_validate(recording)


@router.post("/batch-approve", response_model=dict)
async def batch_approve(
    schedule_id: int,
    body: BatchApproveRequest,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    count = await recording_service.batch_approve(
        session, current_user.guild_id, schedule_id, body.ids
    )
    return {"message": f"已批量审核通过 {count} 条录屏"}

"""排表接口：读取排表（帮众可看）、保存排表（管理员）、候选池（管理员）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.lineup import LineupCandidateOut, LineupOut, LineupUpdate
from app.services import lineup_service

router = APIRouter(prefix="/schedules/{schedule_id}/lineup", tags=["排表"])


@router.get("", response_model=LineupOut)
async def get_lineup(
    schedule_id: int,
    current_user: User = Depends(get_current_user),  # 排表总览帮众可查看
    session: AsyncSession = Depends(get_db),
) -> LineupOut:
    lineup = await lineup_service.get_lineup(session, current_user.guild_id, schedule_id)
    return LineupOut.model_validate(lineup)


@router.put("", response_model=LineupOut)
async def save_lineup(
    schedule_id: int,
    body: LineupUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> LineupOut:
    lineup = await lineup_service.save_lineup(
        session, current_user.guild_id, schedule_id, [t.model_dump() for t in body.data]
    )
    return LineupOut.model_validate(lineup)


@router.get("/candidates", response_model=list[LineupCandidateOut])
async def list_candidates(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[LineupCandidateOut]:
    return await lineup_service.candidate_pool(session, current_user.guild_id, schedule_id)

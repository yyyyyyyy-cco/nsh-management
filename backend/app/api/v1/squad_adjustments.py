"""分析调整副本接口：读取（帮众可看）、保存（管理员）。

调整仅作用于小队分析视图，不修改正式排表。
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.squad_adjustment import SquadAdjustmentOut, SquadAdjustmentUpdate
from app.services import squad_adjustment_service

router = APIRouter(prefix="/schedules/{schedule_id}/squad-adjustments", tags=["分析调整"])


@router.get("", response_model=SquadAdjustmentOut)
async def get_squad_adjustment(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> SquadAdjustmentOut:
    adj = await squad_adjustment_service.get_squad_adjustment(session, current_user.guild_id, schedule_id)
    # 未落库的空副本（GET 不写库）：补展示占位时间，首次保存时才会真正插入
    if adj.updated_at is None:
        adj.updated_at = datetime.now(UTC)
    return SquadAdjustmentOut.model_validate(adj)


@router.put("", response_model=SquadAdjustmentOut)
async def save_squad_adjustment(
    schedule_id: int,
    payload: SquadAdjustmentUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> SquadAdjustmentOut:
    adj = await squad_adjustment_service.save_squad_adjustment(
        session, current_user.guild_id, schedule_id, payload.data
    )
    return SquadAdjustmentOut.model_validate(adj)


@router.delete("/{player_name}", response_model=SquadAdjustmentOut)
async def remove_member_adjustment(
    schedule_id: int,
    player_name: str,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> SquadAdjustmentOut:
    """移除单个成员的分析调整，使其回归未排表状态。"""
    adj = await squad_adjustment_service.remove_member_adjustment(
        session, current_user.guild_id, schedule_id, player_name
    )
    return SquadAdjustmentOut.model_validate(adj)

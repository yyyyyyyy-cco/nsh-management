"""排表接口：读取排表（帮众可看）、保存排表（管理员）、候选池（管理员）。"""
from datetime import datetime, timezone

from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.lineup import LineupCandidateOut, LineupHistoryOut, LineupImportRequest, LineupOut, LineupUpdate
from app.services import lineup_service
from app.utils.member_names import normalize_member_name

router = APIRouter(prefix="/schedules/{schedule_id}/lineup", tags=["排表"])


@router.get("", response_model=LineupOut)
async def get_lineup(
    schedule_id: int,
    current_user: User = Depends(get_current_user),  # 排表总览帮众可查看
    session: AsyncSession = Depends(get_db),
) -> LineupOut:
    lineup = await lineup_service.get_lineup(session, current_user.guild_id, schedule_id)
    prof_map = await lineup_service.get_profession_map(session, schedule_id)
    # 新列可能为 NULL，转为空值避免 Pydantic 校验失败
    if lineup.title_remark is None:
        lineup.title_remark = ""
    if lineup.groups_remark is None:
        lineup.groups_remark = {}
    # 未落库的空排表（GET 不写库）：补展示占位值，首次保存时才会真正插入
    if lineup.id is None:
        lineup.id = 0
    if lineup.updated_at is None:
        lineup.updated_at = datetime.now(timezone.utc)
    result = LineupOut.model_validate(lineup)
    # 仅规范化响应，不批量改写历史数据；与候选池保持同一补人姓名键。
    for team in result.data:
        for slot in team.slots:
            name = normalize_member_name(slot.member_name)
            if slot.member_id is None:
                slot.member_name = name
            slot.profession = prof_map.get(name)
    return result


@router.put("", response_model=LineupOut)
async def save_lineup(
    schedule_id: int,
    body: LineupUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> LineupOut:
    lineup = await lineup_service.save_lineup(
        session, current_user.guild_id, schedule_id, [t.model_dump() for t in body.data],
        title_remark=body.title_remark, groups_remark=body.groups_remark,
    )
    return LineupOut.model_validate(lineup)


@router.get("/candidates", response_model=list[LineupCandidateOut])
async def list_candidates(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    return await lineup_service.candidate_pool(session, current_user.guild_id, schedule_id)


@router.get("/history", response_model=list[LineupHistoryOut])
async def list_history(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    return await lineup_service.list_lineup_history(session, current_user.guild_id, schedule_id)


@router.post("/import", response_model=dict)
async def import_history(
    schedule_id: int,
    body: LineupImportRequest,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    _, imported = await lineup_service.import_lineup(
        session,
        current_user.guild_id,
        schedule_id,
        body.source_schedule_id,
        body.team_keys,
    )
    return {"message": f"已导入 {imported} 名候选池成员（未出现的槽位已留空）"}

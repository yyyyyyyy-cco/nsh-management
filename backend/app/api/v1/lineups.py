"""排表接口：读取排表（帮众可看）、保存排表（管理员）、候选池（管理员）。"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.lineup import LineupCandidateOut, LineupHistoryOut, LineupImportRequest, LineupOut, LineupUpdate
from app.services import lineup_service

router = APIRouter(prefix="/schedules/{schedule_id}/lineup", tags=["排表"])


@router.get("", response_model=LineupOut)
async def get_lineup(
    schedule_id: int,
    current_user: User = Depends(get_current_user),  # 排表总览帮众可查看
    session: AsyncSession = Depends(get_db),
) -> LineupOut:
    lineup = await lineup_service.get_lineup(session, current_user.guild_id, schedule_id)
    # 填充槽位职业快照（出勤库按姓名匹配，供前端展示职业色点）
    prof_map = await lineup_service.get_profession_map(session, schedule_id)
    for team in lineup.data:
        for slot in team["slots"]:
            slot["profession"] = prof_map.get(slot.get("member_name"))
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
    return LineupOut.model_validate(lineup)


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
) -> list[LineupCandidateOut]:
    return await lineup_service.candidate_pool(session, current_user.guild_id, schedule_id)


@router.get("/history", response_model=list[LineupHistoryOut])
async def list_history(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[LineupHistoryOut]:
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

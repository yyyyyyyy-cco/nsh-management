"""个人战绩查询接口：按游戏 ID 聚合历史比赛数据。"""
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services import my_stats_service

router = APIRouter(prefix="/my-stats", tags=["个人战绩"])


# ---- Schema ----

class RankingItem(BaseModel):
    """单维度排名。"""
    label: str
    rank: int
    total: int


class PlayerRecordOut(BaseModel):
    """单局明细（含衍生指标 + 赛程元信息 + 该局排名）。"""
    schedule_id: int
    opponent: str
    match_time: str
    schedule_result: str
    round_no: int
    player_name: str
    profession: str | None
    camp: str
    kills: int
    springs: int
    assists: int
    player_damage: int
    armor_break_damage: int
    building_damage: int
    tower_break_damage: int
    healing: int
    damage_taken: int
    deaths: int
    revives: int
    fen_gu: int
    kda: float
    dps: int
    kpa_damage: int
    damage_per_death: int
    taken_per_death: int
    healing_per_death: int
    heal_conversion: float
    kill_ratio: float
    assist_ratio: float
    player_damage_ratio: float
    building_ratio: float
    taken_ratio: float
    death_ratio: float
    heal_ratio: float
    revive_rate: float
    fen_gu_rate: float
    rankings: list[RankingItem]
    rankings_camp: list[RankingItem]


class PlayerSummary(BaseModel):
    """个人概览统计。"""
    player_name: str
    total_rounds: int
    total_matches: int
    main_profession: str | None
    avg_kda: float
    avg_kills: float
    avg_damage: float
    avg_healing: float
    avg_deaths: float
    total_kills: int
    total_damage: int
    total_healing: int


class MyStatsResponse(BaseModel):
    """个人战绩响应。"""
    records: list[PlayerRecordOut]
    summary: PlayerSummary


# ---- 路由 ----

@router.get("", response_model=MyStatsResponse)
async def get_my_stats(
    player_name: str = Query(..., min_length=1, max_length=32, description="游戏 ID"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> MyStatsResponse:
    """按游戏 ID 查询个人历史战绩（帮众可访问）。"""
    data = await my_stats_service.query_player_stats(session, current_user.guild_id, player_name)
    return MyStatsResponse(
        records=[PlayerRecordOut(**r) for r in data["records"]],
        summary=PlayerSummary(**data["summary"]),
    )

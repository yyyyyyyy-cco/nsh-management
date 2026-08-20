"""比赛数据分析 Pydantic Schema。"""
from datetime import datetime

from pydantic import BaseModel, Field


class MatchDataOut(BaseModel):
    """比赛数据输出。"""
    id: int
    schedule_id: int
    round_no: int
    player_name: str
    profession: str | None
    camp: str
    kills: int
    springs: int
    assists: int
    resource: int
    player_damage: int
    armor_break_damage: int
    building_damage: int
    tower_break_damage: int
    healing: int
    damage_taken: int
    deaths: int
    revives: int
    fen_gu: int
    created_at: datetime

    model_config = {"from_attributes": True}


class PlayerRanking(BaseModel):
    """玩家排行数据。"""
    player_name: str
    profession: str | None
    camp: str
    value: int


class CampStats(BaseModel):
    """阵营统计数据。"""
    camp: str
    player_count: int
    total_kills: int
    total_damage: int
    total_healing: int
    total_damage_taken: int


class MatchDataListResponse(BaseModel):
    """比赛数据列表响应。"""
    items: list[MatchDataOut]
    camps: list[CampStats]
    import_count: int
    imported_rounds: list[int]  # 已导入的局号列表
    rounds: int  # 赛程总局数


class RankingsResponse(BaseModel):
    """排行榜响应。"""
    kills_ranking: list[PlayerRanking]
    damage_ranking: list[PlayerRanking]
    building_ranking: list[PlayerRanking]
    healing_ranking: list[PlayerRanking]
    taken_ranking: list[PlayerRanking]
    fen_gu_ranking: list[PlayerRanking]


class ProfessionStats(BaseModel):
    """职业统计数据。"""
    profession: str
    count: int
    avg_kills: float
    avg_damage: float
    avg_healing: float


class ProfessionStatsResponse(BaseModel):
    """职业统计响应。"""
    items: list[ProfessionStats]

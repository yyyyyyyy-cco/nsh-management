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


class ProfessionCampStats(BaseModel):
    """职业×阵营均值（供 我方/敌方 对比图表）。"""
    camp: str
    count: int
    avg_kills: float
    avg_player_damage: float
    avg_building_damage: float
    avg_healing: float
    avg_damage_taken: float
    avg_kda: float


class ProfessionComparison(BaseModel):
    """职业差值/波动值（基于分阵营均值）。"""
    metric: str
    camp1: str
    camp2: str
    value1: float
    value2: float
    diff: float
    wave: float


class ProfessionStats(BaseModel):
    """职业深度统计：17 项指标（人数 + 16 项衍生指标均值）+ 分阵营对比。

    17 项 = count + 16 项衍生指标均值（kda/dps/kpa_damage/damage_per_death/
    taken_per_death/healing_per_death/heal_conversion/kill_ratio/assist_ratio/
    player_damage_ratio/building_ratio/taken_ratio/death_ratio/heal_ratio/
    revive_rate/fen_gu_rate）。avg_kills/avg_damage/avg_healing 为兼容旧消费方保留。
    """
    profession: str
    count: int
    avg_kills: float
    avg_damage: float
    avg_healing: float
    avg_kda: float
    avg_dps: float
    avg_kpa_damage: float
    avg_damage_per_death: float
    avg_taken_per_death: float
    avg_healing_per_death: float
    avg_heal_conversion: float
    avg_kill_ratio: float
    avg_assist_ratio: float
    avg_player_damage_ratio: float
    avg_building_ratio: float
    avg_taken_ratio: float
    avg_death_ratio: float
    avg_heal_ratio: float
    avg_revive_rate: float
    avg_fen_gu_rate: float
    camps: list[ProfessionCampStats]
    comparison: list[ProfessionComparison]


class ProfessionStatsResponse(BaseModel):
    """职业统计响应。"""
    items: list[ProfessionStats]


class CampTotals(BaseModel):
    """阵营汇总（占比分母/对比用）。"""
    camp: str
    player_count: int
    kills: int
    assists: int
    player_damage: int
    building_damage: int
    healing: int
    damage_taken: int
    deaths: int
    springs: int
    revives: int
    fen_gu: int


class IndicatorOut(BaseModel):
    """带 16 项衍生指标的玩家数据（不含 resource，遵循“资源忽略不显示”约束）。"""
    id: int
    schedule_id: int
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


class IndicatorsResponse(BaseModel):
    """衍生指标数据列表响应。"""
    items: list[IndicatorOut]
    camps: list[CampTotals]


class CampCompareResponse(BaseModel):
    """阵营对比响应。"""
    camps: dict[str, CampTotals]
    comparison: dict[str, dict[str, float | int]]


class SquadMemberOut(BaseModel):
    """小队成员（含 16 项衍生指标全量）。"""
    player_name: str
    profession: str | None
    camp: str
    kills: int
    springs: int
    assists: int
    player_damage: int
    building_damage: int
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


class SquadTotalsOut(BaseModel):
    """小队汇总。"""
    player_count: int
    kills: int
    assists: int
    player_damage: int
    building_damage: int
    healing: int
    damage_taken: int
    deaths: int
    revives: int
    fen_gu: int


class SquadIndicatorsOut(BaseModel):
    """小队指标（成员衍生指标均值）。"""
    kda: float
    dps: float
    kpa_damage: float
    damage_per_death: float
    taken_per_death: float
    healing_per_death: float
    heal_conversion: float
    revive_rate: float
    fen_gu_rate: float


class SquadOut(BaseModel):
    """小队维度分析单元。"""
    squad_name: str
    category: str
    team_index: int
    members: list[SquadMemberOut]
    totals: SquadTotalsOut
    indicators: SquadIndicatorsOut


class SquadAnalysisResponse(BaseModel):
    """小队维度分析响应。"""
    squads: list[SquadOut]
"""个人战绩接口 Schema（自 api/v1/my_stats.py 抽出并扩展名称归属说明）。"""

from pydantic import BaseModel


class RankingItem(BaseModel):
    """单维度排名。"""

    label: str
    rank: int
    total: int


class PlayerRecordOut(BaseModel):
    """单局明细（含衍生指标 + 赛程元信息 + 该局排名；player_name 为比赛当时 ID）。"""

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


class PlayerIdentityOut(BaseModel):
    """名称归属说明：merged 合并已确认新旧 ID / exact 原始按名查询。"""

    mode: str
    query_player_name: str
    member_id: int | None = None
    current_game_id: str | None = None
    aliases: list[str]


class MyStatsResponse(BaseModel):
    """个人战绩响应。"""

    records: list[PlayerRecordOut]
    summary: PlayerSummary
    identity: PlayerIdentityOut


class PlayerNameList(BaseModel):
    """玩家名候选列表。"""

    names: list[str]

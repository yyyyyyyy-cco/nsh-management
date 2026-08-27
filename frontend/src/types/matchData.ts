/** 比赛数据分析类型定义。 */

/** 比赛数据记录 */
export interface MatchData {
  id: number
  schedule_id: number
  round_no: number
  player_name: string
  profession: string | null
  camp: string
  kills: number
  springs: number
  assists: number
  resource: number
  player_damage: number
  armor_break_damage: number
  building_damage: number
  tower_break_damage: number
  healing: number
  damage_taken: number
  deaths: number
  revives: number
  fen_gu: number
  created_at: string
}

/** 阵营统计 */
export interface CampStats {
  camp: string
  player_count: number
  total_kills: number
  total_damage: number
  total_healing: number
  total_damage_taken: number
}

/** 玩家排行 */
export interface PlayerRanking {
  player_name: string
  profession: string | null
  camp: string
  value: number
}

/** 排行榜响应 */
export interface RankingsResponse {
  kills_ranking: PlayerRanking[]
  damage_ranking: PlayerRanking[]
  building_ranking: PlayerRanking[]
  healing_ranking: PlayerRanking[]
  taken_ranking: PlayerRanking[]
  fen_gu_ranking: PlayerRanking[]
}

/** 职业统计（17 项指标 = 人数 + 16 项衍生指标均值 + 分阵营对比） */
export interface ProfessionStats {
  profession: string
  count: number
  avg_kills: number
  avg_damage: number
  avg_healing: number
  avg_kda: number
  avg_dps: number
  avg_kpa_damage: number
  avg_damage_per_death: number
  avg_taken_per_death: number
  avg_healing_per_death: number
  avg_heal_conversion: number
  avg_kill_ratio: number
  avg_assist_ratio: number
  avg_player_damage_ratio: number
  avg_building_ratio: number
  avg_taken_ratio: number
  avg_death_ratio: number
  avg_heal_ratio: number
  avg_revive_rate: number
  avg_fen_gu_rate: number
  camps: ProfessionCampStats[]
  comparison: ProfessionComparison[]
}

/** 职业×阵营均值 */
export interface ProfessionCampStats {
  camp: string
  count: number
  avg_kills: number
  avg_player_damage: number
  avg_building_damage: number
  avg_healing: number
  avg_damage_taken: number
  avg_kda: number
}

/** 职业差值/波动值 */
export interface ProfessionComparison {
  metric: string
  camp1: string
  camp2: string
  value1: number
  value2: number
  diff: number
  wave: number
}

/** 阵营汇总（占比分母/对比用） */
export interface CampTotals {
  camp: string
  player_count: number
  kills: number
  assists: number
  player_damage: number
  building_damage: number
  healing: number
  damage_taken: number
  deaths: number
  springs: number
  revives: number
  fen_gu: number
}

/** 带 16 项衍生指标的玩家数据 */
export interface MatchDataIndicators extends MatchData {
  kda: number
  dps: number
  kpa_damage: number
  damage_per_death: number
  taken_per_death: number
  healing_per_death: number
  heal_conversion: number
  kill_ratio: number
  assist_ratio: number
  player_damage_ratio: number
  building_ratio: number
  taken_ratio: number
  death_ratio: number
  heal_ratio: number
  revive_rate: number
  fen_gu_rate: number
}

/** 衍生指标数据列表响应 */
export interface IndicatorsResponse {
  items: MatchDataIndicators[]
  camps: CampTotals[]
}

/** 阵营对比响应 */
export interface CampCompareResponse {
  camps: Record<string, CampTotals>
  comparison: Record<string, Record<string, number>>
}

/** 小队成员（含 16 项衍生指标全量） */
export interface SquadMember {
  player_name: string
  profession: string | null
  camp: string
  kills: number
  springs: number
  assists: number
  player_damage: number
  building_damage: number
  healing: number
  damage_taken: number
  deaths: number
  revives: number
  fen_gu: number
  kda: number
  dps: number
  kpa_damage: number
  damage_per_death: number
  taken_per_death: number
  healing_per_death: number
  heal_conversion: number
  kill_ratio: number
  assist_ratio: number
  player_damage_ratio: number
  building_ratio: number
  taken_ratio: number
  death_ratio: number
  heal_ratio: number
  revive_rate: number
  fen_gu_rate: number
}

/** 小队汇总 */
export interface SquadTotals {
  player_count: number
  kills: number
  assists: number
  player_damage: number
  building_damage: number
  healing: number
  damage_taken: number
  deaths: number
  revives: number
  fen_gu: number
}

/** 小队指标（成员衍生指标均值） */
export interface SquadIndicators {
  kda: number
  dps: number
  kpa_damage: number
  damage_per_death: number
  taken_per_death: number
  healing_per_death: number
  heal_conversion: number
  revive_rate: number
  fen_gu_rate: number
}

/** 小队维度分析单元 */
export interface SquadAnalysis {
  squad_name: string
  category: string
  team_index: number
  members: SquadMember[]
  totals: SquadTotals
  indicators: SquadIndicators
}

/** 小队维度分析响应 */
export interface SquadAnalysisResponse {
  squads: SquadAnalysis[]
}

/** 比赛数据列表响应 */
export interface MatchDataListResponse {
  items: MatchData[]
  camps: CampStats[]
  import_count: number
  imported_rounds: number[]
  rounds: number
}

/** 个人战绩查询类型定义。 */

/** 单维度排名 */
export interface RankingItem {
  label: string
  rank: number
  total: number
}

/** 单局明细（含衍生指标 + 赛程元信息 + 该局排名） */
export interface PlayerRecord {
  schedule_id: number
  opponent: string
  match_time: string
  schedule_result: string
  round_no: number
  player_name: string
  profession: string | null
  camp: string
  kills: number
  springs: number
  assists: number
  player_damage: number
  armor_break_damage: number
  building_damage: number
  tower_break_damage: number
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
  rankings: RankingItem[]
  rankings_camp: RankingItem[]
}

/** 个人概览统计 */
export interface PlayerSummary {
  player_name: string
  total_rounds: number
  total_matches: number
  main_profession: string | null
  avg_kda: number
  avg_kills: number
  avg_damage: number
  avg_healing: number
  avg_deaths: number
  total_kills: number
  total_damage: number
  total_healing: number
}

/** 个人战绩响应 */
export interface MyStatsResponse {
  records: PlayerRecord[]
  summary: PlayerSummary
}

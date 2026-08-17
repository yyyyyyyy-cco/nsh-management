/** 比赛数据分析类型定义。 */

/** 比赛数据记录 */
export interface MatchData {
  id: number
  schedule_id: number
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
  healing_ranking: PlayerRanking[]
  fen_gu_ranking: PlayerRanking[]
}

/** 职业统计 */
export interface ProfessionStats {
  profession: string
  count: number
  avg_kills: number
  avg_damage: number
  avg_healing: number
}

/** 比赛数据列表响应 */
export interface MatchDataListResponse {
  items: MatchData[]
  camps: CampStats[]
  import_count: number
}

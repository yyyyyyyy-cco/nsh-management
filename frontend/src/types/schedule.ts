/** 赛程信息。 */
export interface ScheduleInfo {
  id: number
  guild_id: number
  opponent: string
  match_time: string
  location: string | null
  rounds: number
  result: 'win' | 'lose' | 'draw' | 'pending'
  round_results: string[] | null
  profession_config?: Record<string, number> | null // 单场职业配置覆盖，空/未定义沿用系统配置
  created_at: string
}

/** 创建载荷：与后端 ScheduleCreate 对齐（opponent / match_time / rounds 必填）。 */
export interface ScheduleCreatePayload {
  opponent: string
  match_time: string
  location?: string | null
  rounds: number
}

/** 更新载荷：与后端 ScheduleUpdate 对齐（全部可选，且不含 rounds —— 局数创建后不可修改）。 */
export interface ScheduleUpdatePayload {
  opponent?: string
  match_time?: string
  location?: string | null
  result?: string
  round_results?: string[] | null
}

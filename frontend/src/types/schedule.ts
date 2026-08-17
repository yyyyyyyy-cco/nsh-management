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
  created_at: string
}

/** 创建/更新载荷（局数仅创建时可传）。 */
export interface SchedulePayload {
  opponent?: string
  match_time?: string
  location?: string | null
  rounds?: number
  result?: string
  round_results?: string[] | null
}

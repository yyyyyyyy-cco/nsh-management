/** 排表类型定义。 */

export interface LineupSlot {
  slot_index: number
  member_id: number | null
  member_name: string
  remark: string
  profession?: string | null
}

export interface LineupTeam {
  category: string
  team_index: number
  slots: LineupSlot[]
}

export interface LineupInfo {
  id: number
  schedule_id: number
  data: LineupTeam[]
  title_remark: string
  groups_remark: Record<string, string>
  updated_at: string
}

export interface LineupCandidate {
  member_id: number | null
  member_name: string
  profession: string
  member_status: 'formal' | 'substitute' | 'filler'
  attendance_remark: string | null
}

/** 历史排表条目（含完整排表数据，供导入预览）。 */
export interface LineupHistoryItem {
  schedule_id: number
  opponent: string
  match_time: string
  teams: LineupTeam[]
}

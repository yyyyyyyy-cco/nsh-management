/** 排表类型定义。 */

export interface LineupSlot {
  slot_index: number
  member_id: number | null
  member_name: string
  remark: string
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
  updated_at: string
}

export interface LineupCandidate {
  member_id: number | null
  member_name: string
  profession: string
  member_status: 'formal' | 'substitute' | 'filler'
}

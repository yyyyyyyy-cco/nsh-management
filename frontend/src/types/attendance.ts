/** 出勤库类型定义。 */

export interface AttendanceRecord {
  id: number
  schedule_id: number
  member_id: number | null
  member_name: string
  profession: string
  status: 'normal' | 'leave'
  is_filler: boolean
  remark: string | null
  member_status: 'formal' | 'substitute' | null
  professions?: string[]
}

export interface AttendanceStats {
  total: number
  normal_count: number
  leave_count: number
  gap: number
}

export interface AttendanceList {
  items: AttendanceRecord[]
  stats: AttendanceStats
}

export interface SubstituteCandidate {
  id: number
  name: string
  main_profession: string
  sub_profession: string | null
  remark: string | null
  member_status?: string
}

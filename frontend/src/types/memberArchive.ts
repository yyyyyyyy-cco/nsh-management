/** 成员档案接口类型（出勤明细 / 录屏记录 / 排表历史，对应 backend/app/schemas/member_archive.py）。 */

/** 出勤明细行。 */
export interface MemberAttendanceHistoryItem {
  schedule_id: number
  opponent: string
  match_time: string
  schedule_result: string
  status: string
  remark: string | null
}

/** 录屏记录行（「未提交」由 url 为空 + status=pending 派生）。 */
export interface MemberRecordingHistoryItem {
  schedule_id: number
  opponent: string
  match_time: string
  round_number: number
  url: string | null
  status: string
  review_remark: string | null
}

/** 排表历史行。 */
export interface MemberLineupHistoryItem {
  schedule_id: number
  opponent: string
  match_time: string
  category: string
  team_index: number
  slot_index: number
  slot_remark: string | null
}

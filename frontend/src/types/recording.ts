/** 录屏审核类型定义。 */

/** 录屏记录 */
export interface Recording {
  id: number
  schedule_id: number
  member_id: number | null
  member_name: string
  profession?: string | null
  round_number: number
  url: string | null
  /** 帮众备注（展示层对帮众脱敏，仅管理员可见） */
  note: string | null
  status: 'pending' | 'approved' | 'rejected'
  review_remark: string | null
  reviewed_at: string | null
  created_at: string
}

/** 单局审核进度 */
export interface RoundProgress {
  round_number: number
  total: number
  approved: number
  rejected: number
  pending: number
}

/** 录屏列表响应 */
export interface RecordingListResponse {
  items: Recording[]
  progress: RoundProgress[]
}

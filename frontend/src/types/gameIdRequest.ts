/** 游戏 ID 改名申请类型定义。 */

export type GameIdRequestStatus = 'pending' | 'approved' | 'rejected' | 'invalidated'

/** 候选成员（最小信息，选择改名对象用）。 */
export interface GameIdOption {
  id: number
  name: string
  main_profession: string
  status: 'formal' | 'substitute'
}

export interface GameIdOptionPage {
  items: GameIdOption[]
  total: number
  page: number
  page_size: number
}

/** 帮众可见的申请记录（不含账号快照）。 */
export interface GameIdRequestItem {
  id: number
  member_id: number | null
  old_game_id: string
  new_game_id: string
  status: GameIdRequestStatus
  review_remark: string | null
  invalidated_reason: string | null
  created_at: string
  reviewed_at: string | null
  updated_at: string
}

/** 管理员可见的申请记录（含提交/审核账号快照与当前成员名）。 */
export interface GameIdRequestAdminItem extends GameIdRequestItem {
  requester_username: string
  reviewer_username: string | null
  current_game_id: string | null
}

export interface GameIdRequestMemberPage {
  member: GameIdOption
  items: GameIdRequestItem[]
  total: number
  page: number
  page_size: number
}

export interface GameIdRequestAdminPage {
  items: GameIdRequestAdminItem[]
  total: number
  page: number
  page_size: number
}

/** 状态文案与标签色（invalidated 用 info；文字始终可见，不单靠颜色区分）。 */
export const GAME_ID_STATUS_LABELS: Record<GameIdRequestStatus, string> = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已驳回',
  invalidated: '已失效',
}

export const GAME_ID_STATUS_TYPES: Record<GameIdRequestStatus, 'warning' | 'success' | 'danger' | 'info'> = {
  pending: 'warning',
  approved: 'success',
  rejected: 'danger',
  invalidated: 'info',
}

/** 失效原因文案。 */
export const GAME_ID_INVALIDATED_LABELS: Record<string, string> = {
  member_renamed: '成员已被直接改名',
  member_deleted: '成员已被删除',
}

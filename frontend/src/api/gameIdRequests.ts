/** 游戏 ID 改名申请接口。 */
import http from '@/api/http'
import type {
  GameIdOptionPage,
  GameIdRequestAdminItem,
  GameIdRequestAdminPage,
  GameIdRequestItem,
  GameIdRequestMemberPage,
} from '@/types/gameIdRequest'

/** 常驻成员最小候选（帮众选择改名对象）。 */
export function listGameIdOptions(params: { q?: string; page?: number; page_size?: number }): Promise<GameIdOptionPage> {
  return http.get('/members/game-id-options', { params })
}

/** 提交改名申请（帮众）。 */
export function createGameIdRequest(
  memberId: number,
  data: { expected_old_game_id: string; new_game_id: string },
): Promise<GameIdRequestItem> {
  return http.post(`/members/${memberId}/game-id-requests`, data)
}

/** 某成员的申请历史（帮众/管理员）。 */
export function listMemberGameIdRequests(
  memberId: number,
  params: { page?: number; page_size?: number },
): Promise<GameIdRequestMemberPage> {
  return http.get(`/members/${memberId}/game-id-requests`, { params })
}

/** 帮会审核列表（管理员）。 */
export function listGameIdRequests(params: {
  status?: string
  keyword?: string
  page?: number
  page_size?: number
}): Promise<GameIdRequestAdminPage> {
  return http.get('/members/game-id-requests', { params })
}

/** 审核申请（管理员）：通过需显式确认身份，驳回需填写原因。 */
export function auditGameIdRequest(
  requestId: number,
  data: { action: 'approve' | 'reject'; identity_confirmed?: boolean; review_remark?: string | null },
): Promise<GameIdRequestAdminItem> {
  return http.put(`/members/game-id-requests/${requestId}/audit`, data)
}

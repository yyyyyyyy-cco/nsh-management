/** 排表接口。 */
import http from './http'
import type { LineupCandidate, LineupHistoryItem, LineupInfo, LineupTeam } from '@/types/lineup'

export function getLineup(scheduleId: number): Promise<LineupInfo> {
  return http.get(`/schedules/${scheduleId}/lineup`)
}

export interface LineupSavePayload {
  data: LineupTeam[]
  title_remark?: string
  groups_remark?: Record<string, string>
}

export function saveLineup(scheduleId: number, payload: LineupSavePayload): Promise<LineupInfo> {
  return http.put(`/schedules/${scheduleId}/lineup`, payload)
}

export function getLineupCandidates(scheduleId: number): Promise<LineupCandidate[]> {
  return http.get(`/schedules/${scheduleId}/lineup/candidates`)
}

/** 历史排表列表（本帮会有排表的其他赛程）。 */
export function getLineupHistory(scheduleId: number): Promise<LineupHistoryItem[]> {
  return http.get(`/schedules/${scheduleId}/lineup/history`)
}

/** 按小队导入历史排表（仅候选池成员，其余留空）。 */
export function importLineup(
  scheduleId: number,
  payload: { source_schedule_id: number; team_keys: string[] },
): Promise<{ message: string }> {
  return http.post(`/schedules/${scheduleId}/lineup/import`, payload)
}

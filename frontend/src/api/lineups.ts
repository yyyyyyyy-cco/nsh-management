/** 排表接口。 */
import http from './http'
import type { LineupCandidate, LineupInfo, LineupTeam } from '@/types/lineup'

export function getLineup(scheduleId: number): Promise<LineupInfo> {
  return http.get(`/schedules/${scheduleId}/lineup`)
}

export function saveLineup(scheduleId: number, data: LineupTeam[]): Promise<LineupInfo> {
  return http.put(`/schedules/${scheduleId}/lineup`, { data })
}

export function getLineupCandidates(scheduleId: number): Promise<LineupCandidate[]> {
  return http.get(`/schedules/${scheduleId}/lineup/candidates`)
}

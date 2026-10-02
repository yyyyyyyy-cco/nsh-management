/** 分析调整副本接口（小队分析内手动分配，不影响正式排表）。 */
import http from './http'

export interface SquadAdjustments {
  schedule_id: number
  /** 成员名 → "category:team_index"（如 "进攻1:0"） */
  data: Record<string, string>
  updated_at: string
}

export function getSquadAdjustments(scheduleId: number): Promise<SquadAdjustments> {
  return http.get(`/schedules/${scheduleId}/squad-adjustments`)
}

export function saveSquadAdjustments(
  scheduleId: number,
  data: Record<string, string>,
): Promise<SquadAdjustments> {
  return http.put(`/schedules/${scheduleId}/squad-adjustments`, { data })
}

export function removeSquadAdjustment(
  scheduleId: number,
  playerName: string,
): Promise<SquadAdjustments> {
  return http.delete(`/schedules/${scheduleId}/squad-adjustments/${encodeURIComponent(playerName)}`)
}

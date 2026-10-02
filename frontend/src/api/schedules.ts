/** 联赛日程接口。 */
import http from './http'
import type { ScheduleInfo, SchedulePayload } from '@/types/schedule'

export function listSchedules(params?: { start?: string; end?: string }): Promise<ScheduleInfo[]> {
  return http.get('/schedules', { params })
}

export function getSchedule(id: number): Promise<ScheduleInfo> {
  return http.get(`/schedules/${id}`)
}

export function createSchedule(data: SchedulePayload): Promise<ScheduleInfo> {
  return http.post('/schedules', data)
}

export function updateSchedule(id: number, data: SchedulePayload): Promise<ScheduleInfo> {
  return http.put(`/schedules/${id}`, data)
}

export function updateScheduleProfessionConfig(
  id: number,
  configs: Record<string, number> | null,
): Promise<ScheduleInfo> {
  return http.put(`/schedules/${id}/profession-config`, { configs })
}

export function deleteSchedule(id: number): Promise<{ message: string }> {
  return http.delete(`/schedules/${id}`)
}

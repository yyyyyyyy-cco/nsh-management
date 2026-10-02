/** 出勤库接口。 */
import http from './http'
import type { AttendanceList, AttendanceRecord, SubstituteCandidate } from '@/types/attendance'

export function getAttendance(scheduleId: number): Promise<AttendanceList> {
  return http.get(`/schedules/${scheduleId}/attendance`)
}

export function importFormal(scheduleId: number): Promise<{ message: string; imported: number; skipped: number }> {
  return http.post(`/schedules/${scheduleId}/attendance/import-formal`)
}

export function getSubstituteCandidates(scheduleId: number): Promise<SubstituteCandidate[]> {
  return http.get(`/schedules/${scheduleId}/attendance/substitute-candidates`)
}

export function importSubstitutes(
  scheduleId: number,
  memberIds: number[],
): Promise<{ message: string; imported: number; skipped: number }> {
  return http.post(`/schedules/${scheduleId}/attendance/import-substitutes`, { member_ids: memberIds })
}

export function addFiller(scheduleId: number, data: { name: string; profession: string }): Promise<AttendanceRecord> {
  return http.post(`/schedules/${scheduleId}/attendance/fillers`, data)
}

export function updateStatus(
  scheduleId: number,
  recordId: number,
  status: 'normal' | 'leave',
): Promise<AttendanceRecord> {
  return http.put(`/schedules/${scheduleId}/attendance/${recordId}/status`, { status })
}

export function updateProfession(
  scheduleId: number,
  recordId: number,
  profession: string,
): Promise<AttendanceRecord> {
  return http.put(`/schedules/${scheduleId}/attendance/${recordId}/profession`, { profession })
}

export function updateRemark(
  scheduleId: number,
  recordId: number,
  remark: string,
): Promise<AttendanceRecord> {
  return http.put(`/schedules/${scheduleId}/attendance/${recordId}/remark`, { remark })
}

export function batchStatus(
  scheduleId: number,
  ids: number[],
  status: 'normal' | 'leave',
): Promise<{ message: string }> {
  return http.post(`/schedules/${scheduleId}/attendance/batch-status`, { ids, status })
}

export function deleteRecord(scheduleId: number, recordId: number): Promise<{ message: string }> {
  return http.delete(`/schedules/${scheduleId}/attendance/${recordId}`)
}

export function getMemberCandidates(scheduleId: number): Promise<SubstituteCandidate[]> {
  return http.get(`/schedules/${scheduleId}/attendance/member-candidates`)
}

export function importAttendanceMembers(
  scheduleId: number,
  memberIds: number[],
): Promise<{ message: string; imported: number; skipped: number }> {
  return http.post(`/schedules/${scheduleId}/attendance/import-members`, { member_ids: memberIds })
}

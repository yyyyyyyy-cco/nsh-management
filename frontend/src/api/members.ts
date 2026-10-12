/** 常驻库成员接口。 */
import http from './http'
import type { MemberInfo } from '@/types/member'
import type {
  MemberAttendanceHistoryItem,
  MemberLineupHistoryItem,
  MemberRecordingHistoryItem,
} from '@/types/memberArchive'

export interface MemberStats {
  formal_count: number
  substitute_count: number
}

export interface MemberPage {
  items: MemberInfo[]
  total: number
  page: number
  page_size: number
  stats: MemberStats
}

export interface ProfessionStat {
  profession: string
  count: number
}

export interface MemberQuery {
  page?: number
  page_size?: number
  keyword?: string
  profession?: string
  status?: string
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface AttendanceRateItem {
  member_id: number
  name: string
  main_profession: string
  status: string
  normal_count: number
  leave_count: number
  attendance_rate: number | null
}

export interface ImportResult {
  message: string
  imported: number
  skipped: number
  errors: string[]
}

export function listMembers(params: MemberQuery): Promise<MemberPage> {
  return http.get('/members', { params })
}

export function createMember(data: Partial<MemberInfo>): Promise<MemberInfo> {
  return http.post('/members', data)
}

export function updateMember(id: number, data: Partial<MemberInfo>): Promise<MemberInfo> {
  return http.put(`/members/${id}`, data)
}

export function deleteMember(id: number): Promise<{ message: string }> {
  return http.delete(`/members/${id}`)
}

/** 查询单个成员详情（成员详情页）。 */
export function getMember(id: number): Promise<MemberInfo> {
  return http.get(`/members/${id}`)
}

export function batchDeleteMembers(ids: number[]): Promise<{ message: string }> {
  return http.post('/members/batch-delete', { ids })
}

export function importMembers(file: File): Promise<ImportResult> {
  const form = new FormData()
  form.append('file', file)
  return http.post('/members/import', form, { headers: { 'Content-Type': 'multipart/form-data' } })
}

/** 一键导出成员 Excel（与列表同款筛选/排序，不分页），返回二进制流。 */
export async function exportMembers(params: MemberQuery): Promise<Blob> {
  return http.get('/members/export', { params, responseType: 'blob' })
}

/** 一键导出成员长图 PNG（按主职业分区），返回二进制流。 */
export async function exportMembersImage(params: MemberQuery): Promise<Blob> {
  return http.get('/members/export-image', { params, responseType: 'blob' })
}

export function getAttendanceRate(): Promise<AttendanceRateItem[]> {
  return http.get('/members/attendance-rate')
}

export function getProfessionStats(params?: { formal_only?: boolean }): Promise<ProfessionStat[]> {
  return http.get('/members/profession-stats', { params })
}

/** 成员档案：出勤明细（成员详情页「出勤档案」Tab）。 */
export function getMemberAttendanceHistory(id: number): Promise<MemberAttendanceHistoryItem[]> {
  return http.get(`/members/${id}/attendance-history`)
}

/** 成员档案：录屏记录（含未提交，成员详情页「录屏记录」Tab）。 */
export function getMemberRecordingHistory(id: number): Promise<MemberRecordingHistoryItem[]> {
  return http.get(`/members/${id}/recording-history`)
}

/** 成员档案：排表历史（成员详情页「排表历史」Tab）。 */
export function getMemberLineupHistory(id: number): Promise<MemberLineupHistoryItem[]> {
  return http.get(`/members/${id}/lineup-history`)
}

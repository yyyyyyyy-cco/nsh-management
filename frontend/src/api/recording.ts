/** 录屏审核 API。 */
import http from '@/api/http'
import type { Recording, RecordingListResponse } from '@/types/recording'

/** 获取录屏列表 */
export async function getRecordings(scheduleId: number): Promise<RecordingListResponse> {
  return http.get(`/schedules/${scheduleId}/recordings`)
}

/** 提交录屏链接 */
export async function submitRecording(scheduleId: number, recordingId: number, url: string): Promise<Recording> {
  return http.put(`/schedules/${scheduleId}/recordings/${recordingId}/submit`, { url })
}

/** 审核通过 */
export async function approveRecording(scheduleId: number, recordingId: number, remark?: string): Promise<Recording> {
  return http.put(`/schedules/${scheduleId}/recordings/${recordingId}/approve`, { remark })
}

/** 审核驳回 */
export async function rejectRecording(scheduleId: number, recordingId: number, remark?: string): Promise<Recording> {
  return http.put(`/schedules/${scheduleId}/recordings/${recordingId}/reject`, { remark })
}

/** 批量审核通过 */
export async function batchApprove(scheduleId: number, ids: number[]): Promise<{ message: string }> {
  return http.post(`/schedules/${scheduleId}/recordings/batch-approve`, { ids })
}

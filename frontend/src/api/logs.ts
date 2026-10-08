/** 系统日志 API（仅开发者）。 */
import http from '@/api/http'
import type { LogList, LogQuery, LogStats } from '@/types/log'

/** 分页查询审计日志 */
export async function getLogs(params: LogQuery): Promise<LogList> {
  return http.get('/developer/logs', { params })
}

/** 日志概览统计 */
export async function getLogStats(): Promise<LogStats> {
  return http.get('/developer/logs/stats')
}

/** 清理 days 天前的日志（默认 90） */
export async function clearLogs(days: number): Promise<{ message: string; deleted: number }> {
  return http.delete('/developer/logs', { data: { days } })
}

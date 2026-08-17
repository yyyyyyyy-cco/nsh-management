/** 比赛数据分析 API。 */
import http from '@/api/http'
import type {
  MatchDataListResponse,
  ProfessionStats,
  RankingsResponse,
} from '@/types/matchData'

/** 导入 CSV 比赛数据 */
export async function importCsv(scheduleId: number, file: File): Promise<{ message: string; count: number }> {
  const formData = new FormData()
  formData.append('file', file)
  return http.post(`/schedules/${scheduleId}/match-data/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取比赛数据列表 */
export async function getMatchData(scheduleId: number): Promise<MatchDataListResponse> {
  return http.get(`/schedules/${scheduleId}/match-data`)
}

/** 获取排行榜 */
export async function getRankings(
  scheduleId: number,
  params?: { camp?: string; limit?: number }
): Promise<RankingsResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/rankings`, { params })
}

/** 获取职业统计 */
export async function getProfessionStats(
  scheduleId: number,
  params?: { camp?: string }
): Promise<{ items: ProfessionStats[] }> {
  return http.get(`/schedules/${scheduleId}/match-data/professions`, { params })
}

/** 获取 HTML 报告 URL */
export function getReportUrl(scheduleId: number): string {
  return `/api/v1/schedules/${scheduleId}/match-data/report`
}

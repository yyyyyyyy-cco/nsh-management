/** 比赛数据分析 API。 */
import http from '@/api/http'
import type {
  MatchDataListResponse,
  ProfessionStats,
  RankingsResponse,
} from '@/types/matchData'

/** 导入 CSV 比赛数据到指定局（覆盖该局已有数据） */
export async function importCsv(scheduleId: number, file: File, roundNo: number): Promise<{ message: string; count: number }> {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('round_no', String(roundNo))
  return http.post(`/schedules/${scheduleId}/match-data/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

/** 获取比赛数据列表（可按局过滤） */
export async function getMatchData(scheduleId: number, roundNo?: number): Promise<MatchDataListResponse> {
  return http.get(`/schedules/${scheduleId}/match-data`, {
    params: roundNo ? { round_no: roundNo } : undefined,
  })
}

/** 获取排行榜 */
export async function getRankings(
  scheduleId: number,
  params?: { roundNo?: number; camp?: string; limit?: number }
): Promise<RankingsResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/rankings`, {
    params: {
      ...(params?.roundNo ? { round_no: params.roundNo } : {}),
      ...(params?.camp ? { camp: params.camp } : {}),
      ...(params?.limit ? { limit: params.limit } : {}),
    },
  })
}

/** 获取职业统计 */
export async function getProfessionStats(
  scheduleId: number,
  params?: { camp?: string }
): Promise<{ items: ProfessionStats[] }> {
  return http.get(`/schedules/${scheduleId}/match-data/professions`, { params })
}

/** 获取 HTML 报告 URL（可按局生成） */
export function getReportUrl(scheduleId: number, roundNo?: number): string {
  return `/api/v1/schedules/${scheduleId}/match-data/report${roundNo ? `?round_no=${roundNo}` : ''}`
}

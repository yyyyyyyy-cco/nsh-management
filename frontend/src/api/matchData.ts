/** 比赛数据分析 API。 */
import http from '@/api/http'
import type {
  CampCompareResponse,
  IndicatorsResponse,
  MatchDataListResponse,
  ProfessionStats,
  RankingsResponse,
  SquadAnalysisResponse,
} from '@/types/matchData'

/** 导入 CSV 比赛数据到指定局（覆盖该局已有数据） */
export async function importCsv(
  scheduleId: number,
  file: File,
  roundNo: number,
): Promise<{ message: string; count: number }> {
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
  params?: { roundNo?: number; camp?: string; limit?: number },
): Promise<RankingsResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/rankings`, {
    params: {
      ...(params?.roundNo ? { round_no: params.roundNo } : {}),
      ...(params?.camp ? { camp: params.camp } : {}),
      ...(params?.limit ? { limit: params.limit } : {}),
    },
  })
}

/** 获取职业统计（17 项指标，可按局/阵营过滤） */
export async function getProfessionStats(
  scheduleId: number,
  params?: { roundNo?: number; camp?: string },
): Promise<{ items: ProfessionStats[] }> {
  return http.get(`/schedules/${scheduleId}/match-data/professions`, {
    params: {
      ...(params?.roundNo ? { round_no: params.roundNo } : {}),
      ...(params?.camp ? { camp: params.camp } : {}),
    },
  })
}

/** 获取带 16 项衍生指标的数据列表（可按局过滤） */
export async function getIndicators(scheduleId: number, roundNo?: number): Promise<IndicatorsResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/indicators`, {
    params: roundNo ? { round_no: roundNo } : undefined,
  })
}

/** 获取阵营对比数据（可按局过滤） */
export async function getCampCompare(scheduleId: number, roundNo?: number): Promise<CampCompareResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/camp-compare`, {
    params: roundNo ? { round_no: roundNo } : undefined,
  })
}

/** 获取小队维度分析数据（可按局过滤） */
export async function getSquadAnalysis(scheduleId: number, roundNo?: number): Promise<SquadAnalysisResponse> {
  return http.get(`/schedules/${scheduleId}/match-data/squad-analysis`, {
    params: roundNo ? { round_no: roundNo } : undefined,
  })
}

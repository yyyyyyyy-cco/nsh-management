/** 帮众首页数据亮点：取最近有比赛数据的已结束赛程，复用战报同源组装（仅我方阵营口径）。 */
import dayjs from 'dayjs'

import { getLineup } from '@/api/lineups'
import { getIndicators } from '@/api/matchData'
import { buildReportData } from '@/components/match-data/reportData'
import type { IndicatorsResponse } from '@/types/matchData'
import type { ScheduleInfo } from '@/types/schedule'
import { endedSchedules } from './stats'
import type { HighlightData } from './types'

/** 最多尝试的候选场次（最近已结束的比赛）。 */
const MAX_TRY = 3

/**
 * 依次尝试最近 3 场已结束比赛：第一场存在衍生指标数据即组装亮点。
 * 排表用于判定我方阵营（失败降级为空，兜底取首条记录阵营，与战报一致）；
 * isStale 返回 true（响应过期）时中止并返回 null。
 */
export async function fetchHighlight(
  schedules: ScheduleInfo[],
  isStale: () => boolean,
): Promise<HighlightData | null> {
  for (const s of endedSchedules(schedules).slice(0, MAX_TRY)) {
    let indicators: IndicatorsResponse
    try {
      indicators = await getIndicators(s.id)
    } catch {
      return null // 接口异常（拦截器已提示），不再继续尝试
    }
    if (isStale()) return null
    if (!indicators.items.length) continue
    const lineup = await getLineup(s.id).catch(() => null)
    if (isStale()) return null
    const report = buildReportData(indicators, lineup, s, null)
    return {
      scheduleId: s.id,
      opponent: s.opponent,
      dateText: dayjs(s.match_time).format('M月D日'),
      mvp: report.mvp,
      kings: report.kings,
    }
  }
  return null
}

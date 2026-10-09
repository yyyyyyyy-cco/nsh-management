/** 赛程工具：离今天距离排序与已结束筛选。 */
import dayjs from 'dayjs'

import type { ScheduleInfo } from '@/types/schedule'

/** 已结束（比赛时间已过）的赛程，按时间倒序（首页「已赛场次/历史比赛」统一口径）。 */
export function endedSchedules(schedules: ScheduleInfo[]): ScheduleInfo[] {
  const now = dayjs()
  return schedules
    .filter((s) => !dayjs(s.match_time).isAfter(now))
    .sort((a, b) => dayjs(b.match_time).valueOf() - dayjs(a.match_time).valueOf())
}

/**
 * 按离今天日期的绝对值排序：绝对值小的在前；
 * 绝对值相同时优先今天之后的赛程（如明天排在昨天前）。
 */
export function sortSchedulesByProximity(list: ScheduleInfo[]): ScheduleInfo[] {
  const todayStart = dayjs().startOf('day')
  return [...list].sort((a, b) => {
    const ta = dayjs(a.match_time)
    const tb = dayjs(b.match_time)
    const da = Math.abs(ta.startOf('day').diff(todayStart, 'day'))
    const db = Math.abs(tb.startOf('day').diff(todayStart, 'day'))
    if (da !== db) return da - db
    const futureA = ta.isAfter(todayStart) ? 1 : 0
    const futureB = tb.isAfter(todayStart) ? 1 : 0
    if (futureA !== futureB) return futureB - futureA
    // 同为今天之后按开始时间升序（先开始的在前）；同为今天之前按时间降序（离今天更近的场次在前）
    return futureA ? ta.valueOf() - tb.valueOf() : tb.valueOf() - ta.valueOf()
  })
}

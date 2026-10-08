import dayjs from 'dayjs'
import { describe, expect, it } from 'vitest'

import type { ScheduleInfo } from '@/types/schedule'

import { sortSchedulesByProximity } from './scheduleSort'

/**
 * 用例以「相对今天」构造赛程，故不依赖执行日期（跨天/跨时区运行结果稳定）。
 */
function schedule(offsetDays: number, hour = 20, id = 1): ScheduleInfo {
  const matchTime = dayjs().startOf('day').add(offsetDays, 'day').hour(hour).minute(0).second(0)
  return {
    id,
    guild_id: 1,
    opponent: `对手${id}`,
    match_time: matchTime.format('YYYY-MM-DD HH:mm:ss'),
    location: null,
    rounds: 3,
    result: 'pending',
    round_results: null,
    created_at: matchTime.format('YYYY-MM-DD HH:mm:ss'),
  }
}

describe('sortSchedulesByProximity（离今天越近越前，同距离未来优先）', () => {
  it('按距今天数的绝对值升序', () => {
    const list = [schedule(5, 20, 1), schedule(1, 20, 2), schedule(3, 20, 3)]
    expect(sortSchedulesByProximity(list).map((s) => s.id)).toEqual([2, 3, 1])
  })

  it('距离相同时「今天之后」排在「今天之前」前', () => {
    const list = [schedule(-1, 20, 1), schedule(1, 20, 2)]
    expect(sortSchedulesByProximity(list).map((s) => s.id)).toEqual([2, 1])
  })

  it('同为未来按开始时间升序；同为过去按时间降序', () => {
    const future = [schedule(2, 21, 1), schedule(2, 18, 2)]
    expect(sortSchedulesByProximity(future).map((s) => s.id)).toEqual([2, 1])

    const past = [schedule(-2, 18, 1), schedule(-2, 21, 2)]
    expect(sortSchedulesByProximity(past).map((s) => s.id)).toEqual([2, 1])
  })

  it('今天的赛程排在最前（绝对距离 0）', () => {
    const list = [schedule(1, 20, 1), schedule(0, 9, 2), schedule(-1, 20, 3)]
    expect(sortSchedulesByProximity(list).map((s) => s.id)).toEqual([2, 1, 3])
  })

  it('不修改入参数组（返回副本）', () => {
    const list = [schedule(3, 20, 1), schedule(1, 20, 2)]
    const before = list.map((s) => s.id)
    sortSchedulesByProximity(list)
    expect(list.map((s) => s.id)).toEqual(before)
  })

  it('空数组安全', () => {
    expect(sortSchedulesByProximity([])).toEqual([])
  })
})

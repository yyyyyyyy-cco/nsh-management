import dayjs from 'dayjs'
import { describe, expect, it } from 'vitest'

import type { ScheduleInfo } from '@/types/schedule'

import { RECENT_ROUND_LIMIT, computeGuildStats, recentRoundResults } from './stats'

/** 以「相对今天」构造已结束赛程（daysAgo ≥ 1），避免用例依赖执行日期。 */
function schedule(daysAgo: number, roundResults: string[] | null, id = daysAgo): ScheduleInfo {
  const matchTime = dayjs().startOf('day').subtract(daysAgo, 'day').hour(20).minute(0).second(0)
  return {
    id,
    guild_id: 1,
    opponent: `对手${id}`,
    match_time: matchTime.format('YYYY-MM-DD HH:mm:ss'),
    location: null,
    rounds: roundResults?.length || 3,
    result: 'pending',
    round_results: roundResults,
    created_at: matchTime.format('YYYY-MM-DD HH:mm:ss'),
  }
}

describe('recentRoundResults（最近 N 个已出结果的局）', () => {
  it('跨场次展开：场次由新到旧，同场内先取本场最后一局（后一局更近）', () => {
    const newest = schedule(1, ['lose', 'win', 'win'])
    const older = schedule(8, ['lose', 'lose', 'lose'])
    // 最近 2 局 = 最新场第 3、2 局（win/win）；若误取第 1、2 局会得到 lose/win
    expect(recentRoundResults([newest, older], 2)).toEqual(['win', 'win'])
  })

  it('待定（pending）与空值不计入窗口，窗口未满继续向更旧场次取', () => {
    const newest = schedule(1, ['win', 'pending', 'win'])
    const older = schedule(8, ['draw', '', 'lose'])
    expect(recentRoundResults([newest, older], 4)).toEqual(['win', 'win', 'lose', 'draw'])
  })

  it('到达上限即截断（不继续取更旧场次）；不足上限按实际返回；空输入安全', () => {
    const newest = schedule(1, ['win', 'lose', 'win', 'lose', 'win', 'lose'])
    const older = schedule(8, ['lose'])
    expect(recentRoundResults([newest, older], 4)).toEqual(['lose', 'win', 'lose', 'win'])
    expect(recentRoundResults([newest], RECENT_ROUND_LIMIT)).toHaveLength(6)
    expect(recentRoundResults([], RECENT_ROUND_LIMIT)).toEqual([])
  })
})

describe('computeGuildStats（近 10 局战绩 + 局胜率）', () => {
  it('近 10 局战绩跨场次统计胜/平/负；待定局不计入窗口，已赛场次为全部已结束比赛', () => {
    const schedules = [
      schedule(1, ['win', 'lose', 'draw']),
      schedule(3, ['win', 'win', 'pending']),
      schedule(6, ['lose', 'lose', 'lose']),
    ]
    const stats = computeGuildStats(schedules)
    expect(stats.playedCount).toBe(3)
    // 已出结果的局共 8 个：3 胜 4 负 1 平（pending 不入窗）
    expect(stats.recentRecord).toBe('3胜1平4负')
  })

  it('超过 10 局时只取最近 10 局（边界场次取本场最后一局）', () => {
    const schedules = [
      schedule(1, ['win', 'lose', 'win', 'lose']),
      schedule(5, ['win', 'win', 'win', 'win']),
      // 第三新的场次只贡献最后 2 局（第 4、3 局 = win/win）；若误取前 2 局会多出 2 负
      schedule(9, ['lose', 'lose', 'win', 'win']),
    ]
    expect(computeGuildStats(schedules).recentRecord).toBe('8胜2负')
  })

  it('无任何已出结果的局时战绩为 "-"；无已出结果的局时局胜率为 null', () => {
    const stats = computeGuildStats([schedule(1, ['pending', 'pending', 'pending'])])
    expect(stats.recentRecord).toBe('-')
    expect(stats.roundWinRate).toBeNull()
  })

  it('局胜率保持近 5 场口径，且待定局不计入分母（回归锁定）', () => {
    const schedules = [schedule(1, ['win', 'lose', 'win']), schedule(3, ['lose', 'draw', 'pending'])]
    // 近 5 场已出结果 5 局：2 胜 → 40%（若误把 pending 计入分母会得到 33%）
    expect(computeGuildStats(schedules).roundWinRate).toBe(40)
  })
})

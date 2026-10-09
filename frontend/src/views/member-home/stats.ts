/** 帮众首页纯计算：已赛场次/近期战绩/局胜率与录屏摘要（不依赖组件状态）。 */
import type { Recording, RoundProgress } from '@/types/recording'
import type { ScheduleInfo } from '@/types/schedule'
import { endedSchedules } from '@/utils/scheduleSort'

/** 近 10 局战绩窗口大小（局，跨场次；一场比赛可含多局）。 */
export const RECENT_ROUND_LIMIT = 10

/**
 * 按时间倒序收集「已出结果」的局（win/lose/draw；待定/空值不计入，窗口未满时继续向更旧的场次取）。
 * schedules 须按时间倒序（endedSchedules 输出）；同场内后一局更近，故先取本场最后一局。
 * limit 省略时取入参场次内的全部已出结果局（局胜率口径）。
 */
export function recentRoundResults(schedules: ScheduleInfo[], limit = Number.POSITIVE_INFINITY): string[] {
  const rounds: string[] = []
  for (const s of schedules) {
    const results = s.round_results ?? []
    for (let i = results.length - 1; i >= 0 && rounds.length < limit; i -= 1) {
      const r = results[i]
      if (r === 'win' || r === 'lose' || r === 'draw') rounds.push(r)
    }
    if (rounds.length >= limit) break
  }
  return rounds
}

/** 战绩统计：已赛场次 + 近 10 局战绩（跨场次，胜/平/负）+ 局胜率（近 5 场已出结果的局，待定不计入）。 */
export function computeGuildStats(schedules: ScheduleInfo[]) {
  const ended = endedSchedules(schedules)
  const recent = recentRoundResults(ended, RECENT_ROUND_LIMIT)
  const wins = recent.filter((r) => r === 'win').length
  const loses = recent.filter((r) => r === 'lose').length
  const draws = recent.filter((r) => r === 'draw').length
  const recentRecord = wins + loses + draws === 0 ? '-' : `${wins}胜${draws > 0 ? `${draws}平` : ''}${loses}负`

  const last5 = ended.slice(0, 5)
  const roundResults = recentRoundResults(last5)
  const roundWinRate = roundResults.length
    ? Math.round((roundResults.filter((r) => r === 'win').length / roundResults.length) * 100)
    : null
  return { playedCount: ended.length, recentRecord, roundWinRate }
}

/** 录屏摘要：未交齐（任一局无链接）与被驳回（需重交）成员名单，按录屏列表顺序去重。 */
export function summarizeRecordings(items: Recording[], targetRounds: number) {
  const submitted = new Map<string, number>()
  for (const r of items) {
    submitted.set(r.member_name, (submitted.get(r.member_name) ?? 0) + (r.url ? 1 : 0))
  }
  const missing = [...submitted.entries()].filter(([, n]) => n < targetRounds).map(([name]) => name)
  const rejected = [...new Set(items.filter((r) => r.status === 'rejected').map((r) => r.member_name))]
  return { missing, rejected }
}

/** 已交率（%，已通过 + 待审 / 总；未导入局不计）；无有效局返回 null。 */
export function submittedRate(progress: RoundProgress[]): number | null {
  const active = progress.filter((p) => p.total > 0)
  const total = active.reduce((sum, p) => sum + p.total, 0)
  if (!total) return null
  const submitted = active.reduce((sum, p) => sum + p.approved + p.pending, 0)
  return Math.round((submitted / total) * 100)
}

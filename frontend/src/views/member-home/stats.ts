/** 帮众首页纯计算：已赛场次/近期战绩/局胜率与录屏摘要（不依赖组件状态）。 */
import dayjs from 'dayjs'

import type { Recording, RoundProgress } from '@/types/recording'
import type { ScheduleInfo } from '@/types/schedule'

/** 已结束（比赛时间已过）的赛程，按时间倒序。 */
export function endedSchedules(schedules: ScheduleInfo[]): ScheduleInfo[] {
  const now = dayjs()
  return schedules
    .filter((s) => !dayjs(s.match_time).isAfter(now))
    .sort((a, b) => dayjs(b.match_time).valueOf() - dayjs(a.match_time).valueOf())
}

/** 战绩统计：已赛场次 + 近 5 场战绩（胜/平/负）+ 局胜率（近 5 场已出结果的局）。 */
export function computeGuildStats(schedules: ScheduleInfo[]) {
  const ended = endedSchedules(schedules)
  const last5 = ended.slice(0, 5)
  const wins = last5.filter((s) => s.result === 'win').length
  const loses = last5.filter((s) => s.result === 'lose').length
  const draws = last5.filter((s) => s.result === 'draw').length
  const recentRecord =
    wins + loses + draws === 0 ? '-' : `${wins}胜${draws > 0 ? `${draws}平` : ''}${loses}负`
  const rounds = last5.flatMap((s) => (s.round_results ?? []).filter(Boolean))
  const roundWinRate = rounds.length
    ? Math.round((rounds.filter((r) => r === 'win').length / rounds.length) * 100)
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

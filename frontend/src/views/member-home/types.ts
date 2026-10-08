/** 帮众首页类型：战绩看板、录屏待办与数据亮点。 */
import type { ReportKingItem, ReportMvp } from '@/components/match-data/reportData'

/** 战绩统计（近 5 场口径 + 最近一场录屏）。 */
export interface GuildStats {
  /** 已赛场次（全部已结束比赛） */
  playedCount: number
  /** 近 5 场战绩，如 "3胜1负"；无可判定结果时 "-" */
  recentRecord: string
  /** 近 5 场局胜率（%）；无已出结果的局为 null */
  roundWinRate: number | null
  /** 最近一场录屏已交率（%，已交 = 已通过 + 待审）；无数据为 null */
  recordingRate: number | null
}

/** 录屏待办（赛后 7 天内且存在未交齐/驳回时呈现的一行状态条）。 */
export interface RecordingTodo {
  scheduleId: number
  dateText: string
  /** 未交齐成员名单（任一局无链接即计入） */
  missingNames: string[]
  /** 被驳回需重交的成员名单 */
  rejectedNames: string[]
}

/** 最近一场数据亮点（与「生成战报」同源数据，仅我方阵营口径）。 */
export interface HighlightData {
  scheduleId: number
  opponent: string
  dateText: string
  mvp: ReportMvp | null
  kings: ReportKingItem[]
}

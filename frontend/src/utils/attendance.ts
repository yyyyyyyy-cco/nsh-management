/**
 * 出勤率展示口径（前端**唯一来源**）。
 *
 * 背景（合规化计划 W2-6）：
 * - 出勤率**公式**只在后端实现一次（`backend/app/services/member_service.py`：
 *   `正常 / (正常 + 请假)`，无记录为 `null`），前端只消费接口返回的 `attendance_rate`，
 *   并不存在「公式两版」。
 * - 但前端此前把「低出勤阈值 `0.5`」与「百分比格式化」硬编码在 3 个组件共 7 处，
 *   且存在两种展示口径（`toFixed(1)` 与 `Math.round` 取整）——违反
 *   `AGENTS.md` §2.1「任何值/事实只允许在权威源维护」。
 * - 本模块把阈值与格式化收敛为单一来源，**两种展示口径作为显式参数保留**（非缺陷，是场景差异：
 *   常驻库列表/成员详情需要 1 位小数精度；首页出勤排行的窄栏位取整更易读）。
 */

/** 低出勤告警阈值：低于该值标红并使用 warn 样式。 */
export const ATTENDANCE_LOW_THRESHOLD = 0.5

/** 是否属低出勤（无记录不告警）。 */
export function isLowAttendance(rate: number | null | undefined): boolean {
  return rate != null && rate < ATTENDANCE_LOW_THRESHOLD
}

/** 进度条颜色：低出勤用告警红，否则用 ui-style-guide 雅金主色。 */
export function attendanceProgressColor(rate: number | null | undefined): string {
  return isLowAttendance(rate) ? '#c0392b' : '#c9a13b'
}

/**
 * 出勤率（0~1）→ 百分比文案。
 *
 * @param rate     出勤率；`null` / `undefined` 表示无出勤记录
 * @param digits   小数位。常驻库列表与成员详情用默认 `1`；首页出勤排行窄栏位传 `0`（取整）
 * @param fallback 无记录时的文案（默认 `-`；有的场景在外层用 `v-if` 显示「无记录」）
 */
export function formatRatePercent(rate: number | null | undefined, digits = 1, fallback = '-'): string {
  if (rate == null) return fallback
  return `${(rate * 100).toFixed(digits)}%`
}
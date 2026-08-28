/** 业务常量。 */

/** 11 种职业（v2 §6.1）。 */
export const PROFESSIONS = [
  '铁衣',
  '血河',
  '沧澜',
  '龙吟',
  '潮光',
  '玄机',
  '碎梦',
  '神相',
  '九灵',
  '鸿音',
  '素问',
] as const

/** 成员状态。 */
export const MEMBER_STATUSES = [
  { value: 'formal', label: '正式' },
  { value: 'substitute', label: '替补' },
] as const

/** 比赛结果。 */
export const SCHEDULE_RESULTS = [
  { value: 'pending', label: '待定' },
  { value: 'win', label: '胜' },
  { value: 'lose', label: '负' },
  { value: 'draw', label: '平' },
] as const

/** 赛程结果标签文字 */
export function resultLabel(value: string): string {
  return SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
}

/** 赛程结果 Element Plus tag type */
export function resultType(value: string): '' | 'success' | 'danger' | 'info' {
  return value === 'win' ? 'success' : value === 'lose' ? 'danger' : 'info'
}

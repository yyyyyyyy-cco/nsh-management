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
/**
 * 出勤 / 排表 / 职业配置等页面的**职业展示顺序**（坦克 → 治疗 → 输出的既定展示顺序）。
 *
 * 必须是 `PROFESSIONS` 的一个排列——新增职业时两处都要改，测试会立刻发现（见
 * `professionSource.spec.ts` 与 F-91）。2026-10-03：原先这串顺序单独住在
 * `composables/lineupBoard.ts`，属同一批数据的第二份副本，已上移到本文件统一维护。
 */
export const PROF_ORDER: readonly string[] = [
  '铁衣',
  '素问',
  '神相',
  '碎梦',
  '血河',
  '玄机',
  '九灵',
  '潮光',
  '龙吟',
  '鸿音',
  '沧澜',
]

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

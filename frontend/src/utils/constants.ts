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

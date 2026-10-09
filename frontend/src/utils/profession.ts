/** 职业色映射（依据 ui-style-guide §7「职业色映射（不变）」，全站唯一来源）。 */
export const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800',
  素问: '#FF9CF2',
  神相: '#3E6BF4',
  碎梦: '#00FFFB',
  血河: '#F04545',
  玄机: '#f6ff00',
  九灵: '#8B5CF6',
  潮光: '#4F95FF',
  龙吟: '#3fe155',
  鸿音: '#C6834D',
  沧澜: '#605EF0',
}

/** 深色职业色值（配白字；其余浅色配深字，依据 ui-style-guide §7「文字颜色」列）。 */
const DARK_PROF_COLORS = ['#3E6BF4', '#F04545', '#8B5CF6', '#4F95FF', '#605EF0', '#C6834D']

/** 获取职业对应的 UI 色值，未知职业返回 ui-style-guide 主色 '#c9a13b'。 */
export function profColor(prof: string | null | undefined): string {
  return (prof && PROF_COLORS[prof]) || '#c9a13b'
}

/** 职业标签（胶囊）内联样式：背景取职业色，深色职业配白字、浅色配深字；未知职业用中性灰底。 */
export function profTagStyle(prof: string | null | undefined): { background: string; color: string } {
  const bg = (prof && PROF_COLORS[prof]) || '#e5e7eb'
  return { background: bg, color: DARK_PROF_COLORS.includes(bg) ? '#fff' : '#333' }
}

/** 排表总览「全底色」整格样式：背景取职业色（未知回退主色，与职业圆点口径一致），文字按底色对比。 */
export function profFillStyle(prof: string | null | undefined): { background: string; color: string } {
  const bg = profColor(prof)
  return { background: bg, color: DARK_PROF_COLORS.includes(bg) ? '#fff' : '#333' }
}

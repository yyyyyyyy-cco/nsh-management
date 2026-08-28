/** 职业色映射（依据 ui-style-guide §9，全站统一来源）。 */
export const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

/** 获取职业对应的 UI 色值，未知职业返回 ui-style-guide 主色 '#c9a13b'。 */
export function profColor(prof: string | null | undefined): string {
  return (prof && PROF_COLORS[prof]) || '#c9a13b'
}

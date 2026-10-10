/** 职业色彩工具（全站唯一来源）：色值由 store 加载目录后经 `setProfessionColors` 水合。 */
import { reactive } from 'vue'

/** 职业色缓存：原地更新（保持响应式追踪与对象身份，`analysis.ts` 等再导出断言不受影响）。 */
export const PROF_COLORS = reactive<Record<string, string>>({})

/** 未知职业兜底色（ui-style-guide 主色）。 */
const FALLBACK_COLOR = '#c9a13b'
/** 职业标签未知时的中性灰底。 */
const NEUTRAL_BG = '#e5e7eb'

/**
 * 用职业目录数据水合色彩缓存：原地写入并删除多余键，保持响应式与 `PROF_COLORS` 对象身份。
 * 传入应包含停用职业（历史数据仍需原色显示）。
 */
export function setProfessionColors(next: Record<string, string>): void {
  for (const key of Object.keys(PROF_COLORS)) {
    if (!(key in next)) delete PROF_COLORS[key]
  }
  Object.assign(PROF_COLORS, next)
}

/** 十六进制色 → WCAG 相对亮度（sRGB 线性化）。 */
function relativeLuminance(hex: string): number {
  const value = hex.replace('#', '')
  const channels = [0, 2, 4].map((offset) => parseInt(value.slice(offset, offset + 2), 16) / 255)
  const linear = channels.map((c) => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]
}

/**
 * 底色文字对比色（深底白字 / 浅底深字）：亮度阈值 0.35。
 * 已逐色校准 ui-style-guide §7 的 11 色与两级兜底：深字最小 龙吟 #3fe155 ≈ 0.56、
 * 白字最大 鸿音 #C6834D ≈ 0.29，全部与规范文字颜色一致（见 professionSource.spec.ts）。
 */
function textColorFor(background: string): '#fff' | '#333' {
  return relativeLuminance(background) > 0.35 ? '#333' : '#fff'
}

/** 获取职业对应的 UI 色值，未知职业返回主色 '#c9a13b'。 */
export function profColor(prof: string | null | undefined): string {
  return (prof && PROF_COLORS[prof]) || FALLBACK_COLOR
}

/** 职业标签（胶囊）内联样式：背景取职业色，文字色按亮度自动对比；未知职业用中性灰底。 */
export function profTagStyle(prof: string | null | undefined): { background: string; color: string } {
  const background = (prof && PROF_COLORS[prof]) || NEUTRAL_BG
  return { background, color: textColorFor(background) }
}

/** 排表总览「全底色」整格样式：背景取职业色（未知回退主色），文字按底色对比。 */
export function profFillStyle(prof: string | null | undefined): { background: string; color: string } {
  const background = profColor(prof)
  return { background, color: textColorFor(background) }
}

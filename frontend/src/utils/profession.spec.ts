import { beforeEach, describe, expect, it } from 'vitest'

import { PROF_COLORS, profColor, profFillStyle, profTagStyle, setProfessionColors } from './profession'

const FALLBACK = '#c9a13b'
const NEUTRAL_BG = '#e5e7eb'

/** ui-style-guide §7 全表（色值 + 文字颜色）——作为色彩缓存的水合样本与规范校准。 */
const GUIDE: Record<string, { color: string; text: '#333' | '#fff' }> = {
  铁衣: { color: '#ffc800', text: '#333' },
  素问: { color: '#FF9CF2', text: '#333' },
  神相: { color: '#3E6BF4', text: '#fff' },
  碎梦: { color: '#00FFFB', text: '#333' },
  血河: { color: '#F04545', text: '#fff' },
  玄机: { color: '#f6ff00', text: '#333' },
  九灵: { color: '#8B5CF6', text: '#fff' },
  潮光: { color: '#4F95FF', text: '#fff' },
  龙吟: { color: '#3fe155', text: '#333' },
  鸿音: { color: '#C6834D', text: '#fff' },
  沧澜: { color: '#605EF0', text: '#fff' },
}

beforeEach(() => {
  setProfessionColors(Object.fromEntries(Object.entries(GUIDE).map(([name, spec]) => [name, spec.color])))
})

describe('setProfessionColors / profColor（色彩缓存由目录水合）', () => {
  it('水合后：已知职业返回目录色值', () => {
    expect(profColor('铁衣')).toBe('#ffc800')
    expect(profColor('素问')).toBe('#FF9CF2')
    expect(profColor('神相')).toBe('#3E6BF4')
  })

  it('未知职业 / 空值 一律回退主色', () => {
    for (const value of ['不存在的职业', '', null, undefined]) {
      expect(profColor(value)).toBe(FALLBACK)
    }
  })

  it('水合是原地更新：对象身份不变，且删除不再存在的键', () => {
    const identity = PROF_COLORS
    setProfessionColors({ 铁衣: '#111111' })
    expect(PROF_COLORS).toBe(identity)
    expect(Object.keys(PROF_COLORS)).toEqual(['铁衣'])
    expect(profColor('铁衣')).toBe('#111111')
    expect(profColor('素问')).toBe(FALLBACK)
  })
})

describe('profTagStyle（胶囊内联样式：亮度自动对比）', () => {
  it('阈值 0.35 与规范文字颜色逐色一致', () => {
    for (const [name, spec] of Object.entries(GUIDE)) {
      expect(profTagStyle(name), `${name} 文字颜色`).toEqual({ background: spec.color, color: spec.text })
    }
  })

  it('未知职业使用中性灰底 + 深字', () => {
    expect(profTagStyle(null)).toEqual({ background: NEUTRAL_BG, color: '#333' })
    expect(profTagStyle('不存在的职业')).toEqual({ background: NEUTRAL_BG, color: '#333' })
  })
})

describe('profFillStyle（全底色：职业色铺满整格）', () => {
  it('与胶囊同口径（逐色）', () => {
    for (const [name, spec] of Object.entries(GUIDE)) {
      expect(profFillStyle(name), `${name} 全底色`).toEqual({ background: spec.color, color: spec.text })
    }
  })

  it('未知职业回退主色（与职业圆点一致，非胶囊中性灰）', () => {
    expect(profFillStyle(null)).toEqual({ background: FALLBACK, color: '#333' })
    expect(profFillStyle('不存在的职业')).toEqual({ background: FALLBACK, color: '#333' })
  })
})

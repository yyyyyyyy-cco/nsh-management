import { describe, expect, it } from 'vitest'

import { PROF_COLORS, profColor, profTagStyle } from './profession'

const FALLBACK = '#c9a13b'
const NEUTRAL_BG = '#e5e7eb'

describe('profColor（未知职业回退主色）', () => {
  it('已知职业返回 ui-style-guide §7 规定色', () => {
    expect(profColor('铁衣')).toBe('#ffc800')
    expect(profColor('素问')).toBe('#FF9CF2')
    expect(profColor('神相')).toBe('#3E6BF4')
  })

  it('未知职业 / 空值 一律回退主色', () => {
    for (const value of ['不存在的职业', '', null, undefined]) {
      expect(profColor(value)).toBe(FALLBACK)
    }
  })

  it('色表覆盖 11 种职业（与 utils/constants 的 PROFESSIONS 数量一致）', () => {
    expect(Object.keys(PROF_COLORS)).toHaveLength(11)
  })
})

describe('profTagStyle（胶囊内联样式：深底白字 / 浅底深字）', () => {
  it('深色职业配白字', () => {
    expect(profTagStyle('神相')).toEqual({ background: '#3E6BF4', color: '#fff' })
    expect(profTagStyle('血河')).toEqual({ background: '#F04545', color: '#fff' })
  })

  it('浅色职业配深字', () => {
    expect(profTagStyle('素问')).toEqual({ background: '#FF9CF2', color: '#333' })
    expect(profTagStyle('铁衣')).toEqual({ background: '#ffc800', color: '#333' })
  })

  it('未知职业使用中性灰底 + 深字', () => {
    expect(profTagStyle(null)).toEqual({ background: NEUTRAL_BG, color: '#333' })
    expect(profTagStyle('不存在的职业')).toEqual({ background: NEUTRAL_BG, color: '#333' })
  })
})
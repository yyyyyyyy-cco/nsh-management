/**
 * 职业色与职业清单的「权威源锁定」测试（F-90）。
 *
 * 权威源：`memory-bank/ui-style-guide.md §7 职业色映射（不变）`（色值 + 文字颜色）；
 * 职业清单权威源：`backend/app/utils/constants.py` 的 PROFESSIONS（11 种，顺序一致）。
 *
 * 同时锁定单一来源：`components/match-data/analysis.ts` 必须**转出** `utils/profession.ts` 的色表，
 * 不得再复制一份（本轮 F-90 修复前它就复制了一份，改色时容易漏改）。
 */
import { describe, expect, it } from 'vitest'
import { PROFESSIONS, PROF_ORDER } from './constants'
import { PROF_COLORS, profColor, profTagStyle } from './profession'
import { PROF_COLORS as ANALYSIS_COLORS } from '../components/match-data/analysis'
import { PROF_ORDER as LINEUP_BOARD_PROF_ORDER } from '../composables/lineupBoard'
import { TANK_PROFESSIONS } from '../components/match-data/professionDetailCharts'

/** ui-style-guide §7 全表：职业 → 色值 + 文字颜色 */
const GUIDE: Record<string, { color: string; text: string }> = {
  铁衣: { color: '#ffc800', text: '#333' },
  素问: { color: '#FF9CF2', text: '#333' },
  神相: { color: '#3E6BF4', text: '#fff' },
  碎梦: { color: '#00FFFB', text: '#333' },
  血河: { color: '#F04545', text: '#fff' },
  沧澜: { color: '#605EF0', text: '#fff' },
  玄机: { color: '#f6ff00', text: '#333' },
  九灵: { color: '#8B5CF6', text: '#fff' },
  潮光: { color: '#4F95FF', text: '#fff' },
  龙吟: { color: '#3fe155', text: '#333' },
  鸿音: { color: '#C6834D', text: '#fff' },
}

/** 后端 PROFESSIONS 的顺序（与 backend/app/utils/constants.py 一致） */
const EXPECTED_PROFESSIONS = [
  '铁衣', '血河', '沧澜', '龙吟', '潮光', '玄机', '碎梦', '神相', '九灵', '鸿音', '素问',
]

describe('职业清单与后端一致', () => {
  it('11 种且顺序与后端一致', () => {
    expect(PROFESSIONS).toEqual(EXPECTED_PROFESSIONS)
  })

  it('色表覆盖全部职业（无缺漏、无多余）', () => {
    expect(Object.keys(PROF_COLORS).sort()).toEqual([...EXPECTED_PROFESSIONS].sort())
  })
})

describe('职业色对齐 ui-style-guide §7', () => {
  it('每个职业的色值与规范完全一致', () => {
    for (const [prof, spec] of Object.entries(GUIDE)) {
      expect(PROF_COLORS[prof], `${prof} 色值`).toBe(spec.color)
    }
  })

  it('每个职业的文字颜色与规范一致（深色配白字、浅色配深字）', () => {
    for (const [prof, spec] of Object.entries(GUIDE)) {
      expect(profTagStyle(prof).color, `${prof} 文字颜色`).toBe(spec.text)
    }
  })

  it('未知职业回退规范主色 #c9a13b', () => {
    expect(profColor('不存在的职业')).toBe('#c9a13b')
    expect(profColor(null)).toBe('#c9a13b')
  })
})

describe('职业色单一来源（F-90）', () => {
  it('analysis 模块转出的是同一份色表（不是复制）', () => {
    expect(ANALYSIS_COLORS).toBe(PROF_COLORS)
  })
})

describe('职业清单展示顺序与分类单一来源（F-91）', () => {
  it('PROF_ORDER 是 PROFESSIONS 的一个排列（不漏不重）', () => {
    expect(PROF_ORDER).toHaveLength(EXPECTED_PROFESSIONS.length)
    expect(new Set(PROF_ORDER)).toEqual(new Set(EXPECTED_PROFESSIONS))
  })

  it('PROF_ORDER 由 utils/constants 单一定义，lineupBoard 只转出', () => {
    expect(LINEUP_BOARD_PROF_ORDER).toBe(PROF_ORDER)
  })

  it('承伤职业集合与图表使用的一致（且已补记进数据分析规格）', () => {
    expect([...TANK_PROFESSIONS]).toEqual(['铁衣', '血河', '沧澜', '素问'])
  })
})
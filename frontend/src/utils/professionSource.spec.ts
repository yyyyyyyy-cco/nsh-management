/**
 * 职业色彩与分类的「权威源锁定」测试。
 *
 * 背景（2026-10 职业目录动态化）：职业清单与色值的权威源迁至数据库目录
 * （后端 `PROFESSIONS` 常量与前端静态色表已删除；清单维护见
 * `.agent/plans/profession-catalog-plan.md`）。ui-style-guide §7 的 11 色作为
 * **初始种子色板**由迁移 `q1r2s3t4u5v6` 写入目录，本文件据此校准色彩工具与种子等价。
 *
 * 同时锁定单一来源：`components/match-data/analysis.ts` 必须**转出**
 * `utils/profession.ts` 的色表，不得复制第二份（F-90）。
 */
import { beforeEach, describe, expect, it } from 'vitest'

import { PROF_COLORS, profColor, setProfessionColors } from './profession'
import { PROF_COLORS as ANALYSIS_COLORS } from '../components/match-data/analysis'
import { TANK_PROFESSIONS } from '../components/match-data/professionDetailCharts'

/** ui-style-guide §7 全表（= 迁移种子色板）：职业 → 色值 + 文字颜色 */
const GUIDE: Record<string, { color: string; text: string }> = {
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

describe('初始种子色板与 ui-style-guide §7 一致（目录动态化后作为校准基线）', () => {
  it('11 种职业色逐条对齐（水合后）', () => {
    for (const [prof, spec] of Object.entries(GUIDE)) {
      expect(profColor(prof), `${prof} 色值`).toBe(spec.color)
    }
  })

  it('色表键与种子职业一一对应', () => {
    expect(Object.keys(PROF_COLORS).sort()).toEqual(Object.keys(GUIDE).sort())
  })
})

describe('职业色单一来源（F-90）', () => {
  it('analysis 模块转出的是同一份色表（不是复制）', () => {
    expect(ANALYSIS_COLORS).toBe(PROF_COLORS)
  })
})

describe('职业分类补记（承伤职业集合，见 data-analysis-complete.md）', () => {
  it('承伤职业集合与图表使用的一致（且已补记进数据分析规格）', () => {
    expect([...TANK_PROFESSIONS]).toEqual(['铁衣', '血河', '沧澜', '素问'])
  })
})

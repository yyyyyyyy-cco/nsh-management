import { describe, expect, it } from 'vitest'

import type { MatchData } from '@/types/matchData'

import { calcKDA, computeScores, fmtNum, pctStr, resolveArchetype } from './analysis'

/**
 * 比赛记录工厂：只覆盖用例关心的字段，其余取零值。
 * 注意默认 `profession: '铁衣'`（属**辅助型**，KDA 会折算助攻/死亡）——
 * 需要非辅助语义的用例必须显式覆盖 profession（本轮曾因此写错两条用例）。
 */
function rec(over: Partial<MatchData> = {}): MatchData {
  return {
    id: 1,
    schedule_id: 1,
    round_no: 1,
    player_name: '甲',
    profession: '铁衣',
    camp: '红',
    kills: 0,
    springs: 0,
    assists: 0,
    resource: 0,
    player_damage: 0,
    armor_break_damage: 0,
    building_damage: 0,
    tower_break_damage: 0,
    healing: 0,
    damage_taken: 0,
    deaths: 0,
    revives: 0,
    fen_gu: 0,
    created_at: '2026-01-01T00:00:00Z',
    ...over,
  }
}

describe('fmtNum（万位折算）', () => {
  it('小于 1 万走千分位', () => {
    // toLocaleString 的分组符号随运行环境 locale 变化（, 或窄空格），故用宽松匹配
    expect(fmtNum(9999)).toMatch(/^9[,\s\u00a0]?999$/)
    expect(fmtNum(0)).toBe('0')
  })

  it('达到 1 万折算为「万」保留 1 位小数', () => {
    expect(fmtNum(10000)).toBe('1.0万')
    expect(fmtNum(123456)).toBe('12.3万')
  })
})

describe('pctStr（占比字符串）', () => {
  it('常规占比保留 1 位小数', () => {
    expect(pctStr(1, 4)).toBe('25.0%')
    expect(pctStr(1, 3)).toBe('33.3%')
  })

  it('总数为 0 时返回 0% 且不产生 NaN/Infinity', () => {
    expect(pctStr(5, 0)).toBe('0%')
    expect(pctStr(0, 0)).toBe('0%')
  })
})

describe('calcKDA（辅助型玩家折算）', () => {
  it('非辅助：(击杀+助攻)/死亡', () => {
    const dps = rec({ profession: '血河', kills: 10, assists: 6, deaths: 2, player_damage: 999, healing: 0 })
    expect(calcKDA(dps)).toBeCloseTo(8, 5)
  })

  it('非辅助且死亡为 0 时分母取下限 1（避免除零）', () => {
    expect(calcKDA(rec({ profession: '血河', kills: 10, assists: 6, deaths: 0, player_damage: 999 }))).toBeCloseTo(16, 5)
  })

  it('铁衣恒按辅助折算（助攻 ×0.8、死亡 ×1.2）', () => {
    expect(calcKDA(rec({ profession: '铁衣', kills: 2, assists: 10, deaths: 5, player_damage: 1000 }))).toBeCloseTo(
      10 / 6,
      5,
    )
  })

  it('治疗量高于伤害量时按辅助折算', () => {
    const support = rec({ profession: '素问', kills: 1, assists: 10, deaths: 4, healing: 100, player_damage: 50 })
    expect(calcKDA(support)).toBeCloseTo(9 / 4.8, 5)
  })
})

describe('resolveArchetype（职业分路判定）', () => {
  it('潮光按 建筑 vs 人伤 拆分路', () => {
    expect(resolveArchetype(rec({ profession: '潮光', building_damage: 1000, player_damage: 500 }))).toBe('潮光·拆塔')
    expect(resolveArchetype(rec({ profession: '潮光', building_damage: 100, player_damage: 1000 }))).toBe('潮光·输出')
  })

  it('潮光的人伤含卸甲、建筑含破塔折算（权重 0.7）', () => {
    // 建筑 = 0 + 2000×0.7 = 1400 ≥ 人伤 1000 → 拆塔
    expect(resolveArchetype(rec({ profession: '潮光', tower_break_damage: 2000, player_damage: 1000 }))).toBe(
      '潮光·拆塔',
    )
    // 人伤 = 500 + 800 = 1300 > 建筑 0 → 输出
    expect(resolveArchetype(rec({ profession: '潮光', armor_break_damage: 800, player_damage: 500 }))).toBe('潮光·输出')
  })

  it('鸿音按 治疗 vs 建筑 拆分路', () => {
    expect(resolveArchetype(rec({ profession: '鸿音', healing: 900, building_damage: 100 }))).toBe('鸿音·治疗')
    expect(resolveArchetype(rec({ profession: '鸿音', healing: 0, building_damage: 100 }))).toBe('鸿音·拆塔')
  })

  it('其余职业即分路本身；职业为空记为未知', () => {
    expect(resolveArchetype(rec({ profession: '素问' }))).toBe('素问')
    expect(resolveArchetype(rec({ profession: null }))).toBe('未知')
  })
})

describe('computeScores（综合评分的不变量）', () => {
  it('空输入返回空数组', () => {
    expect(computeScores([])).toEqual([])
  })

  it('单条记录有死亡：各项倍数均为 1 → 100 分权重分 − 15 分重伤惩罚 = 85', () => {
    const only = rec({ profession: '素问', assists: 5, healing: 1000, damage_taken: 500, revives: 1, deaths: 3 })
    const [score] = computeScores([only])
    expect(score.archetype).toBe('素问')
    expect(score.deathMult).toBeCloseTo(1, 5) // 组内死亡均值即自身
    expect(score.deathPts).toBeCloseTo(15, 5)
    expect(score.total).toBe(85)
    expect(score.kda).toBeTypeOf('number')
  })

  it('无死亡时不扣分（deathMult = 0 而非 1，避免「零死亡反被惩罚」）', () => {
    const only = rec({ profession: '素问', assists: 5, healing: 1000, damage_taken: 500, revives: 1 })
    const [score] = computeScores([only])
    expect(score.deathMult).toBe(0)
    expect(score.deathPts).toBe(0)
    expect(score.total).toBe(100)
  })

  it('该分路全部正权重指标为 0（且无死亡）时得 0 分，权重项为空', () => {
    const [score] = computeScores([rec({ profession: '素问' })])
    expect(score.breakdown).toEqual([])
    expect(score.total).toBe(0)
  })

  it('同分路内指标全面更优者得分更高（不锁定具体数值）', () => {
    const strong = rec({
      player_name: '强',
      profession: '素问',
      assists: 12,
      healing: 3000,
      damage_taken: 1200,
      revives: 2,
    })
    const weak = rec({ player_name: '弱', profession: '素问', assists: 2, healing: 400, damage_taken: 200, revives: 0 })
    const scores = computeScores([weak, strong])
    expect(scores[0].player.player_name).toBe('强')
    expect(scores[0].total).toBeGreaterThan(scores[1].total)
  })

  it('按职业分路分组（同名职业不同分路各自成组）', () => {
    const tower = rec({ player_name: '拆塔', profession: '潮光', building_damage: 2000 })
    const dps = rec({ player_name: '输出', profession: '潮光', player_damage: 2000 })
    const archetypes = computeScores([tower, dps]).map((s) => s.archetype)
    expect(new Set(archetypes)).toEqual(new Set(['潮光·拆塔', '潮光·输出']))
  })

  it('返回条数等于入参条数、total 降序、breakdown 与权重口径自洽', () => {
    const items = [
      rec({ player_name: 'A', profession: '血河', kills: 20, assists: 8, deaths: 1, player_damage: 5000 }),
      rec({ player_name: 'B', profession: '血河', kills: 2, assists: 4, deaths: 6, player_damage: 900 }),
      rec({ player_name: 'C', profession: '血河', kills: 9, assists: 6, deaths: 3, player_damage: 2600 }),
    ]
    const scores = computeScores(items)
    expect(scores).toHaveLength(3)
    expect(scores.map((s) => s.total)).toEqual([...scores.map((s) => s.total)].sort((a, b) => b - a))
    for (const s of scores) {
      // 有效权重之和为 1（内部按 wsum 归一化）
      const weightSum = s.breakdown.reduce((acc, b) => acc + b.weight, 0)
      expect(weightSum).toBeCloseTo(1, 6)
      expect(s.deathPts).toBeCloseTo(15 * s.deathMult, 6)
    }
  })

  it('不修改入参数组及其顺序', () => {
    const items = [rec({ player_name: '弱', kills: 1 }), rec({ player_name: '强', kills: 50 })]
    const before = items.map((r) => r.player_name)
    computeScores(items)
    expect(items.map((r) => r.player_name)).toEqual(before)
  })

  it('同一数组引用命中缓存（返回同一结果对象）', () => {
    const items = [rec({ player_name: 'A', profession: '血河', kills: 5 })]
    expect(computeScores(items)).toBe(computeScores(items))
  })
})
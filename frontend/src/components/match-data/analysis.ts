/** 数据分析计算工具 - 基于实际数据优化版 */
import type { MatchData } from '@/types/matchData'

// 职业色映射：唯一来源是 `@/utils/profession`（依据 ui-style-guide §7）。
// 2026-10-03（F-90）：本文件原先**复制**了一份同样的 11 色，改色时容易漏改一处；现改为引用并转出，
// 既有 `import { PROF_COLORS } from './analysis'` 的调用方无需改动。
import { PROF_COLORS } from '@/utils/profession'

export { PROF_COLORS }

/** 阵营颜色（图表系列用）。 */
export const CAMP_COLORS = ['#c9a13b', '#5b7a9d', '#c0392b', '#2e8b57']

export function profColor(prof: string | null | undefined): string {
  return (prof && PROF_COLORS[prof]) || '#999'
}

/** 大数格式化（万）。 */
export function fmtNum(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return n.toLocaleString()
}

/**
 * KDA = (击杀 + 助攻) / 死亡（重伤）。
 * 辅助型玩家（治疗职业：治疗量 > 伤害量；或坦克职业铁衣）
 * 的助攻按 ×0.8 折算、死亡按 ×1.2 加重。
 */
export function calcKDA(p: MatchData): number {
  const isSupport = p.healing > p.player_damage || p.profession === '铁衣'
  const assists = isSupport ? p.assists * 0.8 : p.assists
  const deaths = isSupport ? p.deaths * 1.2 : p.deaths
  return (p.kills + assists) / Math.max(deaths, 1)
}

/** 占比字符串。 */
export function pctStr(part: number, total: number): string {
  if (!total) return '0%'
  return ((part / total) * 100).toFixed(1) + '%'
}

// ==================== 综合评分（贡献倍数法） ====================
/**
 * 计分口径（基于 1440 条历史数据分析推导，见 backend/scripts/sim_contribution_v4_20260907.py）：
 * - 评分 = Σ 权重×(个人指标 ÷ 本轮同职业分路均值)×100 − 15×(个人重伤 ÷ 本轮同职业均值重伤)
 * - 100 分 = 达到本轮同职业(分路)平均贡献水平；扣除重伤惩罚后的期望基准为 85
 * - 权重按 rs（该职业指标均值 ÷ 全体均值）规则推导：rs≥1.5 核心（85% 份额，按 rs 占比）、
 *   1.0≤rs<1.5 次要（15% 份额均分）、rs<1 且均值>0 边际 0.05；复活/焚骨稀缺指标核心权重 cap 0.30
 */

/** 破塔卸甲折算系数（实测鸿音卸甲玩家 卸甲/直接建筑 ≈ 0.68） */
export const TOWER_BREAK_WEIGHT = 0.7

/** 重伤负向权重：每高出同职业均值 1 倍扣 15 分 */
export const DEATH_PENALTY = 15

/** 边际项倍数封顶：防止小均值指标（如沧澜治疗）倍数爆炸 */
export const MARGINAL_MULT_CAP = 2

/** 有效权重低于该阈值的项视为边际项（应用倍数封顶） */
const MARGINAL_WEIGHT_THRESHOLD = 0.06

/** 计分指标 */
export type ScoreMetric = '击杀' | '助攻' | '人伤' | '建筑' | '治疗' | '承伤' | '复活' | '焚骨'

export const SCORE_METRICS: ScoreMetric[] = ['击杀', '助攻', '人伤', '建筑', '治疗', '承伤', '复活', '焚骨']

const METRIC_GETTERS: Record<ScoreMetric, (r: MatchData) => number> = {
  击杀: (r) => r.kills,
  助攻: (r) => r.assists,
  人伤: (r) => r.player_damage + r.armor_break_damage,
  建筑: (r) => r.building_damage + r.tower_break_damage * TOWER_BREAK_WEIGHT,
  治疗: (r) => r.healing,
  承伤: (r) => r.damage_taken,
  复活: (r) => r.revives,
  焚骨: (r) => r.fen_gu,
}

/** 职业分路：潮光/鸿音按当轮自身数据判定，其余职业即分路本身 */
export function resolveArchetype(p: MatchData): string {
  const building = METRIC_GETTERS.建筑(p)
  const damage = METRIC_GETTERS.人伤(p)
  if (p.profession === '潮光') return building >= damage ? '潮光·拆塔' : '潮光·输出'
  if (p.profession === '鸿音') return p.healing > building ? '鸿音·治疗' : '鸿音·拆塔'
  return p.profession || '未知'
}

/** 各职业(分路)指标权重（正向和 = 1.0），由数据推导脚本生成，可按需手工微调 */
export const PROFESSION_WEIGHTS: Record<string, Record<ScoreMetric, number>> = {
  素问: { 击杀: 0, 助攻: 0.1111, 人伤: 0, 建筑: 0, 治疗: 0.6296, 承伤: 0.037, 复活: 0.2222, 焚骨: 0 },
  '鸿音·治疗': { 击杀: 0, 助攻: 0.1836, 人伤: 0, 建筑: 0, 治疗: 0.4703, 承伤: 0.1154, 复活: 0.2308, 焚骨: 0 },
  '鸿音·拆塔': { 击杀: 0.0435, 助攻: 0.0435, 人伤: 0.1304, 建筑: 0.7391, 治疗: 0, 承伤: 0.0435, 复活: 0, 焚骨: 0 },
  // 铁衣：人伤/建筑为手工指定的边际项（OVERRIDE，承伤时打出的伤害与拆塔参与应获认可）
  铁衣: { 击杀: 0, 助攻: 0.1364, 人伤: 0.0455, 建筑: 0.0455, 治疗: 0, 承伤: 0.7727, 复活: 0, 焚骨: 0 },
  // 沧澜/龙吟：助攻为手工指定的边际项（OVERRIDE，rs 0.47 差一点过门槛且非零占比 100%）
  沧澜: { 击杀: 0.0435, 助攻: 0.0435, 人伤: 0.0435, 建筑: 0.7391, 治疗: 0, 承伤: 0.1304, 复活: 0, 焚骨: 0 },
  龙吟: { 击杀: 0.0435, 助攻: 0.0435, 人伤: 0.0435, 建筑: 0.7391, 治疗: 0, 承伤: 0.1304, 复活: 0, 焚骨: 0 },
  神相: { 击杀: 0.3862, 助攻: 0.1429, 人伤: 0.4233, 建筑: 0, 治疗: 0, 承伤: 0.0476, 复活: 0, 焚骨: 0 },
  血河: { 击杀: 0.4391, 助攻: 0.0526, 人伤: 0.4556, 建筑: 0, 治疗: 0, 承伤: 0.0526, 复活: 0, 焚骨: 0 },
  九灵: { 击杀: 0.3082, 助攻: 0.1111, 人伤: 0.3214, 建筑: 0, 治疗: 0, 承伤: 0.037, 复活: 0, 焚骨: 0.2222 },
  // 玄机：建筑为手工指定的边际项（OVERRIDE，玄机也参与拆塔）
  玄机: { 击杀: 0.7727, 助攻: 0.0455, 人伤: 0.1364, 建筑: 0.0455, 治疗: 0, 承伤: 0, 复活: 0, 焚骨: 0 },
  碎梦: { 击杀: 0.7727, 助攻: 0.0455, 人伤: 0.1364, 建筑: 0, 治疗: 0, 承伤: 0.0455, 复活: 0, 焚骨: 0 },
  // 潮光·拆塔：击杀/助攻为手工指定的边际项（OVERRIDE，与沧澜/龙吟同理）
  '潮光·拆塔': { 击杀: 0.037, 助攻: 0.037, 人伤: 0.037, 建筑: 0.6296, 治疗: 0, 承伤: 0.037, 复活: 0.2222, 焚骨: 0 },
  '潮光·输出': { 击杀: 0.2469, 助攻: 0.2469, 人伤: 0.2469, 建筑: 0, 治疗: 0, 承伤: 0.037, 复活: 0.2222, 焚骨: 0 },
}

/** 未知职业兜底：击杀/人伤各半 */
const FALLBACK_WEIGHTS: Record<ScoreMetric, number> = {
  击杀: 0.5, 助攻: 0, 人伤: 0.5, 建筑: 0, 治疗: 0, 承伤: 0, 复活: 0, 焚骨: 0,
}

// ==================== 评分计算 ====================

export interface ScorePart {
  metric: ScoreMetric
  mult: number     // 贡献倍数（个人值 ÷ 同职业分路均值）
  weight: number   // 有效权重（轮内可用项归一化后）
  points: number   // 该项得分贡献 = 权重×倍数×100
}

export interface PlayerScore {
  player: MatchData
  archetype: string   // 职业(分路)
  total: number       // 综合评分，100 = 本轮同职业(分路)平均贡献水平
  deathMult: number   // 重伤倍数（个人重伤 ÷ 同职业均值重伤）
  deathPts: number    // 重伤扣分 = 15 × 重伤倍数
  metrics: Record<ScoreMetric, number>  // 各指标贡献倍数（雷达图用，无数据/无权重为 0）
  breakdown: ScorePart[]                // 得分分解（仅含计分项）
  kda: number
}

/**
 * 综合评分（贡献倍数法）
 * 1. 按职业(分路)分组，组内求各指标均值
 * 2. 评分 = Σ 权重×(个人值÷组均值)×100 − 15×(重伤÷组均值重伤)
 * 3. 组内某指标均值恰为 0 时，该项权重按比例摊给其余指标（保证基准恒为 100）
 *
 * 以 items 数组引用为 key 做 WeakMap 缓存：同一轮渲染中多个 computed
 * （ScoreTab / PlayerAnalysis）对同一份数据只计算一次；筛选/切局产生新数组引用时自动失效。
 */
const scoreCache = new WeakMap<MatchData[], PlayerScore[]>()

export function computeScores(items: MatchData[]): PlayerScore[] {
  if (!items.length) return []
  const cached = scoreCache.get(items)
  if (cached) return cached

  // 按职业(分路)分组
  const groups = new Map<string, MatchData[]>()
  for (const p of items) {
    const arch = resolveArchetype(p)
    const arr = groups.get(arch)
    if (arr) arr.push(p)
    else groups.set(arch, [p])
  }

  const out: PlayerScore[] = []
  for (const [arch, grp] of groups) {
    const weights = PROFESSION_WEIGHTS[arch] ?? FALLBACK_WEIGHTS
    // 组内各指标均值（均值恰为 0 的指标本轮不可用，权重摊给其余项）
    const means = new Map<ScoreMetric, number>()
    let wsum = 0
    for (const m of SCORE_METRICS) {
      if (weights[m] <= 0) continue
      const mean = grp.reduce((s, r) => s + METRIC_GETTERS[m](r), 0) / grp.length
      if (mean > 0) {
        means.set(m, mean)
        wsum += weights[m]
      }
    }
    const active = [...means.keys()]
    const deathMean = grp.reduce((s, r) => s + r.deaths, 0) / grp.length || 1

    for (const p of grp) {
      const metrics = {} as Record<ScoreMetric, number>
      const breakdown: ScorePart[] = []
      let total = 0
      for (const m of active) {
        let mult = METRIC_GETTERS[m](p) / means.get(m)!
        // 边际项（有效权重低于阈值）倍数封顶，防止小均值指标倍数爆炸
        if (weights[m] < MARGINAL_WEIGHT_THRESHOLD && mult > MARGINAL_MULT_CAP) mult = MARGINAL_MULT_CAP
        const weight = weights[m] / wsum
        const points = weight * mult * 100
        metrics[m] = mult
        breakdown.push({ metric: m, mult, weight, points })
        total += points
      }
      for (const m of SCORE_METRICS) if (!(m in metrics)) metrics[m] = 0
      const deathMult = p.deaths / deathMean
      const deathPts = DEATH_PENALTY * deathMult
      total -= deathPts
      out.push({ player: p, archetype: arch, total: Math.round(total), deathMult, deathPts, metrics, breakdown, kda: calcKDA(p) })
    }
  }

  const result = out.sort((a, b) => b.total - a.total)
  scoreCache.set(items, result)
  return result
}

export interface CampAgg {
  camp: string
  count: number
  kills: number
  assists: number
  player_damage: number
  building_damage: number
  healing: number
  damage_taken: number
  deaths: number
  revives: number
  fen_gu: number
}

/** 按阵营聚合战斗数据（以 items 引用为 key 缓存，多组件复用同一份数据只算一次）。 */
const campsCache = new WeakMap<MatchData[], CampAgg[]>()

export function aggregateCamps(items: MatchData[]): CampAgg[] {
  const cached = campsCache.get(items)
  if (cached) return cached
  const map = new Map<string, CampAgg>()
  for (const r of items) {
    const c = map.get(r.camp) ?? {
      camp: r.camp, count: 0, kills: 0, assists: 0, player_damage: 0,
      building_damage: 0, healing: 0, damage_taken: 0, deaths: 0, revives: 0, fen_gu: 0,
    }
    c.count += 1
    c.kills += r.kills
    c.assists += r.assists
    c.player_damage += r.player_damage
    c.building_damage += r.building_damage
    c.healing += r.healing
    c.damage_taken += r.damage_taken
    c.deaths += r.deaths
    c.revives += r.revives
    c.fen_gu += r.fen_gu
    map.set(r.camp, c)
  }
  const result = [...map.values()]
  campsCache.set(items, result)
  return result
}

export interface ProfAgg {
  profession: string
  count: number
  total_kills: number
  total_player_damage: number
  total_building_damage: number
  total_healing: number
  total_damage_taken: number
  total_fen_gu: number
  avg_kills: number
  avg_player_damage: number
  avg_healing: number
  kills_pct: number
  damage_pct: number
  healing_pct: number
}

/** 按职业聚合（支持阵营筛选）。 */
export function aggregateProfessions(items: MatchData[], camp?: string): ProfAgg[] {
  const list = camp ? items.filter((r) => r.camp === camp) : items
  const map = new Map<string, ProfAgg>()
  for (const r of list) {
    const prof = r.profession || '未知'
    const p = map.get(prof) ?? {
      profession: prof, count: 0, total_kills: 0, total_player_damage: 0,
      total_building_damage: 0, total_healing: 0, total_damage_taken: 0, total_fen_gu: 0,
      avg_kills: 0, avg_player_damage: 0, avg_healing: 0, kills_pct: 0, damage_pct: 0, healing_pct: 0,
    }
    p.count += 1
    p.total_kills += r.kills
    p.total_player_damage += r.player_damage
    p.total_building_damage += r.building_damage
    p.total_healing += r.healing
    p.total_damage_taken += r.damage_taken
    p.total_fen_gu += r.fen_gu
    map.set(prof, p)
  }
  const totalKills = list.reduce((s, r) => s + r.kills, 0)
  const totalDmg = list.reduce((s, r) => s + r.player_damage, 0)
  const totalHeal = list.reduce((s, r) => s + r.healing, 0)
  return [...map.values()].map((p) => ({
    ...p,
    avg_kills: p.count ? +(p.total_kills / p.count).toFixed(1) : 0,
    avg_player_damage: p.count ? Math.round(p.total_player_damage / p.count) : 0,
    avg_healing: p.count ? Math.round(p.total_healing / p.count) : 0,
    kills_pct: totalKills ? (p.total_kills / totalKills) * 100 : 0,
    damage_pct: totalDmg ? (p.total_player_damage / totalDmg) * 100 : 0,
    healing_pct: totalHeal ? (p.total_healing / totalHeal) * 100 : 0,
  }))
}

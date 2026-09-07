/** 数据分析计算工具 - 基于实际数据优化版 */
import type { MatchData } from '@/types/matchData'

/** 职业色映射（依据 ui-style-guide）。 */
export const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

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

// ==================== 职业判定系统 ====================

/** 职业类型 */
export type RoleType = 'healer' | 'tank' | 'tower' | 'fighter'

/** 职业类型配置 */
export const ROLE_CONFIG: Record<RoleType, { name: string; icon: string; color: string }> = {
  healer: { name: '治疗职业', icon: '💚', color: '#52c41a' },
  tank: { name: '承伤职业', icon: '🛡️', color: '#faad14' },
  tower: { name: '进攻职业', icon: '🏗️', color: '#1890ff' },
  fighter: { name: '防守职业', icon: '⚔️', color: '#f5222d' },
}

/** 职业判定阈值 */
const ROLE_THRESHOLD = 1

/**
 * 根据玩家数据判定职业类型
 * 基于240条实际数据分析，使用平均值倍数判定
 */
export function detectRole(p: MatchData, avg: { damage: number; building: number; healing: number; taken: number }): RoleType {
  const healingRatio = avg.healing > 0 ? p.healing / avg.healing : 0
  const buildingRatio = avg.building > 0 ? (p.building_damage + p.tower_break_damage) / avg.building : 0
  const damageRatio = avg.damage > 0 ? (p.player_damage + p.armor_break_damage) / avg.damage : 0
  
  // 判定优先级：治疗 > 进攻 > 防守 > 承伤（默认）
  if (healingRatio >= ROLE_THRESHOLD) return 'healer'
  if (buildingRatio >= ROLE_THRESHOLD) return 'tower'
  if (damageRatio >= ROLE_THRESHOLD) return 'fighter'
  return 'tank'
}

// ==================== 评分权重配置 ====================

/** 评分权重配置（基于240条实际数据分析） */
export const SCORE_WEIGHTS: Record<RoleType, { output: number; building: number; healing: number; survival: number; special: number }> = {
  // 治疗职业：治疗为主，承伤为辅
  healer: { output: 0, building: 0, healing: 0.50, survival: 0.30, special: 0.20 },
  // 承伤职业：承伤为主，其他低权重
  tank: { output: 0.05, building: 0.05, healing: 0.05, survival: 0.75, special: 0.10 },
  // 进攻职业：建筑为主，承伤为辅
  tower: { output: 0.10, building: 0.60, healing: 0, survival: 0.25, special: 0.05 },
  // 防守职业：输出为主，承伤为辅
  fighter: { output: 0.75, building: 0.05, healing: 0, survival: 0.10, special: 0.10 },
}

/** 输出维度权重（基于变异系数分析） */
export const OUTPUT_WEIGHTS = {
  kills: 0.35,    // 击杀权重
  assists: 0.15,  // 助攻权重
  damage: 0.50,   // 伤害权重
}

/** 刺客型职业（玄机/碎梦）：击杀权重更高、伤害权重降低 */
export const ASSASSIN_OUTPUT_WEIGHTS = {
  kills: 0.65,    // 击杀权重
  assists: 0.15,  // 助攻权重（与默认一致）
  damage: 0.20,   // 伤害权重
}

/** 破塔卸甲在建筑分中的折算系数 */
export const TOWER_BREAK_WEIGHT = 0.7

/** 铁衣在生存维度中的死亡加重系数（存活率 = 1 - 死亡×系数/全队最高死亡） */
export const TANK_DEATH_PENALTY = 2

/** 刺客型职业（玄机/碎梦）在生存维度中的死亡减轻系数 */
export const ASSASSIN_DEATH_RELIEF = 0.8

/** 适用刺客型输出权重的职业 */
const ASSASSIN_PROFESSIONS = new Set(['玄机', '碎梦'])

/** 生存维度权重 */
export const SURVIVAL_WEIGHTS = {
  taken: 0.40,    // 承伤权重
  survival: 0.60, // 存活率权重
}

// ==================== 评分计算 ====================

export interface PlayerScore {
  player: MatchData
  roleType: RoleType
  output: number
  building: number
  healing: number
  survival: number
  special: number
  total: number
  kda: number
}

/**
 * 综合评分（基于实际数据分析优化版）
 * 
 * 特点：
 * 1. 最大值归一化：单项最高者得 100 分
 * 2. 职业差异化：4 类职业不同权重
 * 3. 输出维度：击杀×0.35 + 助攻×0.15 + 伤害×0.50
 * 4. 生存维度：承伤×0.40 + 存活率×0.60
 */
export function computeScores(items: MatchData[]): PlayerScore[] {
  if (!items.length) return []
  
  // 计算全队平均值
  const avg = {
    kills: items.reduce((s, r) => s + r.kills, 0) / items.length,
    assists: items.reduce((s, r) => s + r.assists, 0) / items.length,
    damage: items.reduce((s, r) => s + r.player_damage + r.armor_break_damage, 0) / items.length,
    building: items.reduce((s, r) => s + r.building_damage + r.tower_break_damage, 0) / items.length,
    healing: items.reduce((s, r) => s + r.healing, 0) / items.length,
    taken: items.reduce((s, r) => s + r.damage_taken, 0) / items.length,
    deaths: items.reduce((s, r) => s + r.deaths, 0) / items.length,
    revives: items.reduce((s, r) => s + r.revives, 0) / items.length,
    fenGu: items.reduce((s, r) => s + r.fen_gu, 0) / items.length,
  }
  
  // 计算每个玩家的评分
  // 先计算原始得分（使用最大值归一化）
  const rawScores = items.map((p) => {
    // 判定职业类型
    const roleType = detectRole(p, avg)
    const weights = SCORE_WEIGHTS[roleType]
    
    // 计算输出维度（最大值归一化，加权）
    const maxKills = Math.max(...items.map(r => r.kills), 1)
    const maxAssists = Math.max(...items.map(r => r.assists), 1)
    const maxDamage = Math.max(...items.map(r => r.player_damage + r.armor_break_damage), 1)
    
    const killsScore = (p.kills / maxKills) * 100
    const assistsScore = (p.assists / maxAssists) * 100
    const damageScore = ((p.player_damage + p.armor_break_damage) / maxDamage) * 100
    const outWeights = ASSASSIN_PROFESSIONS.has(p.profession || '') ? ASSASSIN_OUTPUT_WEIGHTS : OUTPUT_WEIGHTS
    const output = killsScore * outWeights.kills + 
                   assistsScore * outWeights.assists + 
                   damageScore * outWeights.damage
    
    // 计算建筑维度（最大值归一化，破塔卸甲按 ×0.7 折算）
    const buildingValue = (r: MatchData) => r.building_damage + r.tower_break_damage * TOWER_BREAK_WEIGHT
    const maxBuilding = Math.max(...items.map(buildingValue), 1)
    const building = (buildingValue(p) / maxBuilding) * 100
    
    // 计算治疗维度（最大值归一化）
    const maxHealing = Math.max(...items.map(r => r.healing), 1)
    const healing = (p.healing / maxHealing) * 100
    
    // 计算生存维度（最大值归一化，加权；铁衣死亡×2 加重、玄机/碎梦死亡×0.8 减轻）
    const maxTaken = Math.max(...items.map(r => r.damage_taken), 1)
    const maxDeaths = Math.max(...items.map(r => r.deaths), 1)
    
    const takenScore = (p.damage_taken / maxTaken) * 100
    const isAssassin = ASSASSIN_PROFESSIONS.has(p.profession || '')
    const deathPenalty = p.profession === '铁衣' ? TANK_DEATH_PENALTY : isAssassin ? ASSASSIN_DEATH_RELIEF : 1
    const survivalRateScore = Math.max(0, (1 - p.deaths * deathPenalty / maxDeaths) * 100)
    const survival = takenScore * SURVIVAL_WEIGHTS.taken + 
                     survivalRateScore * SURVIVAL_WEIGHTS.survival
    
    // 计算特殊维度（最大值归一化）
    const maxRevives = Math.max(...items.map(r => r.revives), 1)
    const maxFenGu = Math.max(...items.map(r => r.fen_gu), 1)
    
    const revivesScore = (p.revives / maxRevives) * 100
    const fenGuScore = (p.fen_gu / maxFenGu) * 100
    const special = (revivesScore + fenGuScore) / 2
    
    // 计算总分（加权）
    const total = output * weights.output +
                  building * weights.building +
                  healing * weights.healing +
                  survival * weights.survival +
                  special * weights.special
    
    return {
      player: p,
      roleType,
      output: Math.round(output),
      building: Math.round(building),
      healing: Math.round(healing),
      survival: Math.round(survival),
      special: Math.round(special),
      total: Math.round(total),
      kda: calcKDA(p),
    }
  })
  
  // 直接返回排序后的结果（不再归一化）
  return rawScores.sort((a, b) => b.total - a.total)
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

/** 按阵营聚合战斗数据。 */
export function aggregateCamps(items: MatchData[]): CampAgg[] {
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
  return [...map.values()]
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
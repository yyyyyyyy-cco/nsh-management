/** 数据分析计算工具（移植自参考项目 B 的 analysis/utils，字段与 MatchData 对应）。 */
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

/** KDA = (击杀 + 助攻) / 死亡（重伤）。 */
export function calcKDA(p: MatchData): number {
  return (p.kills + p.assists) / Math.max(p.deaths, 1)
}

/** 占比字符串。 */
export function pctStr(part: number, total: number): string {
  if (!total) return '0%'
  return ((part / total) * 100).toFixed(1) + '%'
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

export interface PlayerScore {
  player: MatchData
  output: number
  building: number
  healing: number
  survival: number
  special: number
  total: number
  kda: number
}

/** 综合评分（移植自 B 的 ScoreAnalysis，字段映射：deaths=重伤、revives=复活、fen_gu=焚骨）。 */
export function computeScores(items: MatchData[]): PlayerScore[] {
  if (!items.length) return []
  const max = (key: (r: MatchData) => number) => Math.max(...items.map(key), 1)
  const maxKills = max((r) => r.kills)
  const maxAssists = max((r) => r.assists)
  const maxOutput = max((r) => r.player_damage + r.armor_break_damage)
  const maxBuilding = max((r) => r.building_damage + r.tower_break_damage)
  const maxHealing = max((r) => r.healing)
  const maxTaken = max((r) => r.damage_taken)
  const maxDeaths = max((r) => r.deaths)
  const maxRevives = max((r) => r.revives)
  const maxFenGu = max((r) => r.fen_gu)

  return items
    .map((p) => {
      const output =
        ((p.kills / maxKills) * 0.3 + (p.assists / maxAssists) * 0.2 + ((p.player_damage + p.armor_break_damage) / maxOutput) * 0.5) * 100
      const building = ((p.building_damage + p.tower_break_damage) / maxBuilding) * 100
      const healing = (p.healing / maxHealing) * 100
      const survival = ((p.damage_taken / maxTaken) * 0.6 + (1 - p.deaths / maxDeaths) * 0.4) * 100
      const special = ((p.revives / maxRevives) * 0.5 + (p.fen_gu / maxFenGu) * 0.5) * 100
      const total = output * 0.3 + building * 0.15 + healing * 0.15 + survival * 0.25 + special * 0.15
      return {
        player: p,
        output: Math.round(output),
        building: Math.round(building),
        healing: Math.round(healing),
        survival: Math.round(survival),
        special: Math.round(special),
        total: Math.round(total),
        kda: calcKDA(p),
      }
    })
    .sort((a, b) => b.total - a.total)
}

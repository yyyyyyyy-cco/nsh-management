/** 单场战报渲染数据：仅统计我方阵营（排表成员命中数最多的阵营，与后端小队分析口径一致）。 */
import type { IndicatorsResponse, MatchDataIndicators } from '@/types/matchData'
import type { LineupInfo } from '@/types/lineup'
import type { ScheduleInfo } from '@/types/schedule'
import { aggregateProfessions, computeScores } from './analysis'

/** 榜单条目（按玩家去重后的最佳单局）。 */
export interface ReportRankItem {
  rank: number
  player_name: string
  profession: string | null
  value: number
  round_no: number
}

/** 数据之王条目。 */
export interface ReportKingItem {
  label: string
  player_name: string
  profession: string | null
  value: number
  round_no: number
}

/** 我方聚合（逐局用）。 */
export interface ReportSideAgg {
  camp: string
  kills: number
  assists: number
  playerDamage: number
  buildingDamage: number
  healing: number
  damageTaken: number
  deaths: number
  fenGu: number
}

/** 单局战况（我方视角）。 */
export interface ReportRoundInfo {
  roundNo: number
  result: string | null
  hasData: boolean
  team: ReportSideAgg | null
  mvp: { player_name: string; score: number } | null
  killKing: { player_name: string; kills: number } | null
}

/** 全场 MVP（各局内最高评分者的最高分，标注所属局）。 */
export interface ReportMvp {
  player_name: string
  profession: string | null
  camp: string
  round_no: number
  score: number
  kda: number
  kills: number
  playerDamage: number
  healing: number
}

/** 我方总览（六项合计）。 */
export interface ReportOverviewStats {
  totalKills: number
  totalAssists: number
  totalDamage: number
  totalBuilding: number
  totalHealing: number
  totalFenGu: number
}

/** 职业分布条目（人数 + 伤害占比）。 */
export interface ReportProfessionItem {
  profession: string
  count: number
  damagePct: number
}

/** 战报完整渲染数据。 */
export interface MatchReportData {
  ourCamp: string | null
  playerCount: number
  recordCount: number
  importedRounds: number[]
  rounds: number
  overview: ReportOverviewStats
  mvp: ReportMvp | null
  kings: ReportKingItem[]
  killsTop: ReportRankItem[]
  damageTop: ReportRankItem[]
  healingTop: ReportRankItem[]
  roundsInfo: ReportRoundInfo[]
  professions: ReportProfessionItem[]
}

/** 数据之王口径（六项，各取全场最佳单局）。 */
const KING_DEFS: { label: string; get: (r: MatchDataIndicators) => number }[] = [
  { label: '击杀王', get: (r) => r.kills },
  { label: '伤害王', get: (r) => r.player_damage },
  { label: '建筑王', get: (r) => r.building_damage },
  { label: '治疗王', get: (r) => r.healing },
  { label: '承伤王', get: (r) => r.damage_taken },
  { label: '焚骨王', get: (r) => r.fen_gu },
]

/** 榜单取前 N 名。 */
const TOP_N = 3

/**
 * 我方阵营判定：排表只含我方成员，取命中排表人数最多的阵营（与后端 squad-analysis 口径一致）；
 * 无任何命中时兜底取首条记录阵营。
 */
function resolveOurCamp(items: MatchDataIndicators[], lineup: LineupInfo | null): string | null {
  const nameSet = new Set<string>()
  for (const team of lineup?.data ?? []) {
    for (const slot of team.slots ?? []) {
      const name = (slot.member_name || '').trim()
      if (name) nameSet.add(name)
    }
  }
  const hits = new Map<string, number>()
  for (const r of items) {
    if (nameSet.has((r.player_name || '').trim())) {
      hits.set(r.camp, (hits.get(r.camp) ?? 0) + 1)
    }
  }
  if (hits.size) {
    return [...hits.entries()].sort((a, b) => b[1] - a[1])[0][0]
  }
  return items[0]?.camp ?? null
}

/** 按玩家去重保留最佳单局记录，降序返回。 */
function bestBy(items: MatchDataIndicators[], get: (r: MatchDataIndicators) => number): MatchDataIndicators[] {
  const best = new Map<string, MatchDataIndicators>()
  for (const r of items) {
    const cur = best.get(r.player_name)
    if (!cur || get(r) > get(cur)) best.set(r.player_name, r)
  }
  return [...best.values()].sort((a, b) => get(b) - get(a))
}

function toRankItems(items: MatchDataIndicators[], get: (r: MatchDataIndicators) => number): ReportRankItem[] {
  return bestBy(items, get)
    .slice(0, TOP_N)
    .map((r, index) => ({
      rank: index + 1,
      player_name: r.player_name,
      profession: r.profession,
      value: get(r),
      round_no: r.round_no,
    }))
}

/** 某单局的我方记录汇总。 */
function sumSide(camp: string, recs: MatchDataIndicators[]): ReportSideAgg {
  const acc: ReportSideAgg = {
    camp, kills: 0, assists: 0, playerDamage: 0, buildingDamage: 0,
    healing: 0, damageTaken: 0, deaths: 0, fenGu: 0,
  }
  for (const r of recs) {
    acc.kills += r.kills
    acc.assists += r.assists
    acc.playerDamage += r.player_damage
    acc.buildingDamage += r.building_damage
    acc.healing += r.healing
    acc.damageTaken += r.damage_taken
    acc.deaths += r.deaths
    acc.fenGu += r.fen_gu
  }
  return acc
}

/** 组装战报数据：单一数据源（全部已导入局的衍生指标记录）+ 排表（判定我方）+ 赛程元信息。 */
export function buildReportData(
  indicators: IndicatorsResponse,
  lineup: LineupInfo | null,
  schedule: ScheduleInfo | null,
): MatchReportData {
  const ourCamp = resolveOurCamp(indicators.items, lineup)
  // 仅保留我方阵营记录（其余阵营不参与任何统计）
  const items = ourCamp ? indicators.items.filter((r) => r.camp === ourCamp) : []

  // 参战规模（按玩家去重）
  const playerCount = new Set(items.map((r) => r.player_name)).size

  // 按局分组
  const byRound = new Map<number, MatchDataIndicators[]>()
  for (const r of items) {
    const arr = byRound.get(r.round_no)
    if (arr) arr.push(r)
    else byRound.set(r.round_no, [r])
  }
  const importedRounds = [...byRound.keys()].sort((a, b) => a - b)
  const rounds = schedule?.rounds ?? Math.max(1, ...importedRounds)

  // 我方总览（六项合计）
  const overview = items.reduce(
    (acc, r) => ({
      totalKills: acc.totalKills + r.kills,
      totalAssists: acc.totalAssists + r.assists,
      totalDamage: acc.totalDamage + r.player_damage,
      totalBuilding: acc.totalBuilding + r.building_damage,
      totalHealing: acc.totalHealing + r.healing,
      totalFenGu: acc.totalFenGu + r.fen_gu,
    }),
    { totalKills: 0, totalAssists: 0, totalDamage: 0, totalBuilding: 0, totalHealing: 0, totalFenGu: 0 },
  )

  // 逐局战况 + 全场 MVP（评分口径：该局我方同职业(分路)均值基准，见 analysis.computeScores）
  let mvp: ReportMvp | null = null
  const roundsInfo: ReportRoundInfo[] = []
  for (let n = 1; n <= rounds; n++) {
    const recs = byRound.get(n)
    const result = schedule?.round_results?.[n - 1] ?? null
    if (!recs?.length) {
      roundsInfo.push({ roundNo: n, result, hasData: false, team: null, mvp: null, killKing: null })
      continue
    }
    const team = sumSide(ourCamp ?? '', recs)
    const top = computeScores(recs)[0]
    const killKingRec = recs.reduce((best, r) => (r.kills > best.kills ? r : best), recs[0])
    roundsInfo.push({
      roundNo: n,
      result,
      hasData: true,
      team,
      mvp: top ? { player_name: top.player.player_name, score: top.total } : null,
      killKing: { player_name: killKingRec.player_name, kills: killKingRec.kills },
    })
    if (top && (!mvp || top.total > mvp.score)) {
      mvp = {
        player_name: top.player.player_name,
        profession: top.player.profession,
        camp: top.player.camp,
        round_no: n,
        score: top.total,
        kda: Math.round(top.kda * 10) / 10,
        kills: top.player.kills,
        playerDamage: top.player.player_damage,
        healing: top.player.healing,
      }
    }
  }

  // 数据之王（六项各取我方全场最佳单局）
  const kings: ReportKingItem[] = KING_DEFS.map((def) => {
    const top = bestBy(items, def.get)[0]
    return {
      label: def.label,
      player_name: top?.player_name ?? '-',
      profession: top?.profession ?? null,
      value: top ? def.get(top) : 0,
      round_no: top?.round_no ?? 0,
    }
  })

  // 职业分布（我方人数 + 我方伤害占比）
  const professions = aggregateProfessions(items)
    .sort((a, b) => b.count - a.count)
    .map((p) => ({ profession: p.profession, count: p.count, damagePct: Math.round(p.damage_pct * 10) / 10 }))

  return {
    ourCamp,
    playerCount,
    recordCount: items.length,
    importedRounds,
    rounds,
    overview,
    mvp,
    kings,
    killsTop: toRankItems(items, (r) => r.kills),
    damageTop: toRankItems(items, (r) => r.player_damage),
    healingTop: toRankItems(items, (r) => r.healing),
    roundsInfo,
    professions,
  }
}

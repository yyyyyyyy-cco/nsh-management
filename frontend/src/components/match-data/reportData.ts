/** 单场战报渲染数据：仅统计我方阵营（排表成员命中数最多的阵营，与后端小队分析口径一致）。
 * 行数豁免（连续逻辑）：战报数据组装围绕同一数据流（衍生指标记录 + 排表/分析调整副本 + 赛程元信息）。
 * 登记见 .agent/rules/file-length-rule.md 豁免清单。 */
import type { IndicatorsResponse, MatchData, MatchDataIndicators } from '@/types/matchData'
import type { LineupInfo } from '@/types/lineup'
import type { ScheduleInfo } from '@/types/schedule'
import { computeScores } from './analysis'

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
  deathKing: { player_name: string; deaths: number } | null
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

/** 小队战况条目（按排表 + 分析调整副本归属聚合我方记录；无排表时列表为空）。 */
export interface ReportSquadItem {
  name: string
  kills: number
  assists: number
  deaths: number
  playerDamage: number
  buildingDamage: number
  healing: number
  damageTaken: number
  fenGu: number
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
  buildingTop: ReportRankItem[]
  deathsTop: ReportRankItem[]
  scoreTop: ReportRankItem[]
  roundsInfo: ReportRoundInfo[]
  squads: ReportSquadItem[]
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

/** 组装战报数据：单一数据源（全部已导入局的衍生指标记录）+ 排表（判定我方/小队归属）+ 分析调整副本（覆盖小队归属）+ 赛程元信息。 */
export function buildReportData(
  indicators: IndicatorsResponse,
  lineup: LineupInfo | null,
  schedule: ScheduleInfo | null,
  adjustments: Record<string, string> | null = null,
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
  // 总分榜：按玩家保留最佳单局综合评分（与榜单“去重取最佳单局”口径一致）
  const scoreBest = new Map<string, { player: MatchData; score: number; roundNo: number }>()
  for (let n = 1; n <= rounds; n++) {
    const recs = byRound.get(n)
    const result = schedule?.round_results?.[n - 1] ?? null
    if (!recs?.length) {
      roundsInfo.push({ roundNo: n, result, hasData: false, team: null, mvp: null, killKing: null, deathKing: null })
      continue
    }
    const team = sumSide(ourCamp ?? '', recs)
    const scored = computeScores(recs)
    const top = scored[0]
    for (const s of scored) {
      const prev = scoreBest.get(s.player.player_name)
      if (!prev || s.total > prev.score) {
        scoreBest.set(s.player.player_name, { player: s.player, score: s.total, roundNo: n })
      }
    }
    const killKingRec = recs.reduce((best, r) => (r.kills > best.kills ? r : best), recs[0])
    const deathKingRec = recs.reduce((worst, r) => (r.deaths > worst.deaths ? r : worst), recs[0])
    roundsInfo.push({
      roundNo: n,
      result,
      hasData: true,
      team,
      mvp: top ? { player_name: top.player.player_name, score: top.total } : null,
      killKing: { player_name: killKingRec.player_name, kills: killKingRec.kills },
      deathKing: { player_name: deathKingRec.player_name, deaths: deathKingRec.deaths },
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

  // 总分榜（综合评分最佳单局 TOP3；口径与 MVP 一致，见 analysis.computeScores）
  const scoreTop: ReportRankItem[] = [...scoreBest.values()]
    .sort((a, b) => b.score - a.score)
    .slice(0, TOP_N)
    .map((s, index) => ({
      rank: index + 1,
      player_name: s.player.player_name,
      profession: s.player.profession,
      value: s.score,
      round_no: s.roundNo,
    }))

  // 小队战况（按排表 + 分析调整副本归属聚合我方各队记录；无排表时列表为空，区块自动隐藏）
  const squads: ReportSquadItem[] = []
  if (lineup?.data?.length) {
    const squadOf = new Map<string, string>()
    const squadOrder: string[] = []
    // 排表队伍 key（category:team_index）→ 展示名，同时用于校验调整目标仍存在
    const nameByKey = new Map<string, string>()
    for (const team of lineup.data) {
      const name = `${team.category} 第${team.team_index + 1}队`
      nameByKey.set(`${team.category}:${team.team_index}`, name)
      if (!squadOrder.includes(name)) squadOrder.push(name)
      for (const slot of team.slots ?? []) {
        const member = (slot.member_name || '').trim()
        if (member) squadOf.set(member, name)
      }
    }
    // 叠加分析调整副本（未排表成员 → 目标队伍；目标已不存在于排表时忽略，与小队分析视图口径一致）
    for (const [player, target] of Object.entries(adjustments ?? {})) {
      const name = nameByKey.get(target)
      const member = (player || '').trim()
      if (name && member) squadOf.set(member, name)
    }
    const acc = new Map<string, Omit<ReportSquadItem, 'name'>>()
    for (const r of items) {
      const squad = squadOf.get((r.player_name || '').trim()) ?? '未排表'
      const cur = acc.get(squad) ?? { kills: 0, assists: 0, deaths: 0, playerDamage: 0, buildingDamage: 0, healing: 0, damageTaken: 0, fenGu: 0 }
      cur.kills += r.kills
      cur.assists += r.assists
      cur.deaths += r.deaths
      cur.playerDamage += r.player_damage
      cur.buildingDamage += r.building_damage
      cur.healing += r.healing
      cur.damageTaken += r.damage_taken
      cur.fenGu += r.fen_gu
      acc.set(squad, cur)
    }
    for (const name of [...squadOrder, '未排表']) {
      const cur = acc.get(name)
      if (cur) {
        squads.push({ name, ...cur })
      } else if (name !== '未排表') {
        // 已排表但无比赛记录的队伍：显示 0，保证排表队伍完整呈现
        squads.push({ name, kills: 0, assists: 0, deaths: 0, playerDamage: 0, buildingDamage: 0, healing: 0, damageTaken: 0, fenGu: 0 })
      }
    }
  }

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
    buildingTop: toRankItems(items, (r) => r.building_damage),
    deathsTop: toRankItems(items, (r) => r.deaths),
    scoreTop,
    roundsInfo,
    squads,
  }
}

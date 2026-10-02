/** 职业深度图表 option 与对比行构建（自 ProfessionDetailTab.vue 拆出，纯函数）。 */
import type { ProfessionStats } from '@/types/matchData'

import { CAMP_COLORS, fmtNum, PROF_COLORS } from './analysis'
import { CHART_THEME } from './chartTheme'

const HEALERS = new Set(['素问', '鸿音', '潮光'])
export const TANK_PROFESSIONS = new Set(['铁衣', '血河', '沧澜', '素问'])

/** 治疗职业判定：职业名在候选列表中，且该职业整体治疗量 > 伤害量。 */
export function isHealer(p: ProfessionStats) {
  return HEALERS.has(p.profession) && p.avg_healing > p.avg_damage
}

export function isTank(p: ProfessionStats) {
  return TANK_PROFESSIONS.has(p.profession) && p.camps.some((c) => c.avg_damage_taken > 0)
}

export function hex(c: string): string {
  return c.length > 7 ? c.slice(0, 7) : c
}

export function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}

export function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

export const METRIC_LABELS: Record<string, string> = {
  avg_kills: '平均击杀',
  avg_player_damage: '平均伤害',
  avg_building_damage: '平均塔伤',
  avg_healing: '平均治疗',
  avg_damage_taken: '平均承伤',
  avg_kda: '平均KDA',
}

/** 职业人数分布饼图 */
export function buildCountPieOption(profStats: ProfessionStats[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', ...CHART_THEME.tooltip, formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['40%', '50%'],
        data: profStats.map((p) => ({
          name: p.profession,
          value: p.count,
          itemStyle: { color: hex(PROF_COLORS[p.profession] || '#999'), borderColor: '#fff', borderWidth: 2 },
        })),
        label: { show: false },
        emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  }
}

export type MetricKey = 'avg_kills' | 'avg_player_damage' | 'avg_healing' | 'avg_damage_taken'

/** 职业平均指标分阵营柱状图 */
export function buildMetricBarOption(
  profStats: ProfessionStats[],
  metric: MetricKey,
  opts?: { filterProf?: (p: ProfessionStats) => boolean; fmt?: (v: number) => string },
) {
  const list = profStats.filter((p) => !opts?.filterProf || opts.filterProf(p))
  const campNames = [...new Set(list.flatMap((p) => p.camps.map((c) => c.camp)))]
  const fmt = opts?.fmt ?? ((v: number) => v.toFixed(1))
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      valueFormatter: (v: number) => fmt(v),
    },
    legend: { top: 0, data: campNames, ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((p) => p.profession),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: campNames.map((camp, i) => ({
      name: camp,
      type: 'bar',
      barWidth: 16,
      barGap: '40%',
      itemStyle: { color: campColor(i), borderRadius: [3, 3, 0, 0] },
      data: list.map((p) => p.camps.find((c) => c.camp === camp)?.[metric] ?? 0),
    })),
  }
}

/** 职业技能使用率柱状图（清泉羽化率 / 焚骨率） */
export function buildSkillBarOption(profStats: ProfessionStats[]) {
  const list = profStats.filter((p) => p.camps.some((c) => c.count > 0))
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      valueFormatter: (v: number) => v.toFixed(2) + ' 次/分钟',
    },
    legend: { bottom: 0, data: ['清泉羽化率', '焚骨率'], ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((p) => p.profession),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
    },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => v.toFixed(1) }, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '清泉羽化率', type: 'bar', barWidth: 14, itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] }, data: list.map((p) => p.avg_revive_rate) },
      { name: '焚骨率', type: 'bar', barWidth: 14, itemStyle: { color: '#5b7a9d', borderRadius: [3, 3, 0, 0] }, data: list.map((p) => p.avg_fen_gu_rate) },
    ],
  }
}

/** 职业差值/波动值行数据（可按职业筛选） */
export function buildComparisonRows(profStats: ProfessionStats[], profFilter: string) {
  const rows: { profession: string; label: string; value1: number; value2: number; diff: number; wave: number; metric: string }[] = []
  const list = profFilter
    ? profStats.filter((p) => p.profession === profFilter)
    : profStats
  for (const p of list) {
    for (const cmp of p.comparison) {
      rows.push({
        profession: p.profession,
        label: METRIC_LABELS[cmp.metric] ?? cmp.metric,
        value1: cmp.value1,
        value2: cmp.value2,
        diff: cmp.diff,
        wave: cmp.wave,
        metric: cmp.metric,
      })
    }
  }
  return rows
}

/** 差值表数值格式化（按指标类型） */
export function fmtCmpValue(row: { metric: string }, v: number): string {
  if (row.metric === 'avg_kda') return v.toFixed(2)
  if (row.metric === 'avg_kills') return v.toFixed(1)
  if (
    row.metric === 'avg_player_damage' ||
    row.metric === 'avg_building_damage' ||
    row.metric === 'avg_healing' ||
    row.metric === 'avg_damage_taken'
  ) {
    return fmtNum(v)
  }
  return String(v)
}

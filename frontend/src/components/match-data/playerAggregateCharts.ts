/** 职业/阵营聚合类图表 option 构建（自 PlayerAnalysis.vue 拆出，纯函数）。 */
import type { MatchData } from '@/types/matchData'

import type { CampAgg } from './analysis'
import { computeScores, fmtNum, profColor } from './analysis'
import { CHART_THEME, tooltipText } from './chartTheme'

/** 职业×指标热力图（按平均值归一化：avg / 该列最高均值 * 100）。 */
export function buildHeatmapOption(items: MatchData[], allProfs: string[]) {
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'player_damage', label: '伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
    { key: 'assists', label: '助攻' },
  ]
  const raw: { xi: number; yi: number; avg: number; label: string; prof: string }[] = []
  allProfs.forEach((prof, yi) => {
    const players = items.filter((r) => (r.profession || '未知') === prof)
    if (!players.length) return
    metrics.forEach((m, xi) => {
      const avg = players.reduce((s, r) => s + (r[m.key as keyof MatchData] as number), 0) / players.length
      raw.push({ xi, yi, avg, label: m.label, prof })
    })
  })
  const maxVals = metrics.map((_, xi) => Math.max(...raw.filter((r) => r.xi === xi).map((r) => r.avg)))
  // 按平均值归一化：avg / 该列最高均值 * 100，颜色直接反映平均值大小（非列内 min-max 拉伸）
  const data = raw.map((r) => {
    const normalized = maxVals[r.xi] > 0 ? Math.round((r.avg / maxVals[r.xi]) * 100) : 0
    return [r.xi, r.yi, normalized, fmtNum(r.avg), r.label, r.prof]
  })
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: (number | string)[] }).data
        return `<b>${tooltipText(d[5])}</b> · ${tooltipText(d[4])}<br/>平均值: ${tooltipText(d[3])}<br/>相对水平: ${tooltipText(d[2])}%`
      },
    },
    grid: { left: 64, right: 20, top: 10, bottom: 52 },
    xAxis: {
      type: 'category',
      data: metrics.map((m) => m.label),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0, fontSize: 12 },
      axisTick: { show: false },
      splitArea: { show: true, areaStyle: { color: ['transparent', 'rgba(0,0,0,0.015)'] } },
    },
    yAxis: {
      type: 'category',
      data: allProfs,
      axisLabel: { ...CHART_THEME.axis.axisLabel, fontSize: 11, fontWeight: 600, width: 48, overflow: 'truncate' },
      axisTick: { show: false },
      axisLine: { show: false },
    },
    visualMap: {
      min: 0,
      max: 100,
      dimension: 2, // 显式绑定归一化值维度（data 第 3 项），否则默认取第一维 xi 导致颜色失效
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 2,
      itemWidth: 12,
      itemHeight: 80,
      inRange: { color: ['#fef9e7', '#fce38a', '#f8b739', '#e67e22', '#d35400', '#a93226'] },
      textStyle: { color: '#8a8378', fontSize: 10 },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: true,
          fontSize: 10,
          color: '#444',
          fontWeight: 500,
          formatter: (p: unknown) => (p as { data: number[] }).data[3],
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 2,
          borderRadius: 3,
        },
        emphasis: { itemStyle: { shadowBlur: 8, shadowColor: 'rgba(0, 0, 0, 0.3)', borderColor: '#fff', borderWidth: 2 } },
      },
    ],
  }
}

/** 玩家四维数据：Top10 按综合评分降序，玩家伤害/建筑伤害/治疗/承伤分组柱。 */
export function buildPlayerBarsOption(items: MatchData[]) {
  const top = computeScores(items).slice(0, 10).map((s) => s.player)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: ['玩家伤害', '建筑伤害', '治疗', '承伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 24, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: top.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      { name: '玩家伤害', type: 'bar', barWidth: 8, barGap: '25%', itemStyle: { color: '#c9a13b', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.player_damage) },
      { name: '建筑伤害', type: 'bar', barWidth: 8, itemStyle: { color: '#5b7a9d', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.building_damage) },
      { name: '治疗', type: 'bar', barWidth: 8, itemStyle: { color: '#2e8b57', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.healing) },
      { name: '承伤', type: 'bar', barWidth: 8, itemStyle: { color: '#c0392b', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.damage_taken) },
    ],
  }
}

/** 阵营职业伤害/治疗构成堆叠柱状图。 */
export function buildStackOption(
  items: MatchData[],
  camps: CampAgg[],
  allProfs: string[],
  field: 'player_damage' | 'healing',
) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { axisValue: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${tooltipText(list[0]?.axisValue)}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${tooltipText(p.seriesName)}: ${fmtNum(p.value)}<br/>`
        })
        return html
      },
    },
    legend: { top: 0, ...CHART_THEME.legend, type: 'scroll' },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: camps.map((c) => c.camp), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: allProfs.map((prof) => ({
      name: prof,
      type: 'bar',
      stack: 'total',
      barWidth: 40,
      itemStyle: { color: profColor(prof), borderRadius: 0 },
      data: camps.map((c) =>
        items.filter((r) => r.camp === c.camp && (r.profession || '未知') === prof).reduce((s, r) => s + r[field], 0),
      ),
    })),
  }
}

/** 伤害分布饼图：玩家伤害 / 建筑伤害 / 治疗。 */
export function buildDamagePieOption(items: MatchData[]) {
  const total = (key: keyof MatchData) => items.reduce((s, r) => s + (r[key] as number), 0)
  const rows = [
    { name: '玩家伤害', value: total('player_damage') },
    { name: '建筑伤害', value: total('building_damage') },
    { name: '治疗', value: total('healing') },
  ].filter((r) => r.value > 0)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      ...CHART_THEME.tooltip,
      formatter: (p: { name: string; value: number; percent: number }) =>
        `${tooltipText(p.name)}: ${fmtNum(p.value)} (${tooltipText(p.percent)}%)`
    },
    legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['40%', '50%'],
        data: rows.map((r, i) => ({
          name: r.name,
          value: r.value,
          itemStyle: { color: ['#c9a13b', '#5b7a9d', '#2e8b57'][i], borderColor: '#fff', borderWidth: 2 },
        })),
        label: { show: false },
        emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  }
}

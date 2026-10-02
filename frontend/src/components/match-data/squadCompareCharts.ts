/** 多小队对比图表 option 与差值行构建（自 SquadAnalysisTab.vue 拆出，纯函数）。 */
import type { SquadAnalysis } from '@/types/matchData'

import { fmtNum } from './analysis'
import { CHART_THEME } from './chartTheme'

export const COMPARE_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b']

export const COMPARE_METRIC_LABELS: Record<string, string> = {
  kills: '总击杀',
  assists: '总助攻',
  player_damage: '玩家伤害',
  building_damage: '建筑伤害',
  healing: '治疗',
  damage_taken: '承伤',
  deaths: '总死亡',
  kda: '均 KDA',
  dps: '均秒伤',
  damage_per_death: '均每死输出',
  taken_per_death: '均每死承伤',
  heal_conversion: '均治疗转化',
}

/** 多小队对比：汇总对比柱状图 */
export function compareSummaryBarOption(sel: SquadAnalysis[]) {
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'assists', label: '助攻' },
    { key: 'deaths', label: '重伤' },
    { key: 'player_damage', label: '玩家伤害' },
    { key: 'building_damage', label: '建筑伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { top: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: metrics.map((m) => m.label),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        ...CHART_THEME.axis.axisLabel,
        formatter: (v: number) => fmtNum(v),
        width: 50,
        overflow: 'truncate',
      },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: sel.map((s, i) => ({
      name: s.squad_name,
      type: 'bar',
      barWidth: 14,
      barGap: '30%',
      itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length], borderRadius: [3, 3, 0, 0] },
      data: metrics.map((m) => s.totals[m.key as keyof typeof s.totals]),
      // 柱顶数值：击杀/助攻/重伤小数字原样展示，大额伤害压缩
      label: {
        show: true,
        position: 'top',
        fontSize: 10,
        color: '#6b5b45',
        formatter: (p: { value: number }) => (p.value > 9999 ? fmtNum(p.value) : String(p.value)),
      },
    })),
  }
}

/** 多小队对比：均值指标雷达图 */
export function compareRadarOption(sel: SquadAnalysis[]) {
  const dims = [
    { name: 'KDA', max: 0 },
    { name: '秒伤', max: 0 },
    { name: '每死输出', max: 0 },
    { name: '每死承伤', max: 0 },
    { name: '治疗转化', max: 0 },
  ]
  const keys: (keyof SquadAnalysis['indicators'])[] = [
    'kda',
    'dps',
    'damage_per_death',
    'taken_per_death',
    'heal_conversion',
  ]
  // 动态 max
  for (const d of dims) d.max = 1
  for (const s of sel) {
    keys.forEach((k, i) => {
      const v = s.indicators[k]
      if (v > dims[i].max) dims[i].max = v
    })
  }
  // 留余量
  for (const d of dims) d.max = Math.ceil(d.max * 1.15)

  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    radar: {
      center: ['50%', '46%'],
      radius: '60%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 50 },
      indicator: dims,
    },
    series: [
      {
        type: 'radar',
        data: sel.map((s, i) => ({
          name: s.squad_name,
          value: keys.map((k) => s.indicators[k]),
          areaStyle: { opacity: 0.1 },
          lineStyle: { width: 2.5, color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
          itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
          symbol: 'circle',
          symbolSize: 5,
        })),
      },
    ],
  }
}

/** 双小队对比：差值 / 波动值行数据（恰好选 2 队时展示） */
export function buildCompareDiffRows(a: SquadAnalysis, b: SquadAnalysis) {
  const rows: { label: string; v1: string; v2: string; diff: number; diffStr: string; wave: number }[] = []

  // 汇总指标
  const totalKeys: (keyof SquadAnalysis['totals'])[] = [
    'kills',
    'assists',
    'player_damage',
    'building_damage',
    'healing',
    'damage_taken',
    'deaths',
  ]
  for (const k of totalKeys) {
    const v1 = a.totals[k]
    const v2 = b.totals[k]
    const diff = v1 - v2
    const base = Math.min(v1, v2)
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: fmtNum(v1),
      v2: fmtNum(v2),
      diff,
      diffStr: fmtNum(Math.abs(diff)),
      wave: base > 0 ? (Math.abs(diff) / base) * 100 : 0,
    })
  }

  // 均值指标
  const indKeys: (keyof SquadAnalysis['indicators'])[] = [
    'kda',
    'dps',
    'damage_per_death',
    'taken_per_death',
    'heal_conversion',
  ]
  for (const k of indKeys) {
    const v1 = a.indicators[k]
    const v2 = b.indicators[k]
    const diff = +(v1 - v2).toFixed(2)
    const base = Math.min(v1, v2)
    const isDecimal = k === 'kda' || k === 'heal_conversion'
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: isDecimal ? v1.toFixed(2) : fmtNum(Math.round(v1)),
      v2: isDecimal ? v2.toFixed(2) : fmtNum(Math.round(v2)),
      diff,
      diffStr: isDecimal ? Math.abs(diff).toFixed(2) : fmtNum(Math.round(Math.abs(diff))),
      wave: base > 0 ? (Math.abs(diff) / base) * 100 : 0,
    })
  }

  return rows
}

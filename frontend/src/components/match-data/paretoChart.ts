/** 贡献度帕累托图与排行榜共用横轴标签（自 rankingCharts 拆出）。 */
import type { MatchData } from '@/types/matchData'

import { fmtNum } from './analysis'
import { CHART_THEME } from './chartTheme'

export const RANKING_X_LABEL = { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate', hideOverlap: true }

/** 贡献度帕累托图：玩家伤害降序柱 + 累计占比折线，识别核心输出。 */
export function buildParetoOption(items: MatchData[]) {
  const sorted = items.slice().sort((a, b) => b.player_damage - a.player_damage).slice(0, 20)
  const total = sorted.reduce((s, r) => s + r.player_damage, 0)
  let acc = 0
  const cum = sorted.map((r) => {
    acc += r.player_damage
    return total ? Math.round((acc / total) * 1000) / 10 : 0
  })
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { name: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${list[0].name}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${p.seriesName}: ${p.seriesName === '累计占比' ? p.value + '%' : fmtNum(p.value)}<br/>`
        })
        return html
      },
    },
    grid: { left: 12, right: 40, top: 32, bottom: 32, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: RANKING_X_LABEL,
    },
    yAxis: [
      {
        type: 'value',
        name: '伤害',
        axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
        splitLine: CHART_THEME.axis.splitLine,
        nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 40, 0, 0] },
      },
      {
        type: 'value',
        name: '累计占比',
        max: 100,
        axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: '{value}%' },
        splitLine: { show: false },
        nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 0, 0, 40] },
      },
    ],
    series: [
      {
        name: '玩家伤害',
        type: 'bar',
        barWidth: 14,
        data: sorted.map((r) => r.player_damage),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#c9a13b' }, { offset: 1, color: '#c9a13b88' }] },
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '累计占比',
        type: 'line',
        yAxisIndex: 1,
        data: cum,
        smooth: true,
        lineStyle: { width: 2, color: '#f04545', type: 'dashed' },
        itemStyle: { color: '#f04545' },
        symbol: 'circle',
        symbolSize: 5,
      },
    ],
  }
}

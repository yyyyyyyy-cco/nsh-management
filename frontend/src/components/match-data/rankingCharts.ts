/** 排行榜图表 option 构建（自 RankingTab.vue 拆出，纯函数）。 */
import type { MatchData } from '@/types/matchData'

import { calcKDA, fmtNum } from './analysis'
import { CHART_THEME, tooltipText } from './chartTheme'

import { RANKING_X_LABEL as X_LABEL } from './paretoChart'

/** KDA 分布折线图（KDA 榜 Top 20） */
export function buildKdaLineOption(items: MatchData[]) {
  const sorted = items.slice().sort((a, b) => calcKDA(b) - calcKDA(a)).slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    grid: { left: 12, right: 12, top: 32, bottom: 32, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: X_LABEL,
    },
    yAxis: [
      { type: 'value', name: 'KDA', axisLabel: { ...CHART_THEME.axis.axisLabel, width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine, nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 40, 0, 0] } },
      { type: 'value', name: '击杀', axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' }, splitLine: { show: false }, nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 0, 0, 40] } },
    ],
    series: [
      {
        name: 'KDA',
        type: 'line',
        data: sorted.map((r) => calcKDA(r).toFixed(1)),
        smooth: true,
        lineStyle: { width: 3, color: '#c9a13b' },
        itemStyle: { color: '#c9a13b' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(201,161,59,0.25)' }, { offset: 1, color: 'rgba(201,161,59,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
      {
        name: '击杀',
        type: 'line',
        yAxisIndex: 1,
        data: sorted.map((r) => r.kills),
        smooth: true,
        lineStyle: { width: 2, color: '#f04545', type: 'dashed' },
        itemStyle: { color: '#f04545' },
        symbol: 'diamond',
        symbolSize: 6,
      },
    ],
  }
}

/** 伤害分布折线图（玩家/建筑切换，Top 20） */
export function buildDamageLineOption(items: MatchData[], mode: 'player' | 'building') {
  const sorted = items
    .slice()
    .sort((a, b) => (mode === 'player' ? b.player_damage - a.player_damage : b.building_damage - a.building_damage))
    .slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    grid: { left: 12, right: 24, top: 28, bottom: 32, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: X_LABEL,
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      {
        name: mode === 'player' ? '玩家伤害' : '建筑伤害',
        type: 'line',
        data: sorted.map((r) => (mode === 'player' ? r.player_damage : r.building_damage)),
        smooth: true,
        lineStyle: { width: 3, color: '#5b7a9d' },
        itemStyle: { color: '#5b7a9d' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(91,122,157,0.25)' }, { offset: 1, color: 'rgba(91,122,157,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
    ],
  }
}

/** 治疗 / 承伤分布折线图（切换，Top 20） */
export function buildHealLineOption(items: MatchData[], mode: 'healing' | 'taken') {
  const sorted = items
    .slice()
    .sort((a, b) => (mode === 'healing' ? b.healing - a.healing : b.damage_taken - a.damage_taken))
    .slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    grid: { left: 12, right: 24, top: 28, bottom: 32, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: X_LABEL,
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      {
        name: mode === 'healing' ? '治疗量' : '承伤',
        type: 'line',
        data: sorted.map((r) => (mode === 'healing' ? r.healing : r.damage_taken)),
        smooth: true,
        lineStyle: { width: 3, color: mode === 'healing' ? '#2e8b57' : '#c0392b' },
        itemStyle: { color: mode === 'healing' ? '#2e8b57' : '#c0392b' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: mode === 'healing' ? 'rgba(46,139,87,0.25)' : 'rgba(192,57,43,0.25)' }, { offset: 1, color: mode === 'healing' ? 'rgba(46,139,87,0.02)' : 'rgba(192,57,43,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
    ],
  }
}

/** KDA 构成堆叠（击杀/助攻/重伤），看 KDA 高分是打得猛还是死得少。 */
export function buildKdaStackOption(items: MatchData[]) {
  const sorted = items.slice().sort((a, b) => calcKDA(b) - calcKDA(a)).slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { name: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${tooltipText(list[0]?.name)}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${tooltipText(p.seriesName)}: ${tooltipText(p.value)}<br/>`
        })
        return html
      },
    },
    legend: { bottom: 0, data: ['击杀', '助攻', '重伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 20, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: X_LABEL,
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '击杀', type: 'bar', stack: 'kda', barWidth: 18, itemStyle: { color: '#c9a13b' }, data: sorted.map((r) => r.kills) },
      { name: '助攻', type: 'bar', stack: 'kda', itemStyle: { color: '#5b7a9d' }, data: sorted.map((r) => r.assists) },
      { name: '重伤', type: 'bar', stack: 'kda', itemStyle: { color: '#c0392b' }, data: sorted.map((r) => r.deaths) },
    ],
  }
}

export { buildParetoOption } from './paretoChart'

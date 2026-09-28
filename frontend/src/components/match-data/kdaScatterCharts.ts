/** 玩家与小队成员的 KDA 散点图（自 playerScatterCharts / squadCharts 拆出）。 */
import type { MatchData, SquadMember } from '@/types/matchData'

import { calcKDA, fmtNum, profColor } from './analysis'
import { CHART_THEME } from './chartTheme'

/** 击杀 vs 重伤散点（KDA 分布）。 */
export function buildKdaScatterOption(items: MatchData[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: (number | string)[] }).data
        return `<b>${d[2]}</b> (${d[3]})<br/>击杀: ${d[0]}<br/>重伤: ${d[1]}<br/>KDA: ${Number(d[4]).toFixed(2)}`
      },
    },
    grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
    xAxis: {
      name: '击杀', nameLocation: 'middle', nameGap: 32,
      axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 12 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
    },
    yAxis: {
      name: '重伤（死亡）', nameLocation: 'middle', nameGap: 50,
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: 9,
        data: items.map((r) => [r.kills, r.deaths, r.player_name, r.profession || '未知', calcKDA(r)]),
        itemStyle: {
          color: (p: { data: (number | string)[] }) => profColor(String(p.data[3])),
          opacity: 0.75,
          borderColor: 'rgba(0,0,0,0.08)',
          borderWidth: 1,
        },
        emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
        markLine: {
          silent: true,
          lineStyle: { color: 'rgba(0,0,0,0.1)', type: 'dashed', width: 1 },
          data: [
            { type: 'average', name: '平均击杀' },
            { type: 'average', valueIndex: 1, name: '平均重伤' },
          ],
          label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
        },
      },
    ],
  }
}

/** 成员 KDA 散点：击杀 vs 重伤，气泡大小=伤害 */
export function memberKdaScatterOption(members: SquadMember[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: (number | string)[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>击杀: ${d[0]}<br/>重伤: ${d[1]}<br/>KDA: ${Number(d[5]).toFixed(2)}<br/>伤害: ${fmtNum(Number(d[2]))}`
      },
    },
    grid: { left: 16, right: 20, top: 20, bottom: 16, containLabel: true },
    xAxis: {
      name: '击杀', nameLocation: 'middle', nameGap: 28,
      axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 10 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [6, 0, 0, 0] },
    },
    yAxis: {
      name: '重伤', nameLocation: 'middle', nameGap: 40,
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [{
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(8, Math.min(22, Math.sqrt(data[2]) / 400)),
      data: members.map((m) => [m.kills, m.deaths, m.player_damage, m.player_name, m.profession || '未知', m.kda]),
      itemStyle: {
        color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
        opacity: 0.8,
        borderColor: 'rgba(0,0,0,0.1)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      label: {
        show: true,
        formatter: (p: unknown) => (p as { data: (string | number)[] }).data[3],
        fontSize: 10,
        color: '#555',
        position: 'top',
      },
    }],
  }
}

/** 小队分析图表 option 构建：总览柱状图与成员明细图表（自 SquadAnalysisTab.vue 拆出，纯函数）。 */
import type { SquadMember } from '@/types/matchData'

import { fmtNum } from './analysis'
import { CHART_THEME } from './chartTheme'

export const CONTRIB_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b']

/** 顶部图表通用柱状图底座 */
export function squadBarOption(names: string[], data: number[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    grid: { left: 16, right: 20, top: 30, bottom: 56, containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 30, fontSize: 10, width: 60, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      {
        name: '数值',
        type: 'bar',
        barWidth: 16,
        itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] },
        data,
      },
    ],
  }
}

/** 成员四维对比：玩家伤害/建筑伤害/治疗/承伤 分组柱状图 */
export function memberContribOption(members: SquadMember[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: ['玩家伤害', '建筑伤害', '治疗', '承伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
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
    series: [
      {
        name: '玩家伤害',
        type: 'bar',
        barWidth: 7,
        barGap: '15%',
        itemStyle: { color: CONTRIB_COLORS[0], borderRadius: [2, 2, 0, 0] },
        data: members.map((m) => m.player_damage),
      },
      {
        name: '建筑伤害',
        type: 'bar',
        barWidth: 7,
        itemStyle: { color: CONTRIB_COLORS[1], borderRadius: [2, 2, 0, 0] },
        data: members.map((m) => m.building_damage),
      },
      {
        name: '治疗',
        type: 'bar',
        barWidth: 7,
        itemStyle: { color: CONTRIB_COLORS[2], borderRadius: [2, 2, 0, 0] },
        data: members.map((m) => m.healing),
      },
      {
        name: '承伤',
        type: 'bar',
        barWidth: 7,
        itemStyle: { color: CONTRIB_COLORS[3], borderRadius: [2, 2, 0, 0] },
        data: members.map((m) => m.damage_taken),
      },
    ],
  }
}

/** 成员能力雷达图（全员叠加） */
export function memberRadarOption(members: SquadMember[]) {
  if (!members.length) return {}
  const maxOf = (fn: (m: SquadMember) => number) => Math.max(...members.map(fn), 1) * 1.15
  const dims = [
    { name: '击杀', max: maxOf((m) => m.kills) },
    { name: '助攻', max: maxOf((m) => m.assists) },
    { name: '伤害', max: maxOf((m) => m.player_damage) },
    { name: '治疗', max: maxOf((m) => m.healing) },
    { name: '承伤', max: maxOf((m) => m.damage_taken) },
    { name: 'KDA', max: maxOf((m) => m.kda) },
  ]
  const RADAR_MEMBER_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b', '#8B5CF6', '#f6ff00']
  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: members.map((m) => m.player_name), ...CHART_THEME.legend, type: 'scroll' },
    radar: {
      center: ['50%', '44%'],
      radius: '58%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 40 },
      indicator: dims.map((d) => ({ name: d.name, max: Math.round(d.max) })),
    },
    series: [
      {
        type: 'radar',
        data: members.map((m, i) => ({
          name: m.player_name,
          value: [m.kills, m.assists, m.player_damage, m.healing, m.damage_taken, m.kda],
          areaStyle: { opacity: 0.06 },
          lineStyle: { width: 2, color: RADAR_MEMBER_COLORS[i % RADAR_MEMBER_COLORS.length] },
          itemStyle: { color: RADAR_MEMBER_COLORS[i % RADAR_MEMBER_COLORS.length] },
          symbol: 'circle',
          symbolSize: 4,
        })),
      },
    ],
  }
}

/** 成员占比构成：击杀/助攻/人伤/拆塔/承伤/治疗 占比 堆叠条形图 */
export function memberRatioBarOption(members: SquadMember[]) {
  const ratios = [
    { key: 'kill_ratio', label: '击杀占比' },
    { key: 'assist_ratio', label: '助攻占比' },
    { key: 'player_damage_ratio', label: '人伤占比' },
    { key: 'building_ratio', label: '拆塔占比' },
    { key: 'taken_ratio', label: '承伤占比' },
    { key: 'heal_ratio', label: '治疗占比' },
  ]
  const COLORS = ['#c9a13b', '#e8d48b', '#5b7a9d', '#2e8b57', '#c0392b', '#FF9CF2']
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => (v * 100).toFixed(1) + '%' },
    legend: { bottom: 0, data: ratios.map((r) => r.label), ...CHART_THEME.legend, type: 'scroll' },
    grid: { left: 12, right: 16, top: 20, bottom: 40, containLabel: true },
    xAxis: {
      type: 'value',
      max: 1,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => v * 100 + '%' },
    },
    yAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 50, overflow: 'truncate' },
    },
    series: ratios.map((r, i) => ({
      name: r.label,
      type: 'bar',
      stack: 'total',
      barWidth: 14,
      itemStyle: { color: COLORS[i] },
      data: members.map((m) => (m[r.key as keyof SquadMember] as number) ?? 0),
    })),
  }
}

export { memberKdaScatterOption } from './kdaScatterCharts'

/** 成员击杀/助攻/重伤 分组柱状图 */
export function memberKillsStackOption(members: SquadMember[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: ['击杀', '助攻', '重伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      {
        name: '击杀',
        type: 'bar',
        barWidth: 8,
        itemStyle: { color: '#c9a13b', borderRadius: [2, 2, 0, 0] },
        data: members.map((m) => m.kills),
      },
      { name: '助攻', type: 'bar', barWidth: 8, itemStyle: { color: '#e8d48b' }, data: members.map((m) => m.assists) },
      { name: '重伤', type: 'bar', barWidth: 8, itemStyle: { color: '#c0392b' }, data: members.map((m) => m.deaths) },
    ],
  }
}

/** 成员效率指标：秒伤 / 每死输出 / 每死治疗 分组柱状图 */
export function memberEfficiencyOption(members: SquadMember[]) {
  const series = [
    { key: 'dps', label: '秒伤', color: '#5b7a9d' },
    { key: 'damage_per_death', label: '每死输出', color: '#c9a13b' },
    { key: 'healing_per_death', label: '每死治疗', color: '#2e8b57' },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: series.map((s) => s.label), ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
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
    series: series.map((s) => ({
      name: s.label,
      type: 'bar',
      barWidth: 8,
      itemStyle: { color: s.color, borderRadius: [2, 2, 0, 0] },
      data: members.map((m) => (m[s.key as keyof SquadMember] as number) ?? 0),
    })),
  }
}

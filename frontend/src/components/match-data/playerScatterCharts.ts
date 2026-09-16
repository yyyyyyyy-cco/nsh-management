/** 玩家维度散点类图表 option 构建（自 PlayerAnalysis.vue 拆出，纯函数）。 */
import type { MatchData } from '@/types/matchData'

import { calcKDA, computeScores, fmtNum, profColor } from './analysis'
import { CHART_THEME } from './chartTheme'

/** 击杀 vs 伤害分析（散点，气泡大小 = KDA） */
export function buildScatterOption(items: MatchData[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: number[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>击杀: ${d[0]}<br/>伤害: ${fmtNum(d[1])}<br/>治疗: ${fmtNum(d[2])}<br/>KDA: ${d[5].toFixed(1)}`
      },
    },
    grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
    xAxis: {
      name: '击杀',
      nameLocation: 'middle',
      nameGap: 32,
      axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 12 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
    },
    yAxis: {
      name: '玩家伤害',
      nameLocation: 'middle',
      nameGap: 50,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: number[]) => Math.max(6, Math.min(13, data[5] * 2)),
        data: items.map((r) => [
          r.kills,
          r.player_damage,
          r.healing,
          r.player_name,
          r.profession || '未知',
          calcKDA(r),
        ]),
        itemStyle: {
          color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
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
            { type: 'average', valueIndex: 1, name: '平均伤害' },
          ],
          label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
        },
      },
    ],
  }
}

/** 治疗 vs 承伤散点：气泡大小=综合评分，颜色=职业，评估治疗职业表现。 */
export function buildHealTakenOption(items: MatchData[]) {
  const scored = computeScores(items)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: number[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>治疗: ${fmtNum(d[0])}<br/>承伤: ${fmtNum(d[1])}<br/>评分: ${d[2]}<br/>KDA: ${d[5].toFixed(1)}`
      },
    },
    grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
    xAxis: {
      name: '治疗量',
      nameLocation: 'middle',
      nameGap: 32,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), margin: 12 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
    },
    yAxis: {
      name: '承受伤害',
      nameLocation: 'middle',
      nameGap: 50,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: number[]) => Math.max(6, Math.min(13, (data[5] as number) * 2)),
        data: scored.map((s) => [s.player.healing, s.player.damage_taken, s.total, s.player.player_name, s.player.profession || '未知', s.kda]),
        itemStyle: {
          color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
          opacity: 0.75,
          borderColor: 'rgba(0,0,0,0.08)',
          borderWidth: 1,
        },
        emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
        markLine: {
          silent: true,
          lineStyle: { color: 'rgba(0,0,0,0.1)', type: 'dashed', width: 1 },
          data: [
            { type: 'average', name: '平均治疗' },
            { type: 'average', valueIndex: 1, name: '平均承伤' },
          ],
          label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
        },
      },
    ],
  }
}

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

/** 伤害 vs 治疗气泡：气泡大小 = 承伤（开根号缩放）。 */
export function buildDmgHealBubbleOption(items: MatchData[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: (number | string)[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>伤害: ${fmtNum(Number(d[0]))}<br/>治疗: ${fmtNum(Number(d[1]))}<br/>承伤: ${fmtNum(Number(d[2]))}`
      },
    },
    grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
    xAxis: {
      name: '玩家伤害', nameLocation: 'middle', nameGap: 32,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), margin: 12 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
    },
    yAxis: {
      name: '治疗量', nameLocation: 'middle', nameGap: 50,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: number[]) => Math.max(4, Math.min(14, Math.sqrt(data[2]) / 300)),
        data: items.map((r) => [r.player_damage, r.healing, r.damage_taken, r.player_name, r.profession || '未知']),
        itemStyle: {
          color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
          opacity: 0.7,
          borderColor: 'rgba(0,0,0,0.08)',
          borderWidth: 1,
        },
        emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  }
}

/** 玩家综合能力雷达图 option 构建（自 PlayerAnalysis.vue 拆出，纯函数）。 */
import type { MatchData } from '@/types/matchData'

import { calcKDA } from './analysis'
import { CHART_THEME } from './chartTheme'

export const RADAR_COLORS = ['#c9a13b', '#5b7a9d']

/** 双玩家对比雷达图（左侧/右侧玩家名，空值返回 {}）。 */
export function buildRadarOption(items: MatchData[], left: string, right: string) {
  const pL = items.find((r) => r.player_name === left)
  const pR = items.find((r) => r.player_name === right)
  const players = [pL, pR].filter(Boolean) as MatchData[]
  if (!players.length) return {}
  const maxOf = (key: 'kills' | 'assists' | 'player_damage' | 'healing' | 'damage_taken' | 'kda') => {
    const vals =
      key === 'kda'
        ? items.map((r) => calcKDA(r))
        : items.map((r) => r[key] as number)
    return Math.max(...vals, 1) * 1.15
  }
  const dims = [
    { name: '击杀', max: maxOf('kills') },
    { name: '助攻', max: maxOf('assists') },
    { name: '伤害', max: maxOf('player_damage') },
    { name: '治疗', max: maxOf('healing') },
    { name: '承伤', max: maxOf('damage_taken') },
    { name: 'KDA', max: maxOf('kda') },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: players.map((p) => p.player_name), ...CHART_THEME.legend },
    radar: {
      center: ['50%', '46%'],
      radius: '62%',
      axisName: { ...CHART_THEME.axis.axisName, color: '#6d665c' },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0.02)', 'transparent'] } },
      indicator: dims.map((d) => ({ name: d.name, max: Math.round(d.max) })),
    },
    series: [
      {
        type: 'radar',
        data: players.map((p, i) => ({
          name: p.player_name,
          value: [p.kills, p.assists, p.player_damage, p.healing, p.damage_taken, calcKDA(p)],
          areaStyle: { opacity: 0.1 },
          lineStyle: { width: 2.5, color: RADAR_COLORS[i] },
          itemStyle: { color: RADAR_COLORS[i] },
          symbol: 'circle',
          symbolSize: 5,
        })),
      },
    ],
  }
}

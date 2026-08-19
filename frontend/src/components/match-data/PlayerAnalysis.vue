<template>
  <div class="player-analysis">
    <!-- 击杀 vs 伤害散点图 -->
    <div class="chart-card">
      <div class="chart-card__title">击杀 vs 伤害分析</div>
      <EChart :option="scatterOption" :height="320" />
    </div>

    <!-- 职业×指标热力图 -->
    <div class="chart-card">
      <div class="chart-card__title">职业×指标热力图</div>
      <EChart :option="heatmapOption" :height="heatmapHeight" />
    </div>

    <!-- 阵营职业伤害/治疗构成堆叠柱状图 -->
    <div v-if="camps.length >= 2" class="stack-row">
      <div class="chart-card">
        <div class="chart-card__title">阵营职业伤害构成</div>
        <EChart :option="stackOption('player_damage')" :height="300" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">阵营职业治疗构成</div>
        <EChart :option="stackOption('healing')" :height="300" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { MatchData } from '@/types/matchData'
import { aggregateCamps, calcKDA, fmtNum, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const camps = computed(() => aggregateCamps(props.items))
const allProfs = computed(() => [...new Set(props.items.map((r) => r.profession || '未知'))].sort())

const scatterOption = computed(() => ({
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
      symbolSize: (data: number[]) => Math.max(8, Math.min(18, data[5] * 3)),
      data: props.items.map((r) => [
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
}))

const heatmapHeight = computed(() => Math.max(340, allProfs.value.length * 44 + 120))

const heatmapOption = computed(() => {
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'player_damage', label: '伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
    { key: 'assists', label: '助攻' },
  ]
  const raw: { xi: number; yi: number; avg: number; label: string; prof: string }[] = []
  allProfs.value.forEach((prof, yi) => {
    const players = props.items.filter((r) => (r.profession || '未知') === prof)
    if (!players.length) return
    metrics.forEach((m, xi) => {
      const avg = players.reduce((s, r) => s + (r[m.key as keyof MatchData] as number), 0) / players.length
      raw.push({ xi, yi, avg, label: m.label, prof })
    })
  })
  const maxVals = metrics.map((_, xi) => Math.max(...raw.filter((r) => r.xi === xi).map((r) => r.avg)))
  const minVals = metrics.map((_, xi) => Math.min(...raw.filter((r) => r.xi === xi).map((r) => r.avg)))
  const data = raw.map((r) => {
    const range = maxVals[r.xi] - minVals[r.xi]
    const normalized = range > 0 ? Math.round(((r.avg - minVals[r.xi]) / range) * 100) : 50
    return [r.xi, r.yi, normalized, fmtNum(r.avg), r.label, r.prof]
  })
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: number[] }).data
        return `<b>${d[5]}</b> · ${d[4]}<br/>平均值: ${d[3]}<br/>相对水平: ${d[2]}%`
      },
    },
    grid: { left: 72, right: 24, top: 12, bottom: 64 },
    xAxis: {
      type: 'category',
      data: metrics.map((m) => m.label),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0, fontSize: 13 },
      axisTick: { show: false },
      splitArea: { show: true, areaStyle: { color: ['transparent', 'rgba(0,0,0,0.015)'] } },
    },
    yAxis: {
      type: 'category',
      data: allProfs.value,
      axisLabel: { ...CHART_THEME.axis.axisLabel, fontSize: 13, fontWeight: 600, width: 56, overflow: 'truncate' },
      axisTick: { show: false },
      axisLine: { show: false },
    },
    visualMap: {
      min: 0,
      max: 100,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 4,
      itemWidth: 14,
      itemHeight: 100,
      inRange: { color: ['#fff7bc', '#fec44f', '#fe9929', '#ec7014', '#cc4c02', '#8c2d04'] },
      textStyle: { color: '#8a8378', fontSize: 11 },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: true,
          fontSize: 11,
          color: '#333',
          fontWeight: 500,
          formatter: (p: unknown) => (p as { data: number[] }).data[3],
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 3,
          borderRadius: 4,
        },
        emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(0, 0, 0, 0.4)', borderColor: '#fff', borderWidth: 2 } },
      },
    ],
  }
})

function stackOption(field: 'player_damage' | 'healing') {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { axisValue: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${list[0].axisValue}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${p.seriesName}: ${fmtNum(p.value)}<br/>`
        })
        return html
      },
    },
    legend: { top: 0, ...CHART_THEME.legend, type: 'scroll' },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: camps.value.map((c) => c.camp), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: allProfs.value.map((prof) => ({
      name: prof,
      type: 'bar',
      stack: 'total',
      barWidth: 40,
      itemStyle: { color: profColor(prof), borderRadius: 0 },
      data: camps.value.map((c) =>
        props.items.filter((r) => r.camp === c.camp && (r.profession || '未知') === prof).reduce((s, r) => s + r[field], 0),
      ),
    })),
  }
}
</script>

<style scoped>
.player-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stack-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
  margin-bottom: 10px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .stack-row {
    grid-template-columns: 1fr;
  }
}
</style>

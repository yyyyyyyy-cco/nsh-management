<template>
  <el-card shadow="never" class="trend-card">
    <template #header>
      <div class="trend-header">
        <span class="trend-title">趋势图</span>
      </div>
    </template>
    <el-tabs v-model="activeMetric" class="trend-tabs">
      <el-tab-pane v-for="m in metricOptions" :key="m.value" :label="m.label" :name="m.value">
        <EChart :option="buildOption(m)" :height="300" />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { PlayerRecord } from '@/types/myStats'
import { CHART_THEME } from '@/components/match-data/chartTheme'
import { fmtNum } from '@/components/match-data/analysis'
import EChart from '@/components/match-data/EChart.vue'

const props = defineProps<{ records: PlayerRecord[] }>()

interface MetricDef {
  label: string
  value: string
  color: string
  unit: string
  formatter: (v: number) => string
}

const metricOptions: MetricDef[] = [
  { label: '击杀', value: 'kills', color: '#c9a13b', unit: '', formatter: (v) => String(v) },
  { label: '对玩家伤害', value: 'player_damage', color: '#F04545', unit: '', formatter: fmtNum },
  { label: '对建筑伤害', value: 'building_damage', color: '#D97706', unit: '', formatter: fmtNum },
  { label: '治疗', value: 'healing', color: '#2E8B57', unit: '', formatter: fmtNum },
  { label: 'KDA', value: 'kda', color: '#5B7A9D', unit: '', formatter: (v) => v.toFixed(2) },
  { label: '承伤', value: 'damage_taken', color: '#605EF0', unit: '', formatter: fmtNum },
  { label: '助攻', value: 'assists', color: '#8B5CF6', unit: '', formatter: (v) => String(v) },
  { label: '秒伤', value: 'dps', color: '#3E6BF4', unit: '/s', formatter: (v) => String(v) },
  { label: '每死输出', value: 'damage_per_death', color: '#4F95FF', unit: '', formatter: fmtNum },
  { label: '重伤', value: 'deaths', color: '#C0392B', unit: '', formatter: (v) => String(v) },
]

const activeMetric = ref('kills')

// X 轴：按时间正序
const sorted = computed(() => [...props.records].reverse())
const xLabels = computed(() =>
  sorted.value.map((r) => `${r.match_time.slice(5, 10)} 第${r.round_no}局`)
)

function buildOption(m: MetricDef) {
  const data = sorted.value.map((r) => (r as unknown as Record<string, number>)[m.value])
  return {
    tooltip: {
      ...CHART_THEME.tooltip,
      trigger: 'axis' as const,
      formatter: (params: { name: string; value: number }[]) => {
        const p = params[0]
        return `${p.name}<br/><strong>${m.formatter(p.value)}${m.unit}</strong>`
      },
    },
    grid: { left: 60, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category' as const,
      data: xLabels.value,
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: xLabels.value.length > 10 ? 30 : 0 },
    },
    yAxis: {
      type: 'value' as const,
      name: m.unit ? m.label + m.unit : m.label,
      nameTextStyle: CHART_THEME.axis.axisName,
      splitLine: CHART_THEME.axis.splitLine,
      axisLabel: {
        ...CHART_THEME.axis.axisLabel,
        formatter: (v: number) => m.formatter(v),
      },
    },
    series: [{
      name: m.label,
      type: 'line' as const,
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: { width: 3, color: m.color },
      itemStyle: { color: m.color },
      areaStyle: {
        color: {
          type: 'linear' as const,
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: m.color + '30' },
            { offset: 1, color: m.color + '05' },
          ],
        },
      },
      data,
    }],
  }
}
</script>

<style scoped>
.trend-header {
  display: flex;
  align-items: center;
}

.trend-title {
  font-family: var(--font-serif);
  font-weight: 700;
  letter-spacing: 1px;
}

.trend-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  letter-spacing: 0.5px;
}

.trend-tabs :deep(.el-tabs__active-bar) {
  background: var(--gold-gradient);
}
</style>

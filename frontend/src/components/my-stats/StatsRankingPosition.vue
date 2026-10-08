<template>
  <el-card v-if="records.length" shadow="never" class="ranking-card">
    <template #header>
      <div class="ranking-header">
        <span class="ranking-title">排行榜趋势</span>
        <el-radio-group v-model="scope" size="small" class="scope-switch">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="camp">己方阵营</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <el-tabs v-model="activeRank" class="rank-tabs">
      <el-tab-pane v-for="r in rankLabels" :key="r" :label="r" :name="r">
        <EChart :option="buildOption(r)" :height="280" />
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { PlayerRecord } from '@/types/myStats'
import { CHART_THEME } from '@/components/match-data/chartTheme'
import EChart from '@/components/match-data/EChart.vue'

const props = defineProps<{ records: PlayerRecord[] }>()

const scope = ref<'all' | 'camp'>('all')
const activeRank = ref('击杀')

const rankLabels = computed(() => {
  const first = props.records[0]
  return first?.rankings?.map((r) => r.label) || []
})

// 根据 scope 选择对应排名数据
function getRankings(r: PlayerRecord) {
  return scope.value === 'camp' ? r.rankings_camp : r.rankings
}

// X 轴：按时间正序
const sorted = computed(() => [...props.records].reverse())
const xLabels = computed(() => sorted.value.map((r) => `${r.match_time.slice(5, 10)} 第${r.round_no}局`))

const rankColor = '#c9a13b'

function buildOption(label: string) {
  const rankData = sorted.value.map((r) => {
    const item = getRankings(r)?.find((rk) => rk.label === label)
    return item?.rank ?? null
  })

  const totalData = sorted.value.map((r) => {
    const item = getRankings(r)?.find((rk) => rk.label === label)
    return item?.total ?? 0
  })

  const maxTotal = Math.max(...totalData, 1)

  return {
    tooltip: {
      ...CHART_THEME.tooltip,
      trigger: 'axis' as const,
      formatter: (params: { name: string; value: number; dataIndex: number }[]) => {
        const rankVal = params[0]?.value
        const totalVal = totalData[params[0]?.dataIndex ?? 0]
        if (rankVal == null) return ''
        return `${params[0].name}<br/>排名：<strong>#${rankVal}</strong> / ${totalVal}`
      },
    },
    grid: { left: 50, right: 20, top: 20, bottom: 30 },
    xAxis: {
      type: 'category' as const,
      data: xLabels.value,
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: xLabels.value.length > 8 ? 30 : 0 },
    },
    yAxis: {
      type: 'value' as const,
      inverse: true,
      min: 1,
      max: maxTotal,
      nameTextStyle: CHART_THEME.axis.axisName,
      splitLine: CHART_THEME.axis.splitLine,
      axisLabel: {
        ...CHART_THEME.axis.axisLabel,
        formatter: (v: number) => '#' + v,
      },
    },
    series: [
      {
        name: label,
        type: 'line' as const,
        smooth: true,
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { width: 3, color: rankColor },
        itemStyle: { color: rankColor },
        areaStyle: {
          color: {
            type: 'linear' as const,
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: rankColor + '25' },
              { offset: 1, color: rankColor + '05' },
            ],
          },
        },
        data: rankData,
        connectNulls: true,
      },
    ],
  }
}
</script>

<style scoped>
.ranking-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.ranking-title {
  font-family: var(--font-serif);
  font-weight: 700;
  letter-spacing: 1px;
}

.rank-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  letter-spacing: 0.5px;
}

.rank-tabs :deep(.el-tabs__active-bar) {
  background: var(--gold-gradient);
}
</style>

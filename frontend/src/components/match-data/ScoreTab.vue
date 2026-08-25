<template>
  <div class="score-tab">
    <!-- 评分雷达图 + 散点图 -->
    <div class="score-row">
      <div class="chart-card">
        <div class="chart-card__title">TOP10 玩家评分雷达</div>
        <EChart :option="radarOption" :height="350" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">输出 vs 生存评分</div>
        <EChart :option="scatterOption" :height="350" />
      </div>
    </div>

    <!-- 综合评分排名表 -->
    <div class="chart-card">
      <div class="chart-card__title">综合评分排名</div>
      <el-table :data="scores" size="small" max-height="500" :cell-style="{ textAlign: 'center' }" :header-cell-style="{ textAlign: 'center' }">
        <el-table-column label="排名" width="55" align="center">
          <template #default="{ $index }">
            <span class="rank-badge num" :class="`rank-badge--${$index + 1}`">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="ID" min-width="110">
          <template #default="{ row }">
            <span class="player-cell">
              <i class="prof-dot" :style="{ background: profColor(row.player.profession) }" />
              <span class="rank-player">{{ row.player.player_name }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="player.profession" label="职业" min-width="70" />

        <el-table-column prop="player.camp" label="阵营" min-width="55" />
        <el-table-column label="总分" min-width="65" align="right" sortable :sort-by="'total'">
          <template #default="{ row }">
            <span class="score-num" :class="scoreClass(row.total)">{{ row.total }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="output" label="输出" min-width="55" align="right" sortable />
        <el-table-column prop="building" label="建筑" min-width="55" align="right" sortable />
        <el-table-column prop="healing" label="治疗" min-width="55" align="right" sortable />
        <el-table-column prop="survival" label="生存" min-width="55" align="right" sortable />
        <el-table-column prop="special" label="特殊" min-width="55" align="right" sortable />
        <el-table-column label="KDA" min-width="60" align="right" sortable :sort-by="'kda'">
          <template #default="{ row }">{{ row.kda.toFixed(1) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { MatchData } from '@/types/matchData'
import { computeScores, profColor, ROLE_CONFIG, type RoleType } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const scores = computed(() => computeScores(props.items))

const radarOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: CHART_THEME.tooltip,
  legend: { bottom: 0, ...CHART_THEME.legend },
  radar: {
    center: ['50%', '45%'],
    radius: '60%',
    axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 40 },
    indicator: [
      { name: '输出', max: 200 },
      { name: '建筑', max: 200 },
      { name: '治疗', max: 200 },
      { name: '生存', max: 200 },
      { name: '特殊', max: 200 },
    ],
  },
  series: [
    {
      type: 'radar',
      data: scores.value.slice(0, 10).map((s) => ({
        name: s.player.player_name,
        value: [s.output, s.building, s.healing, s.survival, s.special],
        areaStyle: { opacity: 0.1, color: profColor(s.player.profession) },
        lineStyle: { width: 2, color: profColor(s.player.profession) },
        itemStyle: { color: profColor(s.player.profession) },
        symbol: 'circle',
        symbolSize: 4,
      })),
    },
  ],
}))

const scatterOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = (p as { data: (number | string)[] }).data
      return `<b>${d[3]}</b> (${d[4]})<br/>总分: ${d[2]}<br/>输出: ${d[0]}<br/>生存: ${d[1]}`
    },
  },
  grid: { left: 12, right: 24, top: 20, bottom: 12, containLabel: true },
  xAxis: {
    name: '输出评分',
    nameLocation: 'middle',
    nameGap: 32,
    axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
  },
  yAxis: {
    name: '生存评分',
    nameLocation: 'middle',
    nameGap: 45,
    axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(10, data[2] / 3),
      data: scores.value.map((s) => [s.output, s.survival, s.total, s.player.player_name, s.player.profession || '未知']),
      itemStyle: {
        color: (p: unknown) => profColor(String((p as { data: (number | string)[] }).data[4])),
        opacity: 0.75,
        borderColor: 'rgba(255,255,255,0.3)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      label: {
        show: true,
        position: 'top',
        formatter: (p: unknown) => ((p as { data: (number | string)[] }).data[2] as number) >= 55 ? String((p as { data: (number | string)[] }).data[3]) : '',
        fontSize: 11,
        color: '#555',
      },
    },
  ],
}))

function scoreClass(total: number): string {
  return total >= 120 ? 'is-high' : total >= 80 ? 'is-mid' : 'is-low'
}

function getRoleTagType(roleType: RoleType): string {
  const typeMap: Record<RoleType, string> = {
    healer: 'success',
    tank: 'warning',
    tower: '',
    fighter: 'danger',
  }
  return typeMap[roleType] || 'info'
}
</script>

<style scoped>
.score-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-row {
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

.player-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.rank-player {
  font-weight: 600;
  color: var(--ink-900);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  color: var(--ink-400);
  background: var(--edge-faint);
}

.rank-badge--1 {
  background: linear-gradient(135deg, #f6c94d, #d4a017);
  color: #fff;
  box-shadow: 0 2px 6px rgba(212, 160, 23, 0.4);
}

.rank-badge--2 {
  background: linear-gradient(135deg, #c9c9c9, #9a9a9a);
  color: #fff;
}

.rank-badge--3 {
  background: linear-gradient(135deg, #e0a877, #b97f4b);
  color: #fff;
}

.score-num {
  font-weight: 800;
}

.score-num.is-high {
  color: var(--jade);
}

.score-num.is-mid {
  color: var(--gold-700);
}

.score-num.is-low {
  color: var(--ink-400);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .score-row {
    grid-template-columns: 1fr;
  }
}
</style>
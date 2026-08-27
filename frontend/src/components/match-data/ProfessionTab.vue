<template>
  <div class="profession-tab">
    <!-- 三个图表 -->
    <div class="chart-grid">
      <div class="chart-card">
        <div class="chart-card__title">职业人数占比</div>
        <EChart :option="pieOption('count', true)" :height="320" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">玩家伤害占比</div>
        <EChart :option="pieOption('total_player_damage', false)" :height="320" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">伤害 / 建筑对比（万）</div>
        <EChart :option="barOption" :height="320" />
      </div>
    </div>

    <!-- 明细表 -->
    <div class="chart-card">
      <div class="chart-card__title">职业明细（{{ props.items.length }} 人）</div>
      <el-table :data="profStats" size="small">
        <el-table-column prop="profession" label="职业" min-width="70">
          <template #default="{ row }">
            <span class="prof-cell">
              <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
              {{ row.profession }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="count" label="人数" min-width="55" align="right" sortable />
        <el-table-column prop="avg_kills" label="人均击杀" min-width="80" align="right" sortable />
        <el-table-column label="击杀占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ row.kills_pct.toFixed(1) }}%</template>
        </el-table-column>
        <el-table-column label="玩家伤害" min-width="110" align="right" sortable>
          <template #default="{ row }">
            {{ fmtNum(row.total_player_damage) }}
            <em class="pct">{{ row.damage_pct.toFixed(1) }}%</em>
          </template>
        </el-table-column>
        <el-table-column label="建筑伤害" min-width="110" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.total_building_damage) }}</template>
        </el-table-column>
        <el-table-column label="治疗" min-width="110" align="right" sortable>
          <template #default="{ row }">
            {{ fmtNum(row.total_healing) }}
            <em class="pct">{{ row.healing_pct.toFixed(1) }}%</em>
          </template>
        </el-table-column>
        <el-table-column label="承伤" min-width="110" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.total_damage_taken) }}</template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { MatchData } from '@/types/matchData'
import { aggregateProfessions, fmtNum, profColor, PROF_COLORS } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const profStats = computed(() => aggregateProfessions(props.items))

function hex(c: string): string {
  return c.length > 7 ? c.slice(0, 7) : c
}

function pieOption(field: 'count' | 'total_player_damage', showCount: boolean) {
  return {
    tooltip: {
      trigger: 'item',
      ...CHART_THEME.tooltip,
      formatter: showCount ? '{b}: {c}人 ({d}%)' : '{b}: {d}%',
    },
    // 图例固定底部横向（窄容器下右侧竖排图例会与饼图重叠）
    legend: { orient: 'horizontal', bottom: 0, type: 'scroll', ...CHART_THEME.legend },
    series: [
      {
        type: 'pie',
        radius: ['38%', '66%'],
        center: ['50%', '42%'],
        data: profStats.value
          .filter((p) => (field === 'count' ? true : p.total_player_damage > 0))
          .map((p) => ({
            name: p.profession,
            value: field === 'count' ? p.count : p.total_player_damage,
            itemStyle: { color: hex(PROF_COLORS[p.profession] || '#999'), borderColor: '#fff', borderWidth: 2 },
          })),
        label: { show: false },
        emphasis: { label: { show: true, fontSize: 14, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  }
}

const barOption = computed(() => {
  const profs = profStats.value.map((p) => p.profession)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v * 10000) },
    legend: { bottom: 0, ...CHART_THEME.legend },
    grid: { left: 12, right: 30, top: 12, bottom: 40, containLabel: true },
    xAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 50, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    yAxis: {
      type: 'category',
      data: profs,
      inverse: true,
      axisLabel: { ...CHART_THEME.axis.axisLabel, fontSize: 14, fontWeight: 600, width: 56, overflow: 'truncate' },
      axisLine: { show: false },
      axisTick: { show: false },
    },
    series: [
      {
        name: '玩家伤害(万)',
        type: 'bar',
        barWidth: 8,
        barGap: '60%',
        data: profStats.value.map((p) => ({
          value: +(p.total_player_damage / 10000).toFixed(0),
          itemStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: hex(PROF_COLORS[p.profession] || '#999') },
                { offset: 1, color: hex(PROF_COLORS[p.profession] || '#999') + 'aa' },
              ],
            },
            borderRadius: [0, 3, 3, 0],
          },
        })),
      },
      {
        name: '建筑伤害(万)',
        type: 'bar',
        barWidth: 8,
        data: profStats.value.map((p) => ({
          value: +(p.total_building_damage / 10000).toFixed(0),
          itemStyle: {
            color: {
              type: 'linear', x: 0, y: 0, x2: 1, y2: 0,
              colorStops: [
                { offset: 0, color: hex(PROF_COLORS[p.profession] || '#999') + '80' },
                { offset: 1, color: hex(PROF_COLORS[p.profession] || '#999') + '40' },
              ],
            },
            borderRadius: [0, 3, 3, 0],
          },
        })),
      },
    ],
  }
})
</script>

<style scoped>
.profession-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
  margin-bottom: 8px;
}

.prof-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pct {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 4px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .chart-grid {
    grid-template-columns: 1fr;
  }
}
</style>

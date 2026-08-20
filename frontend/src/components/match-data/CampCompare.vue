<template>
  <div v-if="camps.length >= 2" class="camp-compare">
    <!-- 阵营对比雷达图 -->
    <div class="chart-card">
      <div class="chart-card__title">阵营对比 · 雷达图</div>
      <EChart :option="radarOption" :height="360" />
    </div>

    <!-- 阵营职业人数构成 -->
    <div class="chart-card">
      <div class="chart-card__title">阵营职业人数构成</div>
      <EChart :option="profStackOption" :height="300" />
    </div>

    <!-- 阵营关键数据对比柱状图 -->
    <div class="chart-card">
      <div class="chart-card__title">阵营关键数据对比</div>
      <EChart :option="barOption" :height="300" />
    </div>

    <!-- 占比分析表（独立一行） -->
    <div class="chart-card">
      <div class="chart-card__title">占比分析</div>
      <el-table :data="ratioRows" size="small" max-height="300">
          <el-table-column prop="name" label="阵营" min-width="70" />
          <el-table-column prop="kills" label="击杀" min-width="80" align="right">
            <template #default="{ row }">{{ row.kills }}<em class="pct">{{ row.killsPct }}</em></template>
          </el-table-column>
          <el-table-column prop="playerDmg" label="玩家伤害" min-width="95" align="right">
            <template #default="{ row }">{{ row.playerDmg }}<em class="pct">{{ row.playerDmgPct }}</em></template>
          </el-table-column>
          <el-table-column prop="buildingDmg" label="建筑伤害" min-width="95" align="right">
            <template #default="{ row }">{{ row.buildingDmg }}<em class="pct">{{ row.buildingDmgPct }}</em></template>
          </el-table-column>
          <el-table-column prop="healing" label="治疗" min-width="80" align="right">
            <template #default="{ row }">{{ row.healing }}<em class="pct">{{ row.healingPct }}</em></template>
          </el-table-column>
          <el-table-column prop="taken" label="承伤" min-width="80" align="right">
            <template #default="{ row }">{{ row.taken }}<em class="pct">{{ row.takenPct }}</em></template>
          </el-table-column>
        </el-table>
      </div>
    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { MatchData } from '@/types/matchData'
import { aggregateCamps, CAMP_COLORS, fmtNum, pctStr, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const camps = computed(() => aggregateCamps(props.items))

const radarOption = computed(() => {
  const max = (key: (c: (typeof camps.value)[number]) => number) =>
    Math.max(...camps.value.map(key), 1) * 1.1
  const caps = camps.value.map((c) => c.camp)
  return {
    backgroundColor: 'transparent',
    tooltip: CHART_THEME.tooltip,
    legend: { bottom: 0, data: caps, ...CHART_THEME.legend },
    radar: {
      center: ['50%', '45%'],
      radius: '60%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 50 },
      indicator: [
        { name: '击杀', max: max((c) => c.kills) },
        { name: '助攻', max: max((c) => c.assists) },
        { name: '玩家伤害', max: max((c) => c.player_damage) },
        { name: '建筑伤害', max: max((c) => c.building_damage) },
        { name: '治疗', max: max((c) => c.healing) },
        { name: '承伤', max: max((c) => c.damage_taken) },
      ],
    },
    series: [
      {
        type: 'radar',
        data: camps.value.map((c, i) => ({
          name: c.camp,
          value: [c.kills, c.assists, c.player_damage, c.building_damage, c.healing, c.damage_taken],
          areaStyle: { opacity: 0.12 },
          lineStyle: { width: 2.5, color: CAMP_COLORS[i % CAMP_COLORS.length] },
          itemStyle: { color: CAMP_COLORS[i % CAMP_COLORS.length] },
          symbol: 'circle',
          symbolSize: 5,
        })),
      },
    ],
  }
})

/** 阵营职业人数构成堆叠图。 */
const profStackOption = computed(() => {
  const profs = [...new Set(props.items.map((r) => r.profession || '未知'))].sort()
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    legend: { top: 0, type: 'scroll', ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: camps.value.map((c) => c.camp), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: profs.map((prof) => ({
      name: prof,
      type: 'bar',
      stack: 'total',
      barWidth: 36,
      itemStyle: { color: profColor(prof), borderRadius: 0 },
      data: camps.value.map((c) =>
        props.items.filter((r) => r.camp === c.camp && (r.profession || '未知') === prof).length,
      ),
    })),
  }
})

const barOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    ...CHART_THEME.tooltip,
    valueFormatter: (v: number) => (v >= 10000 ? fmtNum(v) : String(v)),
  },
  legend: { top: 0, data: camps.value.map((c) => c.camp), ...CHART_THEME.legend },
  grid: { left: 16, right: 24, top: 40, bottom: 8, containLabel: true },
  xAxis: {
    type: 'category',
    data: ['击杀', '助攻', '玩家伤害(万)', '建筑伤害(万)', '治疗(万)', '承伤(万)'],
    axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
  },
  yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
  series: camps.value.map((c, i) => ({
    name: c.camp,
    type: 'bar',
    barWidth: 20,
    barGap: '30%',
    itemStyle: {
      color: {
        type: 'linear',
        x: 0, y: 0, x2: 0, y2: 1,
        colorStops: [
          { offset: 0, color: CAMP_COLORS[i % CAMP_COLORS.length] },
          { offset: 1, color: CAMP_COLORS[i % CAMP_COLORS.length] + '88' },
        ],
      },
      borderRadius: [4, 4, 0, 0],
    },
    data: [
      c.kills,
      c.assists,
      +(c.player_damage / 10000).toFixed(0),
      +(c.building_damage / 10000).toFixed(0),
      +(c.healing / 10000).toFixed(0),
      +(c.damage_taken / 10000).toFixed(0),
    ],
  })),
}))

const ratioRows = computed(() => {
  const sums = camps.value.reduce(
    (acc, c) => ({
      kills: acc.kills + c.kills,
      pd: acc.pd + c.player_damage,
      bd: acc.bd + c.building_damage,
      heal: acc.heal + c.healing,
      taken: acc.taken + c.damage_taken,
    }),
    { kills: 0, pd: 0, bd: 0, heal: 0, taken: 0 },
  )
  return camps.value.map((c) => ({
    name: c.camp,
    kills: fmtNum(c.kills),
    killsPct: pctStr(c.kills, sums.kills),
    playerDmg: fmtNum(c.player_damage),
    playerDmgPct: pctStr(c.player_damage, sums.pd),
    buildingDmg: fmtNum(c.building_damage),
    buildingDmgPct: pctStr(c.building_damage, sums.bd),
    healing: fmtNum(c.healing),
    healingPct: pctStr(c.healing, sums.heal),
    taken: fmtNum(c.damage_taken),
    takenPct: pctStr(c.damage_taken, sums.taken),
  }))
})
</script>

<style scoped>
.camp-compare {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 14px;
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

.pct {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 4px;
}
</style>

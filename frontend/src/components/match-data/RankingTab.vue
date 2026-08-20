<template>
  <div class="ranking-tab">
    <!-- KDA 分布折线图 -->
    <div class="chart-card">
      <div class="chart-card__header">
        <span class="chart-card__title">KDA 分布（击杀榜 Top 20）</span>
      </div>
      <EChart :option="kdaOption" :height="260" />
    </div>

    <!-- KDA 构成堆叠图 -->
    <div class="chart-card">
      <div class="chart-card__header">
        <span class="chart-card__title">KDA 构成（Top 10）</span>
      </div>
      <EChart :option="kdaStackOption" :height="260" />
    </div>

    <!-- 伤害分布折线图（玩家/建筑切换） -->
    <div class="chart-card">
      <div class="chart-card__header">
        <span class="chart-card__title">伤害分布（Top 20）</span>
        <el-radio-group v-model="damageMode" size="small" class="mode-radio">
          <el-radio-button value="player">对玩家伤害</el-radio-button>
          <el-radio-button value="building">对建筑伤害</el-radio-button>
        </el-radio-group>
      </div>
      <EChart :option="damageOption" :height="260" />
    </div>

    <!-- 贡献度帕累托图 -->
    <div class="chart-card">
      <div class="chart-card__header">
        <span class="chart-card__title">贡献度分析 · 伤害累计占比（Top 20）</span>
      </div>
      <EChart :option="paretoOption" :height="260" />
    </div>

    <!-- 治疗/承伤分布折线图（切换） -->
    <div class="chart-card">
      <div class="chart-card__header">
        <span class="chart-card__title">治疗 / 承伤分布（Top 20）</span>
        <el-radio-group v-model="healMode" size="small" class="mode-radio">
          <el-radio-button value="healing">治疗量</el-radio-button>
          <el-radio-button value="taken">承受伤害</el-radio-button>
        </el-radio-group>
      </div>
      <EChart :option="healOption" :height="260" />
    </div>

    <!-- 四大榜单表格 -->
    <div class="ranking-grid">
      <div v-for="(ranking, key) in rankings" :key="key" class="ranking-card">
        <div class="ranking-card__title">
          <span class="ranking-card__icon">🏅</span>
          {{ rankingTitles[key] }}
        </div>
        <el-table :data="ranking" size="small" max-height="300">
          <el-table-column type="index" width="56" label="#">
            <template #default="{ $index }">
              <span class="rank-badge num" :class="`rank-badge--${$index + 1}`">{{ $index + 1 }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="ID" min-width="80">
            <template #default="{ row }">
              <span class="rank-player">{{ row.player_name }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="profession" label="职业" min-width="60">
            <template #default="{ row }">
              <span class="rank-prof">{{ row.profession }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="value" label="数值" min-width="70" align="right">
            <template #default="{ row }">
              <span class="rank-value num">{{ formatNumber(row.value) }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { MatchData, RankingsResponse } from '@/types/matchData'
import { calcKDA, fmtNum } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[]; rankings: RankingsResponse }>()

const damageMode = ref<'player' | 'building'>('player')
const healMode = ref<'healing' | 'taken'>('healing')

const rankingTitles: Record<string, string> = {
  kills_ranking: '击杀榜',
  damage_ranking: '玩家伤害榜',
  building_ranking: '建筑伤害榜',
  healing_ranking: '治疗榜',
  taken_ranking: '承伤榜',
  fen_gu_ranking: '焚骨榜',
}

const kdaOption = computed(() => {
  const sorted = props.items.slice().sort((a, b) => calcKDA(b) - calcKDA(a)).slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    grid: { left: 12, right: 12, top: 32, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: [
      { type: 'value', name: 'KDA', axisLabel: { ...CHART_THEME.axis.axisLabel, width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine, nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 40, 0, 0] } },
      { type: 'value', name: '击杀', axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' }, splitLine: { show: false }, nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 0, 0, 40] } },
    ],
    series: [
      {
        name: 'KDA',
        type: 'line',
        data: sorted.map((r) => calcKDA(r).toFixed(1)),
        smooth: true,
        lineStyle: { width: 3, color: '#c9a13b' },
        itemStyle: { color: '#c9a13b' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(201,161,59,0.25)' }, { offset: 1, color: 'rgba(201,161,59,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
      {
        name: '击杀',
        type: 'line',
        yAxisIndex: 1,
        data: sorted.map((r) => r.kills),
        smooth: true,
        lineStyle: { width: 2, color: '#f04545', type: 'dashed' },
        itemStyle: { color: '#f04545' },
        symbol: 'diamond',
        symbolSize: 6,
      },
    ],
  }
})

const damageOption = computed(() => {
  const sorted = props.items
    .slice()
    .sort((a, b) => (damageMode.value === 'player' ? b.player_damage - a.player_damage : b.building_damage - a.building_damage))
    .slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    grid: { left: 12, right: 24, top: 28, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      {
        name: damageMode.value === 'player' ? '玩家伤害' : '建筑伤害',
        type: 'line',
        data: sorted.map((r) => (damageMode.value === 'player' ? r.player_damage : r.building_damage)),
        smooth: true,
        lineStyle: { width: 3, color: '#5b7a9d' },
        itemStyle: { color: '#5b7a9d' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: 'rgba(91,122,157,0.25)' }, { offset: 1, color: 'rgba(91,122,157,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
    ],
  }
})

const healOption = computed(() => {
  const sorted = props.items
    .slice()
    .sort((a, b) => (healMode.value === 'healing' ? b.healing - a.healing : b.damage_taken - a.damage_taken))
    .slice(0, 20)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    grid: { left: 12, right: 24, top: 28, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      {
        name: healMode.value === 'healing' ? '治疗量' : '承伤',
        type: 'line',
        data: sorted.map((r) => (healMode.value === 'healing' ? r.healing : r.damage_taken)),
        smooth: true,
        lineStyle: { width: 3, color: healMode.value === 'healing' ? '#2e8b57' : '#c0392b' },
        itemStyle: { color: healMode.value === 'healing' ? '#2e8b57' : '#c0392b' },
        areaStyle: { color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: healMode.value === 'healing' ? 'rgba(46,139,87,0.25)' : 'rgba(192,57,43,0.25)' }, { offset: 1, color: healMode.value === 'healing' ? 'rgba(46,139,87,0.02)' : 'rgba(192,57,43,0.02)' }] } },
        symbol: 'circle',
        symbolSize: 5,
        showSymbol: false,
      },
    ],
  }
})

function formatNumber(value: number): string {
  return fmtNum(value)
}

/** KDA 构成堆叠（击杀/助攻/重伤），看 KDA 高分是打得猛还是死得少。 */
const kdaStackOption = computed(() => {
  const sorted = props.items.slice().sort((a, b) => calcKDA(b) - calcKDA(a)).slice(0, 10)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { name: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${list[0].name}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${p.seriesName}: ${p.value}<br/>`
        })
        return html
      },
    },
    legend: { bottom: 0, data: ['击杀', '助攻', '重伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 20, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '击杀', type: 'bar', stack: 'kda', barWidth: 18, itemStyle: { color: '#c9a13b' }, data: sorted.map((r) => r.kills) },
      { name: '助攻', type: 'bar', stack: 'kda', itemStyle: { color: '#5b7a9d' }, data: sorted.map((r) => r.assists) },
      { name: '重伤', type: 'bar', stack: 'kda', itemStyle: { color: '#c0392b' }, data: sorted.map((r) => r.deaths) },
    ],
  }
})

/** 贡献度帕累托图：玩家伤害降序柱 + 累计占比折线，识别核心输出。 */
const paretoOption = computed(() => {
  const sorted = props.items.slice().sort((a, b) => b.player_damage - a.player_damage).slice(0, 20)
  const total = sorted.reduce((s, r) => s + r.player_damage, 0)
  let acc = 0
  const cum = sorted.map((r) => {
    acc += r.player_damage
    return total ? Math.round((acc / total) * 1000) / 10 : 0
  })
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { name: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${list[0].name}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${p.seriesName}: ${p.seriesName === '累计占比' ? p.value + '%' : fmtNum(p.value)}<br/>`
        })
        return html
      },
    },
    grid: { left: 12, right: 40, top: 32, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: sorted.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: [
      {
        type: 'value',
        name: '伤害',
        axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
        splitLine: CHART_THEME.axis.splitLine,
        nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 40, 0, 0] },
      },
      {
        type: 'value',
        name: '累计占比',
        max: 100,
        axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: '{value}%' },
        splitLine: { show: false },
        nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [0, 0, 0, 40] },
      },
    ],
    series: [
      {
        name: '玩家伤害',
        type: 'bar',
        barWidth: 14,
        data: sorted.map((r) => r.player_damage),
        itemStyle: {
          color: { type: 'linear', x: 0, y: 0, x2: 0, y2: 1, colorStops: [{ offset: 0, color: '#c9a13b' }, { offset: 1, color: '#c9a13b88' }] },
          borderRadius: [4, 4, 0, 0],
        },
      },
      {
        name: '累计占比',
        type: 'line',
        yAxisIndex: 1,
        data: cum,
        smooth: true,
        lineStyle: { width: 2, color: '#f04545', type: 'dashed' },
        itemStyle: { color: '#f04545' },
        symbol: 'circle',
        symbolSize: 5,
      },
    ],
  }
})
</script>

<style scoped>
.ranking-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
}

.chart-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
}

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 每行固定 2 个榜单 */
  gap: 16px;
}

.ranking-card {
  position: relative;
  overflow: hidden;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.ranking-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gold-line);
  opacity: 0.6;
}

.ranking-card__title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 12px 0;
  color: var(--ink-900);
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
}

.ranking-card__icon {
  font-size: 15px;
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

.rank-player {
  font-weight: 600;
  color: var(--ink-900);
}

.rank-prof {
  color: var(--ink-500);
  font-size: 12px;
}

.rank-value {
  font-weight: 700;
  color: var(--gold-700);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .chart-card__header {
    flex-wrap: wrap;
    gap: 6px;
  }

  .mode-radio {
    width: 100%;
  }

  .mode-radio :deep(.el-radio-button) {
    flex: 1;
  }

  .mode-radio :deep(.el-radio-button__inner) {
    width: 100%;
  }

  .ranking-grid {
    grid-template-columns: 1fr;
  }
}
</style>

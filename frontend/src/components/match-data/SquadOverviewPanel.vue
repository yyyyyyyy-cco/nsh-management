<template>
  <!-- 图表行 1：击杀 + 伤害 -->
  <div class="chart-row">
    <div class="chart-card">
      <div class="chart-card__title">小队击杀对比</div>
      <EChart :option="killsBarOption" :height="340" />
    </div>
    <div class="chart-card">
      <div class="chart-card__title">小队伤害对比（万）</div>
      <EChart :option="damageBarOption" :height="340" />
    </div>
  </div>

  <!-- 图表行 2：塔伤 + 重伤对比 -->
  <div class="chart-row">
    <div class="chart-card">
      <div class="chart-card__title">小队塔伤贡献（万）</div>
      <EChart :option="towerBarOption" :height="340" />
    </div>
    <div class="chart-card">
      <div class="chart-card__title">小队重伤对比</div>
      <EChart :option="deathsBarOption" :height="340" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { SquadAnalysis } from '@/types/matchData'

import EChart from './EChart.vue'
import { squadBarOption } from './squadCharts'

const props = defineProps<{ squads: SquadAnalysis[] }>()

const names = computed(() => props.squads.map((s) => s.squad_name))
const killsBarOption = computed(() =>
  squadBarOption(
    names.value,
    props.squads.map((s) => s.totals.kills),
  ),
)
const damageBarOption = computed(() =>
  squadBarOption(
    names.value,
    props.squads.map((s) => +(s.totals.player_damage / 10000).toFixed(0)),
  ),
)
const towerBarOption = computed(() =>
  squadBarOption(
    names.value,
    props.squads.map((s) => +(s.totals.building_damage / 10000).toFixed(0)),
  ),
)
const deathsBarOption = computed(() =>
  squadBarOption(
    names.value,
    props.squads.map((s) => s.totals.deaths),
  ),
)
</script>

<style scoped>
.chart-row {
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
}

/* 注：原实现两行图表紧贴（无纵向间距），此处保持一致，不新增规则 */

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

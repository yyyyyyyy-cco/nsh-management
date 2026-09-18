<!-- 战报区块：我方总览（六数字卡：击杀/助攻/伤害/建筑/治疗/焚骨） -->
<template>
  <div class="ov">
    <div class="ov-head">我方总览</div>
    <div class="ov-grid">
      <div v-for="c in cards" :key="c.label" class="ov-card">
        <div class="ov-value num">{{ fmtNum(c.value) }}</div>
        <div class="ov-label">{{ c.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { fmtNum } from '../analysis'
import type { ReportOverviewStats } from '../reportData'

const props = defineProps<{ stats: ReportOverviewStats }>()

const cards = computed(() => [
  { label: '总击杀', value: props.stats.totalKills },
  { label: '总助攻', value: props.stats.totalAssists },
  { label: '对玩家伤害', value: props.stats.totalDamage },
  { label: '对建筑伤害', value: props.stats.totalBuilding },
  { label: '总治疗', value: props.stats.totalHealing },
  { label: '总焚骨', value: props.stats.totalFenGu },
])
</script>

<style scoped>
.ov {
  padding: 20px 40px 6px;
}

.ov-head {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

.ov-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}

.ov-card {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 10px;
  text-align: center;
}

.ov-value {
  font-size: 19px;
  font-weight: 800;
  color: var(--gold-700);
}

.ov-label {
  margin-top: 4px;
  font-size: 12px;
  letter-spacing: 1px;
  color: var(--ink-500);
}

/* finesse · register=product · shell=match-report-poster: 我方总览六数字卡（960px 固定宽，导出用不响应式） */
</style>

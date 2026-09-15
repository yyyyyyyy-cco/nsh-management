<template>
  <div class="stats-overview">
    <div class="overview-grid">
      <div v-for="(card, i) in cards" :key="card.key" class="stat-card" :style="{ animationDelay: `${i * 60}ms` }">
        <div class="stat-card__header">
          <span class="stat-card__label">{{ card.label }}</span>
          <el-icon class="stat-card__icon"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-card__value">
          <span class="stat-card__number num">{{ card.value }}</span>
          <span v-if="card.suffix" class="stat-card__suffix">{{ card.suffix }}</span>
        </div>
        <div class="stat-card__track" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { DataLine, Document, FirstAidKit, Trophy } from '@element-plus/icons-vue'

import type { PlayerSummary } from '@/types/myStats'
import { fmtNum } from '@/components/match-data/analysis'

const props = defineProps<{ summary: PlayerSummary }>()

const cards = computed(() => [
  { key: 'matches', label: '参战场次', value: `${props.summary.total_matches} 场 / ${props.summary.total_rounds} 局`, icon: Document, suffix: '' },
  { key: 'profession', label: '主力职业', value: props.summary.main_profession || '-', icon: Trophy, suffix: '' },
  { key: 'kda', label: '场均 KDA', value: props.summary.avg_kda.toFixed(2), icon: DataLine, suffix: '' },
  { key: 'kills', label: '场均击杀', value: props.summary.avg_kills.toFixed(1), icon: Trophy, suffix: '' },
  { key: 'damage', label: '场均伤害', value: fmtNum(props.summary.avg_damage), icon: DataLine, suffix: '' },
  { key: 'healing', label: '场均治疗', value: fmtNum(props.summary.avg_healing), icon: FirstAidKit, suffix: '' },
])
</script>

<style scoped>
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 14px;
}

.stat-card {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 16px 18px;
  position: relative;
  overflow: hidden;
  animation: cardUp 0.4s ease-out both;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gold-gradient);
}

@keyframes cardUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.stat-card__label {
  font-size: 12px;
  color: var(--ink-500);
  letter-spacing: 1px;
}

.stat-card__icon {
  font-size: 14px;
  color: var(--gold-500);
}

.stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-card__number {
  font-family: var(--font-num);
  font-size: 22px;
  font-weight: 700;
  color: var(--gold-700);
}

.stat-card__suffix {
  font-size: 12px;
  color: var(--ink-400);
}

.stat-card__track {
  position: absolute;
  bottom: 0;
  left: 18px;
  right: 18px;
  height: 3px;
  border-radius: 2px;
  background: var(--edge-faint);
}

@media (max-width: 768px) {
  .overview-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  .stat-card__number {
    font-size: 18px;
  }
}
</style>

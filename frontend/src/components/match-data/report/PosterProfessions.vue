<!-- 战报区块：职业分布（人数条形，两列） -->
<template>
  <div v-if="items.length" class="pp">
    <div class="pp-head">
      <span>职业分布</span>
      <span class="pp-hint">人数 · 伤害占比</span>
    </div>
    <div class="pp-grid">
      <div v-for="item in items" :key="item.profession" class="pp-row">
        <span class="pp-name" :style="profTagStyle(item.profession)">{{ item.profession }}</span>
        <div class="pp-track">
          <i class="pp-fill" :style="{ width: pct(item.count) + '%', background: profColor(item.profession) }" />
        </div>
        <span class="pp-meta"><b class="num">{{ item.count }}</b> 人 · <b class="num">{{ item.damagePct }}%</b></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { profColor, profTagStyle } from '@/utils/profession'
import type { ReportProfessionItem } from '../reportData'

const props = defineProps<{ items: ReportProfessionItem[] }>()

const maxCount = computed(() => Math.max(1, ...props.items.map((i) => i.count)))

function pct(count: number): number {
  return Math.round((count / maxCount.value) * 100)
}
</script>

<style scoped>
.pp {
  padding: 20px 40px 6px;
}

.pp-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

.pp-hint {
  font-family: var(--font-sans);
  font-size: 11px;
  font-weight: 400;
  letter-spacing: 1px;
  color: var(--ink-400);
}

.pp-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px 28px;
}

.pp-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pp-name {
  flex-shrink: 0;
  width: 52px;
  text-align: center;
  padding: 1px 0;
  border-radius: var(--radius-xl);
  font-size: 11px;
  font-weight: 600;
  line-height: 1.8;
}

.pp-track {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: var(--edge-faint);
  overflow: hidden;
}

.pp-fill {
  display: block;
  height: 100%;
  border-radius: 4px;
  opacity: 0.85;
}

.pp-meta {
  flex-shrink: 0;
  width: 92px;
  text-align: right;
  font-size: 11.5px;
  color: var(--ink-500);
}

.pp-meta b {
  font-weight: 700;
  color: var(--ink-800);
}

/* finesse · register=product · shell=match-report-poster: 职业分布两列条形（960px 固定宽，导出用不响应式） */
</style>

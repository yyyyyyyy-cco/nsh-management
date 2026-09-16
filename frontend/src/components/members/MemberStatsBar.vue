<template>
  <div class="stats-bar">
    <template v-if="showSkeleton">
      <span class="stats-item">正式 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
      <span class="stats-sep" />
      <span class="stats-item">替补 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
      <span class="stats-sep" />
      <span class="stats-item">当前筛选共 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
    </template>
    <template v-else>
      <span class="stats-item">正式 <b class="num">{{ stats.formal_count }}</b> 人</span>
      <span class="stats-sep" />
      <span class="stats-item">替补 <b class="num">{{ stats.substitute_count }}</b> 人</span>
      <span class="stats-sep" />
      <span class="stats-item">当前筛选共 <b class="num">{{ total }}</b> 人</span>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { MemberStats } from '@/api/members'

defineProps<{ showSkeleton: boolean; stats: MemberStats; total: number }>()
</script>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 13px;
  color: var(--ink-500);
}

.stats-item b {
  font-size: 17px;
  color: var(--gold-700);
}

.stats-sep {
  width: 1px;
  height: 14px;
  background: var(--gold-300);
}
</style>

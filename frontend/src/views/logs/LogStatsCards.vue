<template>
  <div class="stats-row">
    <el-card shadow="never" class="stat-card">
      <div class="stat-value num">{{ stats?.today_requests ?? 0 }}</div>
      <div class="stat-label">今日操作数</div>
    </el-card>
    <el-card shadow="never" class="stat-card" :class="{ 'stat-card--error': (stats?.today_errors ?? 0) > 0 }">
      <div class="stat-value num">{{ stats?.today_errors ?? 0 }}</div>
      <div class="stat-label">今日错误数</div>
    </el-card>
    <el-card shadow="never" class="stat-card stat-card--wide">
      <div class="stat-label stat-label--top">近 7 天错误分布</div>
      <div class="weekly-bar">
        <div v-for="item in stats?.weekly_errors ?? []" :key="item.date" class="weekly-item">
          <div class="weekly-col">
            <div class="weekly-count num">{{ item.count }}</div>
            <div
              class="weekly-block"
              :class="{ 'weekly-block--empty': item.count === 0 }"
              :style="{ height: weeklyHeight(item.count) + 'px' }"
            />
          </div>
          <div class="weekly-date">{{ item.date.slice(5) }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { LogStats } from '@/types/log'

const props = defineProps<{ stats: LogStats | null }>()

function weeklyHeight(count: number): number {
  const max = Math.max(1, ...(props.stats?.weekly_errors ?? []).map((i) => i.count))
  return count === 0 ? 4 : Math.max(4, Math.round((count / max) * 56))
}
</script>

<style scoped>
/* ===== 概览统计 ===== */
.stats-row {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 0 0 180px;
  text-align: center;
}

.stat-card--error :deep(.el-card__body) {
  background: rgba(217, 83, 79, 0.04);
}

.stat-card--wide {
  flex: 1;
  text-align: left;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--ink-900, #2b2620);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: var(--ink-500, #8a8378);
}

.stat-label--top {
  margin: 0 0 8px;
}

/* 近 7 天错误柱状分布（纯 CSS，避免引入图表库） */
.weekly-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.weekly-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.weekly-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 76px;
}

.weekly-count {
  font-size: 12px;
  color: var(--ink-700, #4a443c);
  margin-bottom: 2px;
}

.weekly-block {
  width: 26px;
  border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, #d9534f 0%, #c9302c 100%);
}

.weekly-block--empty {
  background: var(--line-300, #e6dfce);
}

.weekly-date {
  font-size: 11px;
  color: var(--ink-500, #8a8378);
}

/* 窄屏适配 */
@media (max-width: 768px) {
  .stats-row {
    flex-direction: column;
  }

  .stat-card {
    flex: none;
  }
}
</style>

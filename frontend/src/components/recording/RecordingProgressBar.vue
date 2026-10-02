<template>
  <div class="progress-bar">
    <span class="round-chip" :class="{ active: roundFilter === null }" @click="$emit('clear-round')">全部</span>
    <div
      v-for="p in progress"
      :key="p.round_number"
      class="progress-item"
      :class="{ active: roundFilter === p.round_number }"
      @click="$emit('toggle-round', p.round_number)"
    >
      <span class="round-label">第{{ p.round_number }}局</span>
      <el-progress
        :percentage="p.total > 0 ? Math.round((p.approved / p.total) * 100) : 0"
        :format="() => `${p.approved}/${p.total}`"
        :stroke-width="16"
        :text-inside="true"
        :color="gradient"
      />
      <span class="progress-detail">
        待审 <em class="num">{{ p.pending }}</em>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { RoundProgress } from '@/types/recording'

defineProps<{ progress: RoundProgress[]; roundFilter: number | null }>()

defineEmits<{ 'toggle-round': [round: number]; 'clear-round': [] }>()

/** 进度条鎏金渐变（el-progress color 函数必须返回字符串，不可返回对象）。 */
const gradient = (percentage: number) =>
  percentage >= 100
    ? 'linear-gradient(90deg, #61a57e, #2e8b57)'
    : 'linear-gradient(90deg, #f2dfa0, #c9a13b)'
</script>

<style scoped>
.progress-bar {
  display: flex;
  gap: 20px;
  padding: 14px 20px;
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 60%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex: 1;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: var(--radius-md);
  border: 1px solid transparent;
  transition: background var(--dur-fast), border-color var(--dur-fast);
}

.progress-item:hover {
  background: rgba(212, 175, 55, 0.08);
}

.progress-item.active {
  background: var(--gold-50);
  border-color: var(--gold-200);
}

.round-chip {
  flex-shrink: 0;
  align-self: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-400);
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-xl);
  padding: 4px 14px;
  cursor: pointer;
  transition: color var(--dur-fast), background var(--dur-fast), border-color var(--dur-fast);
  white-space: nowrap;
}

.round-chip:hover {
  color: var(--gold-700);
  border-color: var(--gold-300);
}

.round-chip.active {
  color: var(--gold-700);
  background: var(--gold-100);
  border-color: var(--gold-300);
}

.progress-item.active .round-label {
  color: var(--gold-700);
}

.round-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-700);
  white-space: nowrap;
  font-family: var(--font-serif);
}

.progress-detail {
  font-size: 12px;
  color: var(--ink-500);
  white-space: nowrap;
}

.progress-detail em {
  font-style: normal;
  font-weight: 700;
  color: var(--ink-700);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 进度条：纵向堆叠为整行列表（每局一行），紧凑高度 */
  .progress-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
    padding: 12px 14px;
  }

  .round-chip {
    align-self: flex-start;
    display: inline-flex;
    align-items: center;
    min-height: 36px;
    padding: 0 16px;
  }

  .progress-item {
    width: 100%;
    min-height: 40px;
    padding: 4px 6px;
  }

  .progress-item :deep(.el-progress) {
    flex: 1;
    min-width: 0;
  }

  .progress-detail {
    font-size: 11px;
  }
}
</style>

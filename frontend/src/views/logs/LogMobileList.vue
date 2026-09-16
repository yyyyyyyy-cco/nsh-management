<template>
  <div class="log-rows">
    <SkeletonTable v-if="showSkeleton && !logs.length" variant="rows" :rows="5" />
    <el-empty v-else-if="!loading && !logs.length" description="暂无日志记录" :image-size="72" />
    <div v-for="row in logs" :key="row.id" class="log-row" @click="$emit('select', row)">
      <div class="log-row__main">
        <span class="log-row__name">{{ row.username || '匿名' }}</span>
        <el-tag :type="levelTagType(row.level)" effect="light" size="small">{{ levelLabel(row.level) }}</el-tag>
        <span class="log-row__module">{{ moduleLabels[row.module] ?? row.module }}</span>
        <span class="log-row__action log-row__action--tag">{{ actionLabels[row.action] ?? row.action }}</span>
      </div>
      <div class="log-row__meta">
        <span class="log-row__time num">{{ formatTime(row.created_at) }}</span>
        <span class="log-row__path">{{ row.method }} {{ row.path }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { OperationLog } from '@/types/log'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

import { actionLabels, formatTime, levelLabel, levelTagType, moduleLabels } from './logLabels'

defineProps<{ loading: boolean; showSkeleton: boolean; logs: OperationLog[] }>()

defineEmits<{ select: [row: OperationLog] }>()
</script>

<style scoped>
/* ===== 移动端日志行列表（isMobile 时渲染，替换表格） ===== */
.log-rows {
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

.log-row {
  padding: 10px 2px;
  border-bottom: 1px solid var(--edge-faint);
  cursor: pointer;
}

.log-row:last-child {
  border-bottom: none;
}

.log-row:active {
  background: var(--gold-50);
  margin: 0 -2px;
  padding: 10px 0;
}

.log-row__main {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.log-row__name {
  font-weight: 600;
  color: var(--ink-900);
  font-size: 14px;
}

.log-row__module {
  font-size: 11px;
  color: var(--ink-400);
  margin-left: auto;
}

.log-row__action--tag {
  font-size: 11px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 0 6px;
  line-height: 18px;
}

.log-row__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.log-row__time {
  font-size: 12px;
  color: var(--ink-400);
}

.log-row__path {
  font-size: 12px;
  color: var(--ink-500);
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>

<!-- 帮众首页·录屏待办一行状态条（悬停查看完整名单，点击直达录屏页） -->
<template>
  <button type="button" class="todo-strip" :title="fullTitle" @click="goRecording">
    <el-icon class="todo-strip__icon"><WarningFilled /></el-icon>
    <span class="todo-strip__text">{{ text }}</span>
    <span class="todo-strip__link">去处理</span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { WarningFilled } from '@element-plus/icons-vue'

import type { RecordingTodo } from './types'

const props = defineProps<{ todo: RecordingTodo }>()

const router = useRouter()

const text = computed(() => {
  const parts: string[] = []
  if (props.todo.missingNames.length) parts.push(`未交齐 ${props.todo.missingNames.length} 人`)
  if (props.todo.rejectedNames.length) parts.push(`驳回 ${props.todo.rejectedNames.length} 人待重交`)
  return `${props.todo.dateText} 场录屏：${parts.join(' · ')}`
})

/** 悬停查看完整名单 */
const fullTitle = computed(() => {
  const parts: string[] = []
  if (props.todo.missingNames.length) parts.push(`未交齐：${props.todo.missingNames.join('、')}`)
  if (props.todo.rejectedNames.length) parts.push(`驳回待重交：${props.todo.rejectedNames.join('、')}`)
  return parts.join('；')
})

function goRecording() {
  router.push({ name: 'schedule-detail', params: { id: props.todo.scheduleId }, query: { tab: 'recording', from: 'home' } })
}
</script>

<style scoped>
/* finesse · register=product · shell=member-home: 录屏待办一行状态条（金底细条，窄屏文字可换行） */
.todo-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  background: var(--gold-50);
  color: var(--gold-700);
  font-family: inherit;
  font-size: 13px;
  font-weight: 600;
  text-align: left;
  cursor: pointer;
  transition: background var(--dur-fast), border-color var(--dur-fast);
}

.todo-strip:hover {
  background: var(--gold-100);
  border-color: var(--gold-300);
}

.todo-strip:focus-visible {
  outline: 2px solid var(--gold-400);
  outline-offset: 2px;
}

.todo-strip__icon {
  flex-shrink: 0;
  font-size: 15px;
}

.todo-strip__text {
  flex: 1;
  min-width: 0;
  overflow-wrap: anywhere;
}

.todo-strip__link {
  flex-shrink: 0;
  text-decoration: underline;
  text-underline-offset: 2px;
}

@media (max-width: 768px) {
  .todo-strip {
    padding: 12px;
  }
}
</style>

<template>
  <el-dialog v-model="visible" :title="`匹配到 ${matches.length} 名成员`" width="420px" append-to-body>
    <p class="match-tip">
      关键词：<b class="keyword">{{ keyword }}</b
      >，点击选择要填入的成员
    </p>
    <div class="match-list">
      <div
        v-for="m in matches"
        :key="m.key"
        class="match-item"
        :class="{ selected: m.key === selectedKey }"
        @click="selectedKey = m.key"
      >
        <span class="match-item__name">{{ m.member_name }}</span>
        <span class="match-item__prof" :style="{ color: profColor(m.profession) }">{{ m.profession }}</span>
        <el-tag v-if="m.member_status === 'filler'" size="small" type="warning" effect="light">补</el-tag>
        <el-tag v-else-if="m.member_status === 'substitute'" size="small" type="info" effect="plain">替补</el-tag>
      </div>
    </div>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="onConfirm">确认填入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

import type { CandidateItem } from '@/composables/lineupBoard'
import { profColor } from '@/utils/profession'

const props = defineProps<{ matches: CandidateItem[]; keyword: string }>()
const emit = defineEmits<{ confirm: [item: CandidateItem] }>()
const visible = defineModel<boolean>({ required: true })

/** 当前选中的匹配项（默认第一个）。 */
const selectedKey = ref<string | null>(null)

watch(visible, (v) => {
  if (v) selectedKey.value = props.matches[0]?.key ?? null
})

function onConfirm() {
  const item = props.matches.find((m) => m.key === selectedKey.value)
  if (item) {
    emit('confirm', item)
    visible.value = false
  }
}
</script>

<style scoped>
.match-tip {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--ink-500);
}

.keyword {
  color: var(--gold-700);
}

.match-list {
  max-height: 300px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.match-list::-webkit-scrollbar {
  width: 6px;
}

.match-list::-webkit-scrollbar-thumb {
  background: var(--gold-300);
  border-radius: 3px;
}

.match-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--dur-fast);
}

.match-item:hover {
  border-color: var(--gold-300);
  background: var(--gold-50);
}

.match-item.selected {
  border-color: var(--gold-500);
  background: var(--gold-100);
}

.match-item__name {
  font-weight: 600;
  color: var(--ink-900);
}

.match-item__prof {
  flex: 1;
  font-size: 12px;
  font-weight: 600;
}
</style>

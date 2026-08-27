<template>
  <div class="player-search">
    <div class="search-row">
      <el-input
        v-model="inputName"
        placeholder="输入游戏 ID 查询战绩"
        clearable
        :prefix-icon="Search"
        class="search-input"
        @keyup.enter="onSearch"
      />
      <el-button type="primary" :loading="loading" @click="onSearch">查询</el-button>
    </div>
    <div v-if="history.length" class="history">
      <span class="history-label">最近查询</span>
      <el-tag
        v-for="name in history"
        :key="name"
        class="history-tag"
        effect="plain"
        @click="$emit('search', name)"
      >
        {{ name }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

defineProps<{ loading: boolean }>()
const emit = defineEmits<{ search: [name: string] }>()

const inputName = ref('')
const STORAGE_KEY = 'my-stats-history'
const MAX_HISTORY = 5
const history = ref<string[]>([])

onMounted(() => {
  try {
    history.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
  } catch {
    history.value = []
  }
})

function onSearch() {
  const name = inputName.value.trim()
  if (!name) return
  emit('search', name)
  saveHistory(name)
}

function saveHistory(name: string) {
  const list = history.value.filter((n) => n !== name)
  list.unshift(name)
  history.value = list.slice(0, MAX_HISTORY)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(history.value))
}
</script>

<style scoped>
.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input {
  max-width: 320px;
}

.history {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.history-label {
  font-size: 12px;
  color: var(--ink-400);
}

.history-tag {
  cursor: pointer;
  border-color: var(--gold-200);
  color: var(--gold-700);
  transition: all var(--dur-fast);
}

.history-tag:hover {
  background: var(--gold-50);
  border-color: var(--gold-400);
}
</style>

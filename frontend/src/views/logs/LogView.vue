<template>
  <div class="log-view">
    <!-- 概览统计 -->
    <LogStatsCards :stats="stats" />

    <!-- 日志列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <div class="header-actions">
            <el-button type="danger" plain @click="clearDialogVisible = true">清理日志</el-button>
            <el-button @click="onSearch">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <LogFilterBar
        :guilds="guilds"
        :filters="filters"
        v-model:dateRange="dateRange"
        @search="onSearch"
        @reset="onReset"
      />

      <!-- 移动端（≤768px）：日志行列表，点击展开详情 -->
      <LogMobileList
        v-if="isMobile"
        :loading="loading"
        :show-skeleton="showSkeleton"
        :logs="logs"
        @select="showDetail"
      />
      <LogTablePanel v-else :show-skeleton="showSkeleton" :logs="logs" @select="showDetail" />

      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <LogDetailDialog v-model="detailVisible" :row="detailRow" />

    <!-- 清理弹窗 -->
    <LogClearDialog v-model="clearDialogVisible" :clearing="clearing" @confirm="onClear" />
  </div>
</template>

<script setup lang="ts">
/** 系统日志页（仅开发者）：审计日志查询、概览统计与清理。 */
import { onMounted, onUnmounted, reactive, ref, watch } from 'vue'

import { clearLogs, getLogs, getLogStats } from '@/api/logs'
import { getGuilds } from '@/api/config'
import type { Guild } from '@/types/config'
import type { LogStats, OperationLog } from '@/types/log'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import LogClearDialog from './LogClearDialog.vue'
import LogDetailDialog from './LogDetailDialog.vue'
import LogFilterBar from './LogFilterBar.vue'
import LogMobileList from './LogMobileList.vue'
import LogStatsCards from './LogStatsCards.vue'
import LogTablePanel from './LogTablePanel.vue'

const stats = ref<LogStats | null>(null)
const logs = ref<OperationLog[]>([])
const total = ref(0)
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const page = ref(1)
const pageSize = ref(20)
const guilds = ref<Guild[]>([])

const filters = reactive<{
  username: string
  guild_id: number | null
  module: string | null
  level: string | null
}>({ username: '', guild_id: null, module: null, level: null })
const dateRange = ref<[Date, Date] | null>(null)

const detailVisible = ref(false)
const detailRow = ref<OperationLog | null>(null)
const clearDialogVisible = ref(false)
const clearing = ref(false)

// 移动端（≤768px）响应式切换
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

async function load() {
  loading.value = true
  try {
    const res = await getLogs({
      username: filters.username || undefined,
      guild_id: filters.guild_id ?? undefined,
      module: filters.module ?? undefined,
      level: filters.level ?? undefined,
      start_time: dateRange.value?.[0]?.toISOString() ?? undefined,
      end_time: dateRange.value?.[1]?.toISOString() ?? undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    logs.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  stats.value = await getLogStats()
}

function onSearch() {
  page.value = 1
  load()
  loadStats()
}

function onReset() {
  filters.username = ''
  filters.guild_id = null
  filters.module = null
  filters.level = null
  dateRange.value = null
  onSearch()
}

function showDetail(row: OperationLog) {
  detailRow.value = row
  detailVisible.value = true
}

async function onClear(days: number) {
  try {
    await ElMessageBox.confirm(`确定删除 ${days} 天前的所有日志吗？此操作不可恢复。`, '清理日志', { type: 'warning' })
  } catch {
    return
  }
  clearing.value = true
  try {
    const res = await clearLogs(days)
    ElMessage.success(res.message)
    clearDialogVisible.value = false
    onSearch()
  } finally {
    clearing.value = false
  }
}

watch([page, pageSize], load)

onMounted(async () => {
  mq.addEventListener('change', onMqChange)
  load()
  loadStats()
  guilds.value = await getGuilds()
})

onUnmounted(() => {
  mq.removeEventListener('change', onMqChange)
})
</script>

<style scoped>
.log-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ===== 列表 ===== */
.section-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}
</style>

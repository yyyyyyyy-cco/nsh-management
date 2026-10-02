<template>
  <el-card shadow="never" class="history-card">
    <template #header>
      <div class="card-head">
        <span class="card-title">申请记录</span>
        <span class="card-sub">
          <template v-if="memberName">成员：{{ memberName }}</template>
          <template v-else>选择成员后显示其历史申请</template>
        </span>
        <el-button v-if="memberId" text type="primary" :loading="loading" class="refresh" @click="load">
          刷新
        </el-button>
      </div>
    </template>

    <div v-if="!memberId" class="placeholder">
      <EmptyState variant="search" description="请先在上方选择常驻成员" :image-size="72" />
    </div>

    <SkeletonTable v-else-if="showSkeleton" :rows="4" :variant="isMobile ? 'rows' : 'table'" />

    <EmptyState v-else-if="loadFailed" variant="error" description="加载失败，请稍后重试" :image-size="72">
      <el-button @click="load">重新加载</el-button>
    </EmptyState>

    <EmptyState v-else-if="!records.length" description="该成员暂无改名申请记录" :image-size="72" />

    <template v-else>
      <!-- 移动端（≤768px）：行列表 -->
      <div v-if="isMobile" class="review-rows">
        <div v-for="record in records" :key="record.id" class="review-row">
          <div class="rr-line">
            <span class="record-id">{{ record.old_game_id }}</span>
            <span class="record-arrow">→</span>
            <span class="record-new">{{ record.new_game_id }}</span>
            <el-tag :type="statusType(record.status)" effect="light" size="small">{{ statusLabel(record.status) }}</el-tag>
          </div>
          <div class="record-meta">申请时间：{{ formatTime(record.created_at) }}</div>
          <div v-if="record.status === 'invalidated'" class="record-meta">{{ invalidatedLabel(record.invalidated_reason) }}</div>
          <div v-if="record.review_remark" class="remark">审核意见：{{ record.review_remark }}</div>
          <div v-else-if="record.status === 'rejected'" class="remark remark--empty">审核意见：未填写</div>
        </div>
      </div>

      <!-- 桌面端：表格 -->
      <el-table v-else :data="records" size="small" :default-sort="{ prop: 'created_at', order: 'descending' }">
        <el-table-column label="原 ID → 新 ID" min-width="200">
          <template #default="{ row }">
            <span class="record-id">{{ row.old_game_id }}</span>
            <span class="record-arrow">→</span>
            <span class="record-new">{{ row.new_game_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="申请时间" min-width="150">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="审核意见" min-width="180">
          <template #default="{ row }">
            <span v-if="row.review_remark" class="remark">{{ row.review_remark }}</span>
            <span v-else-if="row.status === 'invalidated'" class="remark">{{ invalidatedLabel(row.invalidated_reason) }}</span>
            <span v-else class="remark remark--empty">—</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" class="review-pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </template>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import dayjs from 'dayjs'

import { listMemberGameIdRequests } from '@/api/gameIdRequests'
import {
  GAME_ID_INVALIDATED_LABELS,
  GAME_ID_STATUS_LABELS,
  GAME_ID_STATUS_TYPES,
  type GameIdRequestItem,
  type GameIdRequestStatus,
} from '@/types/gameIdRequest'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const props = defineProps<{
  memberId: number | null
  memberName: string | null
  refreshKey: number
}>()

const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const loadFailed = ref(false)
const records = ref<GameIdRequestItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20

const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

// 请求序号：快速切换成员时丢弃过期响应
let loadSeq = 0

function statusLabel(status: GameIdRequestStatus): string {
  return GAME_ID_STATUS_LABELS[status] || status
}

function statusType(status: GameIdRequestStatus) {
  return GAME_ID_STATUS_TYPES[status] || 'info'
}

function invalidatedLabel(reason: string | null): string {
  if (!reason) return '申请已失效'
  return `申请已失效：${GAME_ID_INVALIDATED_LABELS[reason] || reason}`
}

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

async function load() {
  if (!props.memberId) {
    records.value = []
    total.value = 0
    return
  }
  const seq = ++loadSeq
  loading.value = true
  loadFailed.value = false
  try {
    const data = await listMemberGameIdRequests(props.memberId, { page: page.value, page_size: pageSize })
    if (seq !== loadSeq) return
    records.value = data.items
    total.value = data.total
    if (!data.items.length && page.value > 1) {
      page.value = Math.max(1, page.value - 1)
      await load()
    }
  } catch {
    if (seq === loadSeq) loadFailed.value = true
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

watch(
  () => [props.memberId, props.refreshKey],
  () => {
    page.value = 1
    load()
  },
)

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped src="./game-id-shared.css"></style>

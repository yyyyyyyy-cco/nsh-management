<template>
  <el-card shadow="never" class="review-card">
    <template #header>
      <div class="card-head">
        <span class="card-title">改名审核</span>
        <span class="card-sub">帮众提交的游戏 ID 修改申请，核实身份后通过或驳回</span>
      </div>
    </template>

    <div class="review-toolbar">
      <el-radio-group v-model="statusFilter" size="small" @change="onFilterChange">
        <el-radio-button value="pending">待审核</el-radio-button>
        <el-radio-button value="approved">已通过</el-radio-button>
        <el-radio-button value="rejected">已驳回</el-radio-button>
        <el-radio-button value="invalidated">已失效</el-radio-button>
        <el-radio-button value="all">全部</el-radio-button>
      </el-radio-group>
      <span class="review-toolbar__spacer" />
      <el-input
        v-model="keyword"
        size="small"
        clearable
        placeholder="按原/新 ID 搜索"
        class="search"
        @keyup.enter="onFilterChange"
        @clear="onFilterChange"
      />
      <el-button size="small" type="primary" plain @click="onFilterChange">查询</el-button>
    </div>

    <SkeletonTable v-if="showSkeleton" :rows="5" :variant="isMobile ? 'rows' : 'table'" />

    <EmptyState v-else-if="loadFailed" variant="error" description="加载失败，请稍后重试" :image-size="72">
      <el-button @click="load">重新加载</el-button>
    </EmptyState>

    <EmptyState
      v-else-if="!records.length"
      variant="search"
      :description="statusFilter === 'pending' ? '当前没有待审核的改名申请' : '没有符合条件的申请记录'"
      :image-size="72"
    />

    <template v-else>
      <!-- 移动端（≤768px）：行列表（原/新 ID 分行，操作按钮 32px 紧凑右对齐） -->
      <div v-if="isMobile" class="review-rows">
        <div v-for="record in records" :key="record.id" class="review-row">
          <div class="rr-line">
            <span class="record-id">{{ record.old_game_id }}</span>
            <span class="record-arrow">→</span>
            <span class="record-new">{{ record.new_game_id }}</span>
            <el-tag :type="statusType(record.status)" effect="light" size="small">{{ statusLabel(record.status) }}</el-tag>
          </div>
          <div class="record-meta">
            当前：{{ record.current_game_id || '成员已删除' }} · 提交账号：{{ record.requester_username }}
          </div>
          <div class="record-meta">申请时间：{{ formatTime(record.created_at) }}</div>
          <div v-if="record.status === 'invalidated'" class="record-meta">{{ invalidatedLabel(record.invalidated_reason) }}</div>
          <div v-if="record.review_remark" class="remark">审核意见：{{ record.review_remark }}</div>
          <div class="rr-line actions-line">
            <div class="rr-actions">
              <el-button v-if="isPending(record)" size="small" type="primary" plain @click="openDialog(record, 'approve')">通过</el-button>
              <el-button v-if="isPending(record)" size="small" type="danger" plain @click="openDialog(record, 'reject')">驳回</el-button>
              <span v-else class="record-meta">{{ reviewerText(record) }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 桌面端：表格 -->
      <el-table v-else :data="records" size="small">
        <el-table-column label="原 ID / 新 ID" min-width="190">
          <template #default="{ row }">
            <span class="record-id">{{ row.old_game_id }}</span>
            <span class="record-arrow">→</span>
            <span class="record-new">{{ row.new_game_id }}</span>
          </template>
        </el-table-column>
        <el-table-column label="当前成员名" min-width="110">
          <template #default="{ row }">
            <span v-if="row.current_game_id" class="record-id">{{ row.current_game_id }}</span>
            <span v-else class="remark remark--empty">成员已删除</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" effect="light" size="small">{{ statusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="提交账号" min-width="110">
          <template #default="{ row }">{{ row.requester_username }}</template>
        </el-table-column>
        <el-table-column label="申请时间" min-width="145">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="审核信息" min-width="180">
          <template #default="{ row }">
            <span v-if="row.review_remark" class="remark">{{ row.review_remark }}</span>
            <span v-else-if="row.status === 'invalidated'" class="remark">{{ invalidatedLabel(row.invalidated_reason) }}</span>
            <span v-else-if="row.reviewer_username" class="remark">{{ row.reviewer_username }} · {{ formatTime(row.reviewed_at) }}</span>
            <span v-else class="remark remark--empty">—</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" align="right">
          <template #default="{ row }">
            <template v-if="isPending(row)">
              <el-button size="small" type="primary" plain class="row-btn" @click="openDialog(row, 'approve')">通过</el-button>
              <el-button size="small" type="danger" plain class="row-btn" @click="openDialog(row, 'reject')">驳回</el-button>
            </template>
            <span v-else class="remark remark--empty">{{ reviewerText(row) }}</span>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" class="review-pager">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          background
          @current-change="load"
        />
      </div>
    </template>

    <GameIdReviewDialog v-model="dialogVisible" :record="activeRecord" :mode="dialogMode" @reviewed="onReviewed" />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import dayjs from 'dayjs'

import { listGameIdRequests } from '@/api/gameIdRequests'
import {
  GAME_ID_INVALIDATED_LABELS,
  GAME_ID_STATUS_LABELS,
  GAME_ID_STATUS_TYPES,
  type GameIdRequestAdminItem,
  type GameIdRequestStatus,
} from '@/types/gameIdRequest'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import GameIdReviewDialog from '@/components/members/GameIdReviewDialog.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const emit = defineEmits<{ reviewed: [] }>()

const statusFilter = ref('pending')
const keyword = ref('')
const records = ref<GameIdRequestAdminItem[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const loadFailed = ref(false)

const dialogVisible = ref(false)
const dialogMode = ref<'approve' | 'reject'>('approve')
const activeRecord = ref<GameIdRequestAdminItem | null>(null)

const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

let loadSeq = 0

function isPending(record: GameIdRequestAdminItem): boolean {
  return record.status === 'pending'
}

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

function reviewerText(record: GameIdRequestAdminItem): string {
  if (!record.reviewer_username) return '—'
  return `${record.reviewer_username} · ${formatTime(record.reviewed_at)}`
}

function formatTime(value: string | null): string {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm') : '—'
}

async function load() {
  const seq = ++loadSeq
  loading.value = true
  loadFailed.value = false
  try {
    const data = await listGameIdRequests({
      status: statusFilter.value,
      keyword: keyword.value.trim() || undefined,
      page: page.value,
      page_size: pageSize,
    })
    if (seq !== loadSeq) return
    records.value = data.items
    total.value = data.total
    // 当前筛选最后一条被处理掉时回退一页
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

function onFilterChange() {
  page.value = 1
  load()
}

function openDialog(record: GameIdRequestAdminItem, mode: 'approve' | 'reject') {
  activeRecord.value = record
  dialogMode.value = mode
  dialogVisible.value = true
}

/** 审核完成：刷新审核列表并通知父级刷新常驻库成员列表。 */
function onReviewed() {
  emit('reviewed')
  load()
}

defineExpose({ refresh: load })

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped src="./game-id-shared.css"></style>
<style scoped>
.search {
  width: 200px;
}

.actions-line {
  margin-top: 8px;
}

.row-btn + .row-btn {
  margin-left: 8px;
}

@media (max-width: 768px) {
  .search {
    width: 100%;
  }
}
</style>

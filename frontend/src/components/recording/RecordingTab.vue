<template>
  <div class="recording-tab">
    <!-- 审核进度 -->
    <div class="progress-bar">
      <div v-for="p in progress" :key="p.round_number" class="progress-item">
        <span class="round-label">第{{ p.round_number }}局</span>
        <el-progress
          :percentage="p.total > 0 ? Math.round((p.approved / p.total) * 100) : 0"
          :format="() => `${p.approved}/${p.total}`"
          :stroke-width="18"
          :text-inside="true"
        />
        <span class="progress-detail">
          待审 {{ p.pending }} | 驳回 {{ p.rejected }}
        </span>
      </div>
    </div>

    <!-- 管理员工具栏 -->
    <div v-if="auth.isAdmin" class="toolbar">
      <el-button type="success" plain :disabled="selectedIds.length === 0" @click="onBatchApprove">
        批量审核通过（{{ selectedIds.length }}）
      </el-button>
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
        <el-option label="待审核" value="pending" />
        <el-option label="已通过" value="approved" />
        <el-option label="已驳回" value="rejected" />
      </el-select>
    </div>

    <!-- 录屏列表 -->
    <el-table v-loading="loading" :data="filteredItems" @selection-change="onSelectionChange">
      <el-table-column v-if="auth.isAdmin" type="selection" width="44" />
      <el-table-column prop="member_name" label="姓名" min-width="100" fixed />
      <el-table-column label="局数" width="70" align="center">
        <template #default="{ row }">第{{ row.round_number }}局</template>
      </el-table-column>
      <el-table-column label="录屏链接" min-width="280">
        <template #default="{ row }">
          <div v-if="editingId === row.id" class="url-edit">
            <el-input v-model="editingUrl" placeholder="请输入录屏链接" size="small" />
            <el-button type="primary" size="small" @click="onSubmit(row)">保存</el-button>
            <el-button size="small" @click="editingId = null">取消</el-button>
          </div>
          <div v-else-if="row.url" class="url-display">
            <a :href="row.url" target="_blank" class="url-link">{{ row.url }}</a>
            <el-button v-if="!auth.isAdmin" link type="primary" size="small" @click="startEdit(row)">修改</el-button>
          </div>
          <div v-else>
            <el-button v-if="!auth.isAdmin" type="primary" link size="small" @click="startEdit(row)">
              提交链接
            </el-button>
            <span v-else class="empty-url">未提交</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" effect="light" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="审核备注" min-width="150">
        <template #default="{ row }">
          <span v-if="row.review_remark">{{ row.review_remark }}</span>
          <span v-else class="empty-remark">-</span>
        </template>
      </el-table-column>
      <el-table-column v-if="auth.isAdmin" label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <template v-if="row.url">
            <el-button v-if="row.status !== 'approved'" link type="success" @click="onApprove(row)">通过</el-button>
            <el-button v-if="row.status !== 'rejected'" link type="danger" @click="onReject(row)">驳回</el-button>
          </template>
          <span v-else class="empty-action">-</span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  approveRecording,
  batchApprove,
  getRecordings,
  rejectRecording,
  submitRecording,
} from '@/api/recording'
import type { Recording, RoundProgress } from '@/types/recording'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const items = ref<Recording[]>([])
const progress = ref<RoundProgress[]>([])
const selectedIds = ref<number[]>([])
const statusFilter = ref('')
const editingId = ref<number | null>(null)
const editingUrl = ref('')

const filteredItems = computed(() => {
  if (!statusFilter.value) return items.value
  return items.value.filter((r) => r.status === statusFilter.value)
})

onMounted(load)

async function load() {
  loading.value = true
  try {
    const data = await getRecordings(props.scheduleId)
    items.value = data.items
    progress.value = data.progress
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows: Recording[]) {
  selectedIds.value = rows.map((r) => r.id)
}

function startEdit(row: Recording) {
  editingId.value = row.id
  editingUrl.value = row.url || ''
}

async function onSubmit(row: Recording) {
  if (!editingUrl.value.trim()) {
    ElMessage.warning('请输入录屏链接')
    return
  }
  await submitRecording(props.scheduleId, row.id, editingUrl.value.trim())
  ElMessage.success('提交成功')
  editingId.value = null
  load()
}

async function onApprove(row: Recording) {
  const { value: remark } = await ElMessageBox.prompt('审核备注（可选）', '审核通过', {
    inputType: 'textarea',
    inputPlaceholder: '请输入备注',
    confirmButtonText: '通过',
    cancelButtonText: '取消',
  }).catch(() => ({ value: undefined }))
  if (remark === undefined) return

  await approveRecording(props.scheduleId, row.id, remark || undefined)
  ElMessage.success('审核通过')
  load()
}

async function onReject(row: Recording) {
  const { value: remark } = await ElMessageBox.prompt('请输入驳回原因', '审核驳回', {
    inputType: 'textarea',
    inputPlaceholder: '请输入驳回原因',
    confirmButtonText: '驳回',
    cancelButtonText: '取消',
    inputValidator: (value) => !!value?.trim() || '请输入驳回原因',
  }).catch(() => ({ value: undefined }))
  if (remark === undefined) return

  await rejectRecording(props.scheduleId, row.id, remark)
  ElMessage.success('已驳回')
  load()
}

async function onBatchApprove() {
  await ElMessageBox.confirm(
    `确定批量审核通过选中的 ${selectedIds.value.length} 条录屏吗？`,
    '提示',
    { type: 'warning' },
  )
  const result = await batchApprove(props.scheduleId, selectedIds.value)
  ElMessage.success(result.message)
  load()
}

function statusType(status: string) {
  return status === 'approved' ? 'success' : status === 'rejected' ? 'danger' : 'info'
}

function statusLabel(status: string) {
  return status === 'approved' ? '已通过' : status === 'rejected' ? '已驳回' : '待审核'
}
</script>

<style scoped>
.progress-bar {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #fff8e7;
  border-radius: 8px;
  margin-bottom: 12px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.round-label {
  font-size: 13px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
}

.progress-detail {
  font-size: 12px;
  color: #6b7280;
  white-space: nowrap;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.url-edit {
  display: flex;
  gap: 8px;
  align-items: center;
}

.url-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.url-link {
  color: #d4af37;
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
}

.url-link:hover {
  text-decoration: underline;
}

.empty-url,
.empty-remark,
.empty-action {
  color: #9ca3af;
}
</style>

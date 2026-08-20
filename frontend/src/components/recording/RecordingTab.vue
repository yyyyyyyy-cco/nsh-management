<template>
  <div class="recording-tab">
    <!-- 审核进度（点击按局数筛选） -->
    <div class="progress-bar">
      <span class="round-chip" :class="{ active: roundFilter === null }" @click="roundFilter = null">全部</span>
      <div
        v-for="p in progress"
        :key="p.round_number"
        class="progress-item"
        :class="{ active: roundFilter === p.round_number }"
        @click="toggleRound(p.round_number)"
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

    <!-- 工具栏：按ID搜索（帮众/管理员）+ 管理员操作 -->
    <div class="toolbar">
      <el-input v-model="nameFilter" placeholder="按ID搜索" clearable style="width: 200px" :prefix-icon="Search" />
      <template v-if="auth.isAdmin">
        <el-button type="success" plain :disabled="selectedIds.length === 0" @click="onBatchApprove">
          批量审核通过（{{ selectedIds.length }}）
        </el-button>
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
          <el-option label="待审核" value="pending" />
          <el-option label="未提交" value="unsubmitted" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
      </template>
    </div>

    <!-- 录屏列表 -->
    <el-table v-loading="loading" :data="filteredItems" :default-sort="{ prop: 'profession', order: 'ascending' }" @selection-change="onSelectionChange">
      <el-table-column v-if="auth.isAdmin" type="selection" width="44" />
      <el-table-column prop="member_name" label="ID" min-width="100" />
      <el-table-column prop="profession" label="职业" min-width="80" sortable>
        <template #default="{ row }">
          <span class="prof-cell">
            <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
            {{ row.profession || '-' }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="局数" min-width="60" align="center">
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
            <a v-if="auth.isAdmin" :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link">{{ row.url }}</a>
            <span v-else class="submitted-hint">已提交</span>
            <el-button
              v-if="auth.isAdmin"
              link
              type="primary"
              size="small"
              :icon="CopyDocument"
              title="复制链接"
              @click="onCopyUrl(row.url)"
            />
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
      <el-table-column label="状态" min-width="90" align="center">
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
      <el-table-column v-if="auth.isAdmin" label="操作" min-width="150">
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
import { CopyDocument, Search } from '@element-plus/icons-vue'

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
const nameFilter = ref('')
const roundFilter = ref<number | null>(null)
const editingId = ref<number | null>(null)
const editingUrl = ref('')

/** 进度条鎏金渐变（el-progress color 函数必须返回字符串，不可返回对象）。 */
const gradient = (percentage: number) =>
  percentage >= 100
    ? 'linear-gradient(90deg, #61a57e, #2e8b57)'
    : 'linear-gradient(90deg, #f2dfa0, #c9a13b)'

const filteredItems = computed(() => {
  let list = items.value
  const kw = nameFilter.value.trim()
  if (kw) {
    list = list.filter((r) => r.member_name.includes(kw))
  }
  if (roundFilter.value !== null) {
    list = list.filter((r) => r.round_number === roundFilter.value)
  }
  if (statusFilter.value === 'pending') {
    // 待审核：仅已填写链接且未审核，未提交的占位记录不计入
    list = list.filter((r) => r.status === 'pending' && r.url)
  } else if (statusFilter.value === 'unsubmitted') {
    // 未提交：尚未填写录屏链接
    list = list.filter((r) => r.status === 'pending' && !r.url)
  } else if (statusFilter.value) {
    list = list.filter((r) => r.status === statusFilter.value)
  }
  return list
})

/** 点击局数切换筛选（再次点击取消）。 */
function toggleRound(round: number) {
  roundFilter.value = roundFilter.value === round ? null : round
}

/** 职业色映射（依据 ui-style-guide）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profColor(prof: string | null | undefined) {
  return (prof && PROF_COLORS[prof]) || '#c9a13b'
}

/** 补全录屏链接协议（用户常只填域名/编号，缺协议浏览器无法直接打开）。 */
function normalizeUrl(url: string): string {
  return /^https?:\/\//i.test(url) ? url : `https://${url}`
}

/** 复制录屏链接到剪贴板。 */
async function onCopyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('录屏链接已复制')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

onMounted(load)

/** Tab 重新激活时刷新（出勤库变动后同步成员与进度）。 */
function reload() {
  load()
}

defineExpose({ reload })

async function load() {
  loading.value = true
  try {
    const data = await getRecordings(props.scheduleId)
    items.value = data.items
    progress.value = data.progress
  } catch {
    // 错误提示已由 http 拦截器统一处理，此处仅保证 loading 关闭
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows: Recording[]) {
  selectedIds.value = rows.map((r) => r.id)
}

function startEdit(row: Recording) {
  editingId.value = row.id
  // 帮众提交/修改时不回显原链接，避免泄露明文
  editingUrl.value = ''
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
  transition: all var(--dur-fast);
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
  color: var(--gold-700);
  text-decoration: none;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 220px;
  border-bottom: 1px dashed var(--gold-300);
  padding-bottom: 1px;
}

.url-link:hover {
  color: var(--gold-600);
  border-bottom-style: solid;
}

/* 帮众视角：链接脱敏，仅显示已提交状态 */
.submitted-hint {
  font-size: 12px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 1px 10px;
  font-weight: 500;
}

.empty-url,
.empty-remark,
.empty-action {
  color: var(--ink-300);
}

.prof-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--ink-800);
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .progress-bar {
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px 14px;
  }

  .progress-item {
    flex: 1 1 calc(50% - 8px);
    min-width: 0;
    padding: 4px 6px;
  }

  .progress-item :deep(.el-progress) {
    flex: 1;
    min-width: 0;
  }

  .progress-detail {
    font-size: 11px;
  }

  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .toolbar .el-button,
  .toolbar .el-select {
    flex: 1;
  }

  .toolbar .el-input {
    flex: 1 1 100%;
    width: 100% !important;
  }
}

@media (max-width: 480px) {
  .progress-item {
    flex-basis: 100%;
  }
}
</style>

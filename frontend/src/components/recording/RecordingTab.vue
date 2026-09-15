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

    <!-- 移动端（≤768px）：行列表，提交/审核动作 44px 触控 -->
    <div v-if="isMobile" class="rec-list">
      <SkeletonTable v-if="showSkeleton && filteredItems.length === 0" variant="rows" :rows="5" />
      <el-empty v-else-if="!loading && filteredItems.length === 0" description="暂无录屏记录" :image-size="72" />
      <div v-for="row in pagedItems" :key="row.id" class="rec-row" :class="{ 'rec-row--admin': auth.isAdmin }">
        <div class="rec-row__main">
          <el-checkbox
            v-if="auth.isAdmin"
            class="rec-row__check"
            :model-value="selectedIds.includes(row.id)"
            @change="toggleSelect(row.id)"
          />
          <span class="rec-row__name">{{ row.member_name }}</span>
          <!-- 帮众：ID 旁的提交状态胶囊 -->
          <template v-if="!auth.isAdmin">
            <span v-if="row.url" class="rec-row__state">已提交</span>
            <span v-if="row.note" class="rec-row__state">已备注</span>
          </template>
          <el-tag class="rec-row__status" :type="statusType(row.status)" effect="light" size="small">
            {{ statusLabel(row.status) }}
          </el-tag>
        </div>
        <div class="rec-row__meta">
          <span class="prof-cell">
            <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
            {{ row.profession || '-' }}
          </span>
          <span class="rec-row__round">第{{ row.round_number }}局</span>
        </div>

        <div v-if="row.review_remark" class="rec-row__remark">审核备注：{{ row.review_remark }}</div>

        <!-- 行内编辑：录屏链接 -->
        <div v-if="editingId === row.id" class="rec-row__edit">
          <el-input v-model="editingUrl" placeholder="请输入录屏链接" size="small" />
          <div class="rec-row__edit-btns">
            <el-button type="primary" @click="onSubmit(row)">保存</el-button>
            <el-button @click="editingId = null">取消</el-button>
          </div>
        </div>

        <!-- 行内编辑：备注（仅管理员可见，提交后不回显） -->
        <div v-else-if="editingNoteId === row.id" class="rec-row__edit">
          <el-input
            v-model="editingNote"
            type="textarea"
            :autosize="{ minRows: 2, maxRows: 5 }"
            placeholder="备注（仅管理员可见，可填写任何内容）"
          />
          <div class="rec-row__edit-btns">
            <el-button type="primary" @click="onSubmitNote(row)">保存备注</el-button>
            <el-button @click="editingNoteId = null">取消</el-button>
          </div>
        </div>

        <!-- 帮众：提交/修改链接 + 备注（状态胶囊见 ID 旁） -->
        <div v-else-if="!auth.isAdmin" class="rec-row__actions">
          <el-button class="rec-act rec-act--link" @click="startEdit(row)">
            {{ row.url ? '修改链接' : '提交链接' }}
          </el-button>
          <el-button class="rec-act rec-act--note" @click="startNoteEdit(row)">
            {{ row.note ? '修改备注' : '备注' }}
          </el-button>
        </div>

        <!-- 管理员：备注 + 链接 + 复制 + 审核 -->
        <div v-else class="rec-row__admin">
          <div v-if="row.note" class="rec-row__remark">备注：{{ row.note }}</div>
          <div class="rec-row__linkline">
            <template v-if="row.url">
              <a :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link rec-row__url">{{ row.url }}</a>
              <el-button link type="primary" size="small" :icon="CopyDocument" title="复制链接" @click="onCopyUrl(row.url)" />
            </template>
            <span v-else class="empty-url">未提交</span>
          </div>
          <div v-if="row.url" class="rec-row__actions">
            <el-button v-if="row.status !== 'approved'" class="rec-act" type="success" plain @click="onApprove(row)">通过</el-button>
            <el-button v-if="row.status !== 'rejected'" class="rec-act" type="danger" plain @click="onReject(row)">驳回</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 桌面端：表格形态保持不变；row-key + reserve-selection 支持跨页保留勾选 -->
    <SkeletonTable v-else-if="showSkeleton && filteredItems.length === 0" variant="table" :rows="5" />
      <el-table v-else :data="pagedItems" :row-key="rowKey" :default-sort="{ prop: 'member_name', order: 'ascending' }" @selection-change="onSelectionChange">
      <el-table-column v-if="auth.isAdmin" type="selection" width="44" reserve-selection />
      <el-table-column prop="member_name" label="ID" min-width="100" sortable />
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
      <el-table-column label="备注" min-width="150">
        <template #default="{ row }">
          <!-- 管理员：可见备注内容 -->
          <template v-if="auth.isAdmin">
            <span v-if="row.note">{{ row.note }}</span>
            <span v-else class="empty-remark">-</span>
          </template>
          <!-- 帮众：仅可见状态与编辑入口，不回显内容 -->
          <template v-else>
            <div v-if="editingNoteId === row.id" class="note-edit">
              <el-input
                v-model="editingNote"
                type="textarea"
                :autosize="{ minRows: 2, maxRows: 5 }"
                placeholder="备注（仅管理员可见）"
                size="small"
              />
              <div class="note-edit__btns">
                <el-button type="primary" size="small" @click="onSubmitNote(row)">保存</el-button>
                <el-button size="small" @click="editingNoteId = null">取消</el-button>
              </div>
            </div>
            <div v-else-if="row.note" class="note-display">
              <span class="submitted-hint">已备注</span>
              <el-button link type="primary" size="small" @click="startNoteEdit(row)">修改</el-button>
            </div>
            <div v-else>
              <el-button type="primary" link size="small" @click="startNoteEdit(row)">添加备注</el-button>
            </div>
          </template>
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

    <!-- 分页：录屏行为「成员 × 局数」量级（数十至数百行），分页渲染避免全量 DOM 与控件开销 -->
    <div v-if="filteredItems.length > 0" class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="filteredItems.length"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { CopyDocument, Search } from '@element-plus/icons-vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

import {
  approveRecording,
  batchApprove,
  getRecordings,
  rejectRecording,
  submitRecording,
  submitRecordingNote,
} from '@/api/recording'
import type { Recording, RoundProgress } from '@/types/recording'
import { useAuthStore } from '@/stores/auth'
import { profColor } from '@/utils/profession'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const items = ref<Recording[]>([])
const progress = ref<RoundProgress[]>([])
const selectedIds = ref<number[]>([])
const statusFilter = ref('')
const nameFilter = ref('')
const roundFilter = ref<number | null>(null)
const editingId = ref<number | null>(null)
const editingUrl = ref('')
const editingNoteId = ref<number | null>(null)
const editingNote = ref('')

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

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

// ===== 分页（录屏行数可达数百，分页渲染控制 DOM 规模）=====
const page = ref(1)
const pageSize = ref(50)
const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredItems.value.slice(start, start + pageSize.value)
})
/** 表格行 key（配合 reserve-selection 跨页保留勾选）。 */
const rowKey = (row: Recording) => row.id
// 筛选条件或页大小变化时回到第一页（避免停留在越界页码显示空白）
watch([nameFilter, roundFilter, statusFilter, pageSize], () => {
  page.value = 1
})

/** 点击局数切换筛选（再次点击取消）。 */
function toggleRound(round: number) {
  roundFilter.value = roundFilter.value === round ? null : round
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

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))

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

/** 移动端卡片勾选（与表格 selection 共用 selectedIds）。 */
function toggleSelect(id: number) {
  selectedIds.value = selectedIds.value.includes(id)
    ? selectedIds.value.filter((i) => i !== id)
    : [...selectedIds.value, id]
}

function startEdit(row: Recording) {
  editingNoteId.value = null
  editingId.value = row.id
  // 帮众提交/修改时不回显原链接，避免泄露明文
  editingUrl.value = ''
}

/** 备注编辑（帮众）；提交后内容不可见，同样不回显。 */
function startNoteEdit(row: Recording) {
  editingId.value = null
  editingNoteId.value = row.id
  editingNote.value = ''
}

/** 提交备注（自由内容，仅管理员可见，不改变审核状态）。 */
async function onSubmitNote(row: Recording) {
  if (!editingNote.value.trim()) {
    ElMessage.warning('请输入备注内容')
    return
  }
  await submitRecordingNote(props.scheduleId, row.id, editingNote.value.trim())
  ElMessage.success('备注已提交')
  editingNoteId.value = null
  load()
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
/* finesse · register=product · shell=member-detail: rec row-list(≤768px) + table(桌面) */
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

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

/* 分页条：底部右对齐 */
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
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

/* ===== 移动端行列表（isMobile 时渲染） ===== */
.rec-list {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态/加载遮罩的占位高度 */
  touch-action: manipulation;
}

.rec-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.rec-row:last-child {
  border-bottom: none;
}

.rec-row__main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rec-row__check {
  flex-shrink: 0;
  padding: 10px 6px 10px 0;
}

.rec-row__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--ink-900);
}

/* 次要信息行：职业 · 局数 */
.rec-row__meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  font-size: 12.5px;
  color: var(--ink-500);
}

.rec-row__meta .prof-cell {
  flex-shrink: 0;
}

.rec-row__round {
  flex-shrink: 0;
  font-size: 12.5px;
  color: var(--ink-500);
}

.rec-row__meta .rec-row__round::before {
  content: '·';
  margin-right: 6px;
  color: var(--ink-300);
}

.rec-row__status {
  flex-shrink: 0;
  margin-left: auto;
}

.rec-row__remark {
  margin-top: 6px;
  font-size: 12px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

.rec-row__edit {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.rec-row__edit-btns {
  display: flex;
  gap: 8px;
}

.rec-row__edit-btns .el-button {
  flex: 1;
  min-height: 44px;
  margin-left: 0;
}

.rec-row__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

/* 提交状态胶囊：已提交/已备注（手机端行内强提示） */
.rec-row__state {
  flex-shrink: 0;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--gold-700);
  background: var(--gold-100);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-xl);
  padding: 3px 10px;
  line-height: 1.4;
  white-space: nowrap;
}

.rec-row__actions .el-button.rec-act {
  flex: 1;
  min-height: 44px;
  margin-left: 0;
  border-radius: var(--radius-md);
  font-weight: 600;
}

/* 提交链接：鎏金描边（规避 primary+plain 与主题渐变叠加的浑浊观感） */
.rec-row__actions .el-button.rec-act--link {
  background: var(--gold-50);
  border: 1px solid var(--gold-300);
  color: var(--gold-700);
}

.rec-row__actions .el-button.rec-act--link:active {
  background: var(--gold-100);
  border-color: var(--gold-400);
}

/* 备注：墨色描边（次要动作） */
.rec-row__actions .el-button.rec-act--note {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-strong);
  color: var(--ink-700);
}

.rec-row__actions .el-button.rec-act--note:active {
  background: var(--ink-bg-wash);
  border-color: var(--gold-300);
  color: var(--gold-700);
}

/* 桌面端备注编辑（表格单元格内） */
.note-edit {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.note-edit__btns {
  display: flex;
  gap: 6px;
}

.note-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rec-row__admin {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.rec-row__linkline {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

/* 管理员行（勾选区存在）：职业/链接/备注行缩进约 2 字符宽，与 ID 对齐 */
.rec-row--admin .rec-row__meta,
.rec-row--admin .rec-row__linkline,
.rec-row--admin .rec-row__remark {
  padding-left: 28px;
}

.rec-row__url {
  flex: 1;
  min-width: 0;
  max-width: none;
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

</style>
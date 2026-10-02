/** 录屏列表数据与操作逻辑（自 RecordingTab.vue 拆出）。 */
import { computed, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  approveRecording,
  batchApprove,
  getRecordings,
  rejectRecording,
  submitRecording,
  submitRecordingNote,
} from '@/api/recording'
import type { Recording, RoundProgress } from '@/types/recording'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

/** 补全录屏链接协议（用户常只填域名/编号，缺协议浏览器无法直接打开）。 */
export function normalizeUrl(url: string): string {
  return /^https?:\/\//i.test(url) ? url : `https://${url}`
}

export function statusType(status: string) {
  return status === 'approved' ? 'success' : status === 'rejected' ? 'danger' : 'info'
}

export function statusLabel(status: string) {
  return status === 'approved' ? '已通过' : status === 'rejected' ? '已驳回' : '待审核'
}

export function useRecordingList(props: { scheduleId: number }) {
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

  // 筛选条件或页大小变化时回到第一页（避免停留在越界页码显示空白）
  watch([nameFilter, roundFilter, statusFilter, pageSize], () => {
    page.value = 1
  })

  /** 点击局数切换筛选（再次点击取消）。 */
  function toggleRound(round: number) {
    roundFilter.value = roundFilter.value === round ? null : round
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
    await ElMessageBox.confirm(`确定批量审核通过选中的 ${selectedIds.value.length} 条录屏吗？`, '提示', {
      type: 'warning',
    })
    const result = await batchApprove(props.scheduleId, selectedIds.value)
    ElMessage.success(result.message)
    load()
  }

  return {
    loading,
    showSkeleton,
    items,
    progress,
    selectedIds,
    statusFilter,
    nameFilter,
    roundFilter,
    editingId,
    editingUrl,
    editingNoteId,
    editingNote,
    filteredItems,
    pagedItems,
    page,
    pageSize,
    toggleRound,
    onCopyUrl,
    load,
    onSelectionChange,
    toggleSelect,
    startEdit,
    startNoteEdit,
    onSubmitNote,
    onSubmit,
    onApprove,
    onReject,
    onBatchApprove,
  }
}

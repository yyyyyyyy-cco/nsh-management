/** 常驻库成员列表数据与操作逻辑（自 MemberListView.vue 拆出）。 */
import { reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  batchDeleteMembers,
  deleteMember,
  exportMembers,
  exportMembersImage,
  listMembers,
  type MemberQuery,
  type MemberStats,
} from '@/api/members'
import type { MemberInfo } from '@/types/member'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import { useAuthStore } from '@/stores/auth'

export function useMemberList() {
  const loading = ref(false)
  const showSkeleton = useSkeletonLoading(loading)
  const items = ref<MemberInfo[]>([])
  const total = ref(0)
  const stats = ref<MemberStats>({ formal_count: 0, substitute_count: 0 })
  const selectedIds = ref<number[]>([])
  const shortageRefreshKey = ref(0) // 成员数据变更（添加/导入/删除）后递增，驱动缺少职业组件刷新
  const exporting = ref(false)

  /** 初始默认按 ID 正序（与后端白名单字段 name 对应）。 */
  const query = reactive<MemberQuery>({ page: 1, page_size: 20, sort_by: 'name', sort_order: 'asc' })

  async function load() {
    loading.value = true
    // 刷新后清空勾选：桌面表格随数据更新失去选中，移动端勾选同步清空保持一致
    selectedIds.value = []
    try {
      const page = await listMembers(query)
      items.value = page.items
      total.value = page.total
      stats.value = page.stats
    } finally {
      loading.value = false
      shortageRefreshKey.value += 1
    }
  }

  function handleSearch() {
    query.page = 1
    load()
  }

  /** 服务端排序变化：携带排序参数重新请求全量数据（无视分页）。 */
  function onSortChange({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) {
    if (order) {
      query.sort_by = prop
      query.sort_order = order === 'ascending' ? 'asc' : 'desc'
    } else {
      delete query.sort_by
      delete query.sort_order
    }
    query.page = 1
    load()
  }

  /** 一键导出：沿用当前筛选与排序（不含分页），浏览器直接下载 xlsx / png。 */
  async function onExport(format: 'xlsx' | 'png') {
    exporting.value = true
    // 请求前捕获帮会名，避免下载等待期间切换账号后误标来源。
    const guildName = (useAuthStore().user?.guild_name || '未命名帮会')
      .replace(/[<>:"/\\|?*\u0000-\u001f]/g, '_')
    try {
      const params = {
        keyword: query.keyword,
        profession: query.profession,
        status: query.status,
        sort_by: query.sort_by,
        sort_order: query.sort_order,
      }
      const blob = format === 'xlsx' ? await exportMembers(params) : await exportMembersImage(params)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      const tag = new Date().toISOString().slice(0, 10).replace(/-/g, '')
      link.href = url
      link.download = `常驻库_${guildName}_${tag}.${format}`
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      ElMessage.error('导出失败，请稍后重试')
    } finally {
      exporting.value = false
    }
  }

  function onSelectionChange(rows: MemberInfo[]) {
    selectedIds.value = rows.map((row) => row.id)
  }

  /** 移动端行内勾选：与桌面表格共用 selectedIds，支撑批量删除。 */
  function toggleSelect(id: number) {
    const idx = selectedIds.value.indexOf(id)
    if (idx >= 0) selectedIds.value.splice(idx, 1)
    else selectedIds.value.push(id)
  }

  async function onDelete(row: MemberInfo) {
    await ElMessageBox.confirm(`确定删除成员「${row.name}」吗？`, '提示', { type: 'warning' })
    await deleteMember(row.id)
    ElMessage.success('删除成功')
    load()
  }

  async function onBatchDelete() {
    await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 名成员吗？`, '提示', { type: 'warning' })
    const result = await batchDeleteMembers(selectedIds.value)
    ElMessage.success(result.message)
    load()
  }

  return {
    loading,
    showSkeleton,
    items,
    total,
    stats,
    selectedIds,
    shortageRefreshKey,
    exporting,
    query,
    load,
    handleSearch,
    onSortChange,
    onExport,
    onSelectionChange,
    toggleSelect,
    onDelete,
    onBatchDelete,
  }
}

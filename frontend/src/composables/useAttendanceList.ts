/** 出勤表数据与操作逻辑（自 AttendanceTab.vue 拆出）。 */
import { computed, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  batchStatus,
  deleteRecord,
  getAttendance,
  importFormal,
  updateProfession,
  updateRemark,
  updateStatus,
} from '@/api/attendance'
import { getProfessionConfigs } from '@/api/config'
import { getLineup, getLineupCandidates } from '@/api/lineups'
import type { ProfessionConfig } from '@/types/config'
import type { AttendanceRecord, AttendanceStats } from '@/types/attendance'
import type { ScheduleInfo } from '@/types/schedule'
import { PROF_ORDER } from '@/composables/lineupBoard'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

export function useAttendanceList(props: { scheduleId: number; schedule: ScheduleInfo }) {
  const loading = ref(false)
  const showSkeleton = useSkeletonLoading(loading)
  const items = ref<AttendanceRecord[]>([])
  const stats = ref<AttendanceStats>({ total: 0, normal_count: 0, leave_count: 0, gap: 60 })
  const selectedIds = ref<number[]>([])
  const keyword = ref('')
  const professionFilter = ref('')
  const typeFilter = ref('')
  const statusFilter = ref('')
  const customConfig = ref<Record<string, number> | null>(null) // 单场职业配置覆盖，null 沿用系统配置
  const profCfgVisible = ref(false)
  const professionConfigs = ref<ProfessionConfig[]>([])
  const removeVisible = ref(false)
  const removableItems = ref<AttendanceRecord[]>([])
  const removeSelected = ref<string[]>([])

  /** 按 ID / 职业 / 类型 / 状态客户端过滤 */
  const filteredItems = computed(() => {
    const kw = keyword.value.toLowerCase()
    return items.value.filter((r) => {
      if (professionFilter.value && r.profession !== professionFilter.value) return false
      if (statusFilter.value && r.status !== statusFilter.value) return false
      if (typeFilter.value) {
        const type = r.is_filler ? 'filler' : r.member_status === 'substitute' ? 'substitute' : 'formal'
        if (type !== typeFilter.value) return false
      }
      return !kw || r.member_name.toLowerCase().includes(kw)
    })
  })

  /** 切换出勤职业（主/副）。 */
  async function onProfessionChange(row: AttendanceRecord, profession: string) {
    if (profession === row.profession) return
    const updated = await updateProfession(props.scheduleId, row.id, profession)
    row.profession = updated.profession
    ElMessage.success(`已将「${row.member_name}」的职业设为 ${updated.profession}`)
  }

  /** 编辑出勤备注（管理员）：弹窗输入，留空清除；备注会带入排表候选池展示。 */
  async function onEditRemark(row: AttendanceRecord) {
    try {
      const { value } = await ElMessageBox.prompt('备注会带入排表候选池展示（可留空清除）', '编辑备注', {
        inputValue: row.remark || '',
        inputPlaceholder: '输入备注内容',
        inputValidator: (v: string) => (v || '').length <= 255 || '备注不超过 255 字',
      })
      const updated = await updateRemark(props.scheduleId, row.id, value.trim())
      row.remark = updated.remark
      ElMessage.success('备注已保存')
    } catch {
      /* 取消编辑或请求失败（错误提示由 http 拦截器统一处理） */
    }
  }

  /** 当前生效目标人数：单场覆盖优先，否则用系统配置。 */
  const effectiveTargets = computed<Record<string, number>>(() => {
    if (customConfig.value) return customConfig.value
    const map: Record<string, number> = {}
    for (const c of professionConfigs.value) map[c.profession] = c.target_count || 0
    return map
  })

  /** 是否存在目标人数大于 0 的职业（决定是否展示缺口 chips）。 */
  const hasGapTarget = computed(() => professionGap.value.some((g) => g.target > 0))

  /** 各职业缺口：目标人数 - 当前正常出勤人数（请假视为缺口）。 */
  const professionGap = computed(() => {
    const current: Record<string, number> = {}
    for (const r of items.value) {
      if (r.status === 'normal') current[r.profession] = (current[r.profession] || 0) + 1
    }
    return PROF_ORDER.map((p) => {
      const target = effectiveTargets.value[p] || 0
      return { profession: p, target, current: current[p] || 0, gap: target - (current[p] || 0) }
    })
  })

  /** 单场职业配置保存/恢复后更新本地覆盖值，立即重算缺口。 */
  function onProfessionConfigSaved(configs: Record<string, number> | null) {
    customConfig.value = configs
    profCfgVisible.value = false
  }

  async function load() {
    loading.value = true
    // 刷新后清空勾选：桌面表格随数据更新失去选中，移动端勾选同步清空保持一致
    selectedIds.value = []
    try {
      // 赛程详情由父级传入（避免与父级重复请求 getSchedule）
      const [data, configs] = await Promise.all([
        getAttendance(props.scheduleId),
        getProfessionConfigs(),
      ])
      items.value = data.items
      stats.value = data.stats
      professionConfigs.value = configs
      customConfig.value = props.schedule.profession_config ?? null
    } finally {
      loading.value = false
    }
  }

  function onSelectionChange(rows: AttendanceRecord[]) {
    selectedIds.value = rows.map((row) => row.id)
  }

  /** 移动端行内勾选：与桌面表格共用 selectedIds，支撑批量请假/正常。 */
  function toggleSelect(id: number) {
    const idx = selectedIds.value.indexOf(id)
    if (idx >= 0) selectedIds.value.splice(idx, 1)
    else selectedIds.value.push(id)
  }

  async function onImportFormal() {
    const result = await importFormal(props.scheduleId)
    ElMessage.success(result.message)
    load()
  }

  async function onToggle(row: AttendanceRecord, value: boolean) {
    const status = value ? 'normal' : 'leave'
    await updateStatus(props.scheduleId, row.id, status)
    ElMessage.success(status === 'normal' ? '已设为正常' : '已请假')
    load()
  }

  async function onBatch(status: 'normal' | 'leave') {
    await ElMessageBox.confirm(
      `确定将选中的 ${selectedIds.value.length} 名成员设为「${status === 'normal' ? '正常' : '请假'}」吗？`,
      '提示',
      { type: 'warning' },
    )
    const result = await batchStatus(props.scheduleId, selectedIds.value, status)
    ElMessage.success(result.message)
    load()
  }

  async function onDelete(row: AttendanceRecord) {
    await ElMessageBox.confirm(`确定移除「${row.member_name}」的出勤记录吗？`, '提示', { type: 'warning' })
    await deleteRecord(props.scheduleId, row.id)
    ElMessage.success('移除成功')
    load()
  }

  /** 一键移除：候选池中未被排入排表的已出勤（正常）成员，弹窗勾选后移出出勤表。 */
  async function onOpenRemove() {
    const [candidates, lineup] = await Promise.all([
      getLineupCandidates(props.scheduleId),
      getLineup(props.scheduleId),
    ])
    // 已排入排表的成员集合（正式按 member_id，补人按 member_name）
    const placed = new Set<string>()
    for (const team of lineup.data) {
      for (const slot of team.slots) {
        if (slot.member_id != null) placed.add(`id:${slot.member_id}`)
        if (slot.member_name) placed.add(`name:${slot.member_name}`)
      }
    }
    const unplacedNames = new Set(
      candidates
        .filter((c) => !placed.has(`id:${c.member_id}`) && !placed.has(`name:${c.member_name}`))
        .map((c) => c.member_name),
    )
    removableItems.value = items.value.filter(
      (r) => r.status === 'normal' && unplacedNames.has(r.member_name),
    )
    if (!removableItems.value.length) {
      ElMessage.info('没有可移除的人员：未排入排表的已出勤成员为空')
      return
    }
    removeSelected.value = removableItems.value.map((r) => r.member_name)
    removeVisible.value = true
  }

  async function onConfirmRemove() {
    const targets = removableItems.value.filter((r) => removeSelected.value.includes(r.member_name))
    for (const t of targets) {
      await deleteRecord(props.scheduleId, t.id)
    }
    ElMessage.success(`已移除 ${targets.length} 名成员`)
    removeVisible.value = false
    load()
  }

  return {
    loading,
    showSkeleton,
    items,
    stats,
    selectedIds,
    keyword,
    professionFilter,
    typeFilter,
    statusFilter,
    customConfig,
    profCfgVisible,
    professionConfigs,
    removeVisible,
    removableItems,
    removeSelected,
    filteredItems,
    effectiveTargets,
    hasGapTarget,
    professionGap,
    load,
    onSelectionChange,
    toggleSelect,
    onProfessionChange,
    onEditRemark,
    onProfessionConfigSaved,
    onImportFormal,
    onToggle,
    onBatch,
    onDelete,
    onOpenRemove,
    onConfirmRemove,
  }
}

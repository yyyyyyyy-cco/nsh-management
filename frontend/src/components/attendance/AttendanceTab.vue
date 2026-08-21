<template>
  <div class="attendance-tab">
    <div class="stats-bar">
      <div class="stat">
        <span class="label">总人数</span>
        <span class="value num">{{ stats.total }}</span>
      </div>
      <div class="stat-sep" />
      <div class="stat">
        <span class="label">正常</span>
        <span class="value normal num">{{ stats.normal_count }}</span>
      </div>
      <div class="stat-sep" />
      <div class="stat">
        <span class="label">请假</span>
        <span class="value leave num">{{ stats.leave_count }}</span>
      </div>
      <div class="stat-sep" />
      <div class="stat">
        <span class="label">缺口（60 人上限）</span>
        <span class="value num" :class="{ warn: stats.gap > 0 }">{{ stats.gap }}</span>
      </div>
    </div>

    <!-- 职业缺口分析（配置目标 vs 当前出勤） -->
    <div v-if="professionGap.some((g) => g.target > 0)" class="gap-bar">
      <span class="gap-bar__label">职业缺口</span>
      <span
        v-for="g in professionGap"
        :key="g.profession"
        class="gap-chip"
        :class="{ need: g.gap > 0, full: g.gap <= 0 }"
      >
        {{ g.profession }}
        <template v-if="g.gap > 0">缺{{ g.gap }}</template>
        <template v-else>已满</template>
      </span>
    </div>

    <div v-if="auth.isAdmin" class="toolbar">
      <el-button type="primary" :loading="loading" @click="onImportFormal">一键导入正式成员</el-button>
      <el-button @click="substituteVisible = true">导入替补</el-button>
      <el-button @click="memberImportVisible = true">导入成员</el-button>
      <el-button @click="fillerVisible = true">添加补人</el-button>
      <el-button type="warning" plain :disabled="selectedIds.length === 0" @click="onBatch('leave')">
        批量请假（{{ selectedIds.length }}）
      </el-button>
      <el-button type="success" plain :disabled="selectedIds.length === 0" @click="onBatch('normal')">
        批量正常
      </el-button>
      <el-button type="warning" plain @click="leaveImportVisible = true">导入请假</el-button>
      <el-button type="danger" plain @click="onOpenRemove">一键移除</el-button>
      <div class="spacer" />
    </div>

    <!-- ID 搜索 + 职业筛选 -->
    <div class="filter-row">
      <el-input
        v-model="keyword"
        placeholder="搜索 ID 过滤"
        clearable
        :prefix-icon="Search"
        class="keyword-input"
      />
      <el-select v-model="professionFilter" placeholder="职业筛选" clearable class="prof-filter">
        <el-option v-for="p in PROF_ORDER" :key="p" :label="p" :value="p" />
      </el-select>
      <el-select v-model="typeFilter" placeholder="类型筛选" clearable class="small-filter">
        <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
      </el-select>
      <el-select v-model="statusFilter" placeholder="状态筛选" clearable class="small-filter">
        <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
    </div>

    <el-table v-loading="loading" :data="filteredItems" @selection-change="onSelectionChange">
      <el-table-column v-if="auth.isAdmin" type="selection" width="44" />
      <el-table-column prop="member_name" label="ID" min-width="110" />
      <el-table-column prop="profession" label="职业" min-width="110">
        <template #default="{ row }">
          <el-select
            v-if="auth.isAdmin && (row.professions?.length || 0) > 1"
            :model-value="row.profession"
            style="width: 100px"
            @change="(value: string) => onProfessionChange(row, value)"
          >
            <el-option v-for="p in row.professions" :key="p" :label="p" :value="p" />
          </el-select>
          <span v-else class="prof-name" :style="{ color: profColor(row.profession) }">{{ row.profession }}</span>
        </template>
      </el-table-column>
      <el-table-column label="类型" min-width="70">
        <template #default="{ row }">
          <el-tag v-if="row.is_filler" type="warning" effect="light" size="small">补人</el-tag>
          <el-tag v-else-if="row.member_status === 'substitute'" type="info" effect="plain" size="small">替补</el-tag>
          <el-tag v-else type="primary" effect="plain" size="small">正式</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" min-width="110">
        <template #default="{ row }">
          <el-switch
            :model-value="row.status === 'normal'"
            inline-prompt
            active-text="正常"
            inactive-text="请假"
            @change="(value: boolean) => onToggle(row, value)"
          />
        </template>
      </el-table-column>
      <el-table-column v-if="auth.isAdmin" label="操作" min-width="80">
        <template #default="{ row }">
          <el-button link type="danger" @click="onDelete(row)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <FillerDialog v-model="fillerVisible" :schedule-id="scheduleId" @success="load" />
    <SubstituteImportDialog v-model="substituteVisible" :schedule-id="scheduleId" @success="load" />
    <LeaveImportDialog v-model="leaveImportVisible" :schedule-id="scheduleId" :records="items" @success="load" />
    <ImportMemberDialog v-model="memberImportVisible" :schedule-id="scheduleId" @success="load" />

    <!-- 一键移除：候选池中未被排入排表的已出勤（正常）成员 -->
    <el-dialog v-model="removeVisible" title="移除未排入排表的人员" width="min(420px, 92vw)" append-to-body>
      <div class="remove-hint">
        以下成员已出勤（正常），但在排表候选池中未被排入排表，确认后将移出出勤表：
      </div>
      <el-checkbox-group v-model="removeSelected" class="remove-list">
        <el-checkbox v-for="r in removableItems" :key="r.id" :value="r.member_name" class="remove-item">
          <span class="remove-item__name">{{ r.member_name }}</span>
          <span class="remove-item__prof" :style="{ color: profColor(r.profession) }">{{ r.profession }}</span>
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="removeVisible = false">取消</el-button>
        <el-button type="danger" :disabled="removeSelected.length === 0" @click="onConfirmRemove">
          移除（{{ removeSelected.length }}）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

import {
  batchStatus,
  deleteRecord,
  getAttendance,
  importFormal,
  updateProfession,
  updateStatus,
} from '@/api/attendance'
import { getProfessionConfigs } from '@/api/config'
import { getLineup, getLineupCandidates } from '@/api/lineups'
import type { ProfessionConfig } from '@/types/config'
import type { AttendanceRecord, AttendanceStats } from '@/types/attendance'
import { PROF_ORDER } from '@/composables/lineupBoard'
import { useAuthStore } from '@/stores/auth'
import FillerDialog from '@/components/attendance/FillerDialog.vue'
import SubstituteImportDialog from '@/components/attendance/SubstituteImportDialog.vue'
import LeaveImportDialog from '@/components/attendance/LeaveImportDialog.vue'
import ImportMemberDialog from '@/components/attendance/ImportMemberDialog.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const items = ref<AttendanceRecord[]>([])
const stats = ref<AttendanceStats>({ total: 0, normal_count: 0, leave_count: 0, gap: 60 })
const selectedIds = ref<number[]>([])
const fillerVisible = ref(false)
const substituteVisible = ref(false)
const leaveImportVisible = ref(false)
const memberImportVisible = ref(false)
const keyword = ref('')
const professionFilter = ref('')
const typeFilter = ref('')
const statusFilter = ref('')

/** 类型筛选选项：正式 / 替补 / 补人。 */
const TYPE_OPTIONS = [
  { value: 'formal', label: '正式' },
  { value: 'substitute', label: '替补' },
  { value: 'filler', label: '补人' },
]

/** 状态筛选选项：正常 / 请假。 */
const STATUS_OPTIONS = [
  { value: 'normal', label: '正常' },
  { value: 'leave', label: '请假' },
]
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

/** 职业色映射（依据 ui-style-guide）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profColor(prof: string) {
  return PROF_COLORS[prof] || '#c9a13b'
}

/** 切换出勤职业（主/副）。 */
async function onProfessionChange(row: AttendanceRecord, profession: string) {
  if (profession === row.profession) return
  const updated = await updateProfession(props.scheduleId, row.id, profession)
  row.profession = updated.profession
  ElMessage.success(`已将「${row.member_name}」的职业设为 ${updated.profession}`)
}

/** 各职业缺口：目标人数 - 当前正常出勤人数（请假视为缺口）。 */
const professionGap = computed(() => {
  const current: Record<string, number> = {}
  for (const r of items.value) {
    if (r.status === 'normal') current[r.profession] = (current[r.profession] || 0) + 1
  }
  return PROF_ORDER.map((p) => {
    const cfg = professionConfigs.value.find((c) => c.profession === p)
    const target = cfg?.target_count || 0
    return { profession: p, target, current: current[p] || 0, gap: target - (current[p] || 0) }
  })
})

onMounted(load)

async function load() {
  loading.value = true
  try {
    const [data, configs] = await Promise.all([getAttendance(props.scheduleId), getProfessionConfigs()])
    items.value = data.items
    stats.value = data.stats
    professionConfigs.value = configs
  } finally {
    loading.value = false
  }
}

function onSelectionChange(rows: AttendanceRecord[]) {
  selectedIds.value = rows.map((row) => row.id)
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
</script>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 20px;
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 60%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-sep {
  width: 1px;
  height: 30px;
  background: linear-gradient(180deg, transparent, var(--gold-300), transparent);
}

.label {
  font-size: 12px;
  color: var(--ink-500);
}

.value {
  font-size: 22px;
  font-weight: 800;
  color: var(--gold-700);
}

.value.normal {
  color: var(--jade);
}

.value.leave {
  color: var(--ochre);
}

.value.warn {
  color: var(--cinnabar);
}

/* ===== 职业缺口条 ===== */
.gap-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  background: var(--ink-bg-wash);
}

.gap-bar__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
  margin-right: 4px;
}

/* ===== 职业缺口条 ===== */
.gap-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  background: var(--ink-bg-wash);
}

.gap-bar__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
  margin-right: 4px;
}

.gap-chip {
  font-size: 12px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-xl);
  padding: 1px 9px;
  color: var(--ink-400);
}

.gap-chip.need {
  font-weight: 700;
  color: var(--gold-700);
  border-color: var(--gold-300);
  background: var(--gold-50);
}

.gap-chip.full {
  color: var(--ink-300);
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.spacer {
  flex: 1;
}

/* ===== ID 搜索框 ===== */
.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.filter-row .keyword-input {
  flex: 1;
  max-width: 280px;
  margin-bottom: 0;
}

.filter-row .prof-filter {
  width: 140px;
}

.filter-row .small-filter {
  width: 110px;
}

/* ===== 一键移除弹窗 ===== */
.remove-hint {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 12px;
  line-height: 1.6;
}

.remove-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px 2px;
}

.remove-item {
  display: flex;
  align-items: center;
  width: 100%;
  margin-right: 0;
  padding: 4px 8px;
  border-radius: var(--radius-md);
}

.remove-item:hover {
  background: var(--gold-50);
}

.remove-item__name {
  font-weight: 600;
  color: var(--ink-800);
  margin-right: 8px;
}

.remove-item__prof {
  font-size: 12px;
}

/* ===== 出勤状态开关（浅金风，颜色更浅更柔和） ===== */
.attendance-tab :deep(.el-switch.is-checked .el-switch__core) {
  background: linear-gradient(135deg, #f0e0a8 0%, #e8cd72 100%);
  border-color: transparent;
}

.attendance-tab :deep(.el-switch .el-switch__core) {
  border-radius: 999px;
}

.attendance-tab :deep(.el-switch__inner) {
  font-size: 12px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .stats-bar {
    flex-wrap: wrap;
    gap: 10px 16px;
    padding: 12px 14px;
  }

  .stat {
    flex: 1 1 calc(50% - 16px);
    min-width: 0;
  }

  .stat-sep {
    display: none;
  }

  .toolbar .el-button {
    flex: 1 1 calc(50% - 6px);
    margin-left: 0 !important;
    margin-right: 0;
  }

  .filter-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .filter-row .keyword-input {
    flex: 1 1 100%;
    max-width: none;
  }

  .filter-row .prof-filter {
    flex: 1 1 100%;
    width: 100%;
  }

  .filter-row .small-filter {
    flex: 1 1 calc(50% - 4px);
    width: 100%;
  }

  .toolbar {
    gap: 6px;
  }

  .spacer {
    display: none;
  }
}

@media (max-width: 480px) {
  .value {
    font-size: 19px;
  }

  .toolbar .el-button {
    font-size: 12px;
    padding-left: 8px;
    padding-right: 8px;
  }

  .gap-bar__label {
    flex-basis: 100%;
  }

  .stats-bar .label {
    font-size: 11px;
  }
}
</style>

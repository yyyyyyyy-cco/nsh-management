<template>
  <div class="attendance-tab">
    <div class="stats-bar">
      <div class="stat">
        <span class="label">总人数</span>
        <span class="value">{{ stats.total }}</span>
      </div>
      <div class="stat">
        <span class="label">正常</span>
        <span class="value normal">{{ stats.normal_count }}</span>
      </div>
      <div class="stat">
        <span class="label">请假</span>
        <span class="value leave">{{ stats.leave_count }}</span>
      </div>
      <div class="stat">
        <span class="label">缺口（60 人上限）</span>
        <span class="value" :class="{ warn: stats.gap > 0 }">{{ stats.gap }}</span>
      </div>
    </div>

    <div v-if="auth.isAdmin" class="toolbar">
      <el-button type="primary" :loading="loading" @click="onImportFormal">一键导入正式成员</el-button>
      <el-button @click="substituteVisible = true">导入替补</el-button>
      <el-button @click="fillerVisible = true">添加补人</el-button>
      <el-button type="warning" plain :disabled="selectedIds.length === 0" @click="onBatch('leave')">
        批量请假（{{ selectedIds.length }}）
      </el-button>
      <el-button type="success" plain :disabled="selectedIds.length === 0" @click="onBatch('normal')">
        批量正常
      </el-button>
      <div class="spacer" />
      <el-button type="primary" plain @click="onSave">保存考勤</el-button>
    </div>

    <el-table v-loading="loading" :data="items" @selection-change="onSelectionChange">
      <el-table-column v-if="auth.isAdmin" type="selection" width="44" />
      <el-table-column prop="member_name" label="姓名" min-width="110" />
      <el-table-column prop="profession" label="职业" width="90" />
      <el-table-column label="类型" width="80">
        <template #default="{ row }">
          <el-tag v-if="row.is_filler" type="warning" effect="light" size="small">补人</el-tag>
          <el-tag v-else-if="row.member_status === 'substitute'" type="info" effect="plain" size="small">替补</el-tag>
          <el-tag v-else type="primary" effect="plain" size="small">正式</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="120">
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
      <el-table-column v-if="auth.isAdmin" label="操作" width="90" fixed="right">
        <template #default="{ row }">
          <el-button link type="danger" @click="onDelete(row)">移除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <FillerDialog v-model="fillerVisible" :schedule-id="scheduleId" @success="load" />
    <SubstituteImportDialog v-model="substituteVisible" :schedule-id="scheduleId" @success="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  batchStatus,
  deleteRecord,
  getAttendance,
  importFormal,
  saveAttendance,
  updateStatus,
} from '@/api/attendance'
import type { AttendanceRecord, AttendanceStats } from '@/types/attendance'
import { useAuthStore } from '@/stores/auth'
import FillerDialog from '@/components/attendance/FillerDialog.vue'
import SubstituteImportDialog from '@/components/attendance/SubstituteImportDialog.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const items = ref<AttendanceRecord[]>([])
const stats = ref<AttendanceStats>({ total: 0, normal_count: 0, leave_count: 0, gap: 60 })
const selectedIds = ref<number[]>([])
const fillerVisible = ref(false)
const substituteVisible = ref(false)

onMounted(load)

async function load() {
  loading.value = true
  try {
    const data = await getAttendance(props.scheduleId)
    items.value = data.items
    stats.value = data.stats
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

async function onSave() {
  const result = await saveAttendance(props.scheduleId)
  ElMessage.success(result.message)
  stats.value = result.stats
}
</script>

<style scoped>
.stats-bar {
  display: flex;
  gap: 24px;
  padding: 12px 16px;
  background: #fff8e7;
  border-radius: 8px;
  margin-bottom: 12px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.label {
  font-size: 12px;
  color: #6b7280;
}

.value {
  font-size: 20px;
  font-weight: 700;
  color: #b8960e;
}

.value.normal {
  color: #22c55e;
}

.value.leave {
  color: #f59e0b;
}

.value.warn {
  color: #ef4444;
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
</style>

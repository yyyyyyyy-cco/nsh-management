<template>
  <div class="schedule-list page-enter">
    <div class="toolbar">
      <div class="toolbar-info">
        <el-icon class="info-icon"><Calendar /></el-icon>
        <span>联赛日程</span>
      </div>
      <el-button v-if="auth.isAdmin" type="primary" :icon="Plus" @click="openCreate()">创建赛程</el-button>
    </div>

    <ScheduleCalendar :schedules="schedules" @select-schedule="goDetail" @select-date="openCreate" @month-change="load" />

    <el-card v-if="auth.isAdmin" shadow="never" class="table-card">
      <template #header>
        <div class="table-header">
          <span>{{ viewMode === 'month' ? '本月赛程' : '全部赛程' }}</span>
          <el-radio-group v-model="viewMode" size="small" @change="onModeChange">
            <el-radio-button value="month">本月</el-radio-button>
            <el-radio-button value="all">全部</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-table v-loading="loading" :data="schedules" size="small">
        <el-table-column label="时间" min-width="150">
          <template #default="{ row }">
            <span class="time-cell">
              <span class="time-date num">{{ formatDate(row.match_time) }}</span>
              <span class="time-clock num">{{ formatClock(row.match_time) }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="opponent" label="对手" min-width="140">
          <template #default="{ row }">
            <span class="opponent">vs {{ row.opponent }}</span>
          </template>
        </el-table-column>
        <el-table-column label="局数" min-width="70">
          <template #default="{ row }">
            <span class="rounds">{{ row.rounds }}局</span>
          </template>
        </el-table-column>
        <el-table-column label="结果" min-width="80">
          <template #default="{ row }">
            <el-tag :type="resultType(row.result)" effect="light">{{ resultLabel(row.result) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="130">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">详情</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <ScheduleFormDialog v-model="formVisible" :schedule="editingSchedule" :default-date="defaultDate" @success="onSaved" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

import { deleteSchedule, listSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { SCHEDULE_RESULTS } from '@/utils/constants'
import { sortSchedulesByProximity } from '@/utils/scheduleSort'
import ScheduleCalendar from '@/components/schedules/ScheduleCalendar.vue'
import ScheduleFormDialog from '@/components/schedules/ScheduleFormDialog.vue'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const schedules = ref<ScheduleInfo[]>([])
const viewMode = ref<'month' | 'all'>('month')
const formVisible = ref(false)
const editingSchedule = ref<ScheduleInfo | null>(null)
const defaultDate = ref('')

const resultLabel = (value: string) => SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
const resultType = (value: string) =>
  value === 'win' ? 'success' : value === 'lose' ? 'danger' : value === 'draw' ? 'primary' : 'info'
const formatDate = (value: string) => dayjs(value).format('MM-DD')
const formatClock = (value: string) => dayjs(value).format('HH:mm')

onMounted(() => load(dayjs().format('YYYY-MM')))

async function load(month: string) {
  loading.value = true
  try {
    if (viewMode.value === 'month') {
      const start = `${month}-01`
      const end = dayjs(`${month}-01`).add(1, 'month').format('YYYY-MM-DD')
      schedules.value = sortSchedulesByProximity(await listSchedules({ start, end }))
    } else {
      schedules.value = sortSchedulesByProximity(await listSchedules())
    }
  } finally {
    loading.value = false
  }
}

function onModeChange() {
  load(dayjs().format('YYYY-MM'))
}

function openCreate(date?: string) {
  if (!auth.isAdmin) return
  editingSchedule.value = null
  defaultDate.value = date || ''
  formVisible.value = true
}

function goDetail(schedule: ScheduleInfo) {
  router.push({ name: 'schedule-detail', params: { id: schedule.id } })
}

function onSaved() {
  load(dayjs().format('YYYY-MM'))
}

async function onDelete(row: ScheduleInfo) {
  await ElMessageBox.confirm(
    `确定删除赛程「${row.opponent}」吗？将同时删除关联的出勤、排表、录屏和分析数据。`,
    '提示',
    { type: 'warning' },
  )
  await deleteSchedule(row.id)
  ElMessage.success('删除成功')
  load(dayjs().format('YYYY-MM'))
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 1px;
}

.info-icon {
  font-size: 18px;
}

.table-card {
  margin-top: 16px;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.table-header :deep(.el-radio-button__inner) {
  border-color: var(--gold-200);
  color: var(--gold-700);
  background: var(--ink-bg-paper);
}

.table-header :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gold-gradient);
  border-color: transparent;
  color: #fff;
  box-shadow: -1px 0 0 0 var(--gold-400);
}

.time-cell {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.time-date {
  font-weight: 700;
  color: var(--gold-700);
}

.time-clock {
  font-size: 12px;
  color: var(--ink-400);
}

.opponent {
  font-weight: 600;
  color: var(--ink-900);
}

.rounds {
  color: var(--ink-500);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    gap: 10px;
  }

  .toolbar-info {
    font-size: 15px;
  }

  .table-header {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

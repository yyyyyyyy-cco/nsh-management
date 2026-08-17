<template>
  <div class="schedule-list">
    <div class="toolbar">
      <el-button v-if="auth.isAdmin" type="primary" @click="openCreate()">创建赛程</el-button>
    </div>

    <ScheduleCalendar :schedules="schedules" @select-schedule="goDetail" @select-date="openCreate" @month-change="load" />

    <el-card shadow="never" class="table-card">
      <template #header>本月赛程</template>
      <el-table v-loading="loading" :data="schedules" size="small">
        <el-table-column label="时间" width="180">
          <template #default="{ row }">{{ formatTime(row.match_time) }}</template>
        </el-table-column>
        <el-table-column prop="opponent" label="对手" min-width="120" />
        <el-table-column prop="location" label="地点" min-width="120">
          <template #default="{ row }">{{ row.location || '-' }}</template>
        </el-table-column>
        <el-table-column label="局数" width="80">
          <template #default="{ row }">{{ row.rounds }}局</template>
        </el-table-column>
        <el-table-column label="结果" width="90">
          <template #default="{ row }">
            <el-tag :type="resultType(row.result)" effect="light">{{ resultLabel(row.result) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default="{ row }">
            <el-button link type="primary" @click="goDetail(row)">详情</el-button>
            <el-button v-if="auth.isAdmin" link type="danger" @click="onDelete(row)">删除</el-button>
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
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

import { deleteSchedule, listSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { SCHEDULE_RESULTS } from '@/utils/constants'
import ScheduleCalendar from '@/components/schedules/ScheduleCalendar.vue'
import ScheduleFormDialog from '@/components/schedules/ScheduleFormDialog.vue'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const schedules = ref<ScheduleInfo[]>([])
const formVisible = ref(false)
const editingSchedule = ref<ScheduleInfo | null>(null)
const defaultDate = ref('')

const resultLabel = (value: string) => SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
const resultType = (value: string) =>
  value === 'win' ? 'success' : value === 'lose' ? 'danger' : value === 'draw' ? 'primary' : 'info'
const formatTime = (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm')

onMounted(() => load(dayjs().format('YYYY-MM')))

async function load(month: string) {
  loading.value = true
  try {
    const start = `${month}-01`
    const end = dayjs(`${month}-01`).add(1, 'month').format('YYYY-MM-DD')
    schedules.value = await listSchedules({ start, end })
  } finally {
    loading.value = false
  }
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
  margin-bottom: 16px;
}

.table-card {
  margin-top: 16px;
}
</style>

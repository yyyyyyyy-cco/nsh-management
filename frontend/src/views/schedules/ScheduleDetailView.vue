<template>
  <div v-loading="loading" class="schedule-detail">
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <span>赛程详情</span>
          <div>
            <el-button @click="router.back()">返回</el-button>
            <el-button v-if="auth.isAdmin" type="primary" @click="formVisible = true">编辑</el-button>
            <el-button v-if="auth.isAdmin" type="danger" plain @click="onDelete">删除赛程</el-button>
          </div>
        </div>
      </template>
      <el-descriptions v-if="schedule" :column="2" border>
        <el-descriptions-item label="对手">{{ schedule.opponent }}</el-descriptions-item>
        <el-descriptions-item label="比赛时间">{{ formatTime(schedule.match_time) }}</el-descriptions-item>
        <el-descriptions-item label="地点">{{ schedule.location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="局数">{{ schedule.rounds }}局</el-descriptions-item>
        <el-descriptions-item label="比赛结果">
          <el-tag :type="resultType(schedule.result)" effect="light">{{ resultLabel(schedule.result) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="每局结果">
          <template v-if="schedule.round_results?.length">
            <el-tag
              v-for="(r, index) in schedule.round_results"
              :key="index"
              :type="resultType(r)"
              effect="light"
              class="round-tag"
            >
              第{{ index + 1 }}局：{{ resultLabel(r) }}
            </el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="tabs-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="出勤库" name="attendance">
          <AttendanceTab v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
        <el-tab-pane label="排表" name="lineup">
          <LineupTab v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
        <el-tab-pane label="录屏审核" name="recording">
          <RecordingTab v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
        <el-tab-pane label="数据分析" name="analysis">
          <MatchDataTab v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <ScheduleFormDialog v-model="formVisible" :schedule="schedule" @success="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

import { deleteSchedule, getSchedule } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { SCHEDULE_RESULTS } from '@/utils/constants'
import AttendanceTab from '@/components/attendance/AttendanceTab.vue'
import LineupTab from '@/components/lineups/LineupTab.vue'
import RecordingTab from '@/components/recording/RecordingTab.vue'
import MatchDataTab from '@/components/match-data/MatchDataTab.vue'
import ScheduleFormDialog from '@/components/schedules/ScheduleFormDialog.vue'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const schedule = ref<ScheduleInfo | null>(null)
const formVisible = ref(false)
const activeTab = ref('attendance')

const resultLabel = (value: string) => SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
const resultType = (value: string) =>
  value === 'win' ? 'success' : value === 'lose' ? 'danger' : value === 'draw' ? 'primary' : 'info'
const formatTime = (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm')

onMounted(load)

async function load() {
  loading.value = true
  try {
    schedule.value = await getSchedule(Number(route.params.id))
  } finally {
    loading.value = false
  }
}

async function onDelete() {
  if (!schedule.value) return
  await ElMessageBox.confirm(
    `确定删除赛程「${schedule.value.opponent}」吗？将同时删除关联的出勤、排表、录屏和分析数据。`,
    '提示',
    { type: 'warning' },
  )
  await deleteSchedule(schedule.value.id)
  ElMessage.success('删除成功')
  router.push({ name: 'schedules' })
}
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.round-tag {
  margin-right: 8px;
}

.tabs-card {
  margin-top: 16px;
}
</style>

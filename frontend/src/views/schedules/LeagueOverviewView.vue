<template>
  <div class="league-overview page-enter">
    <div class="toolbar">
      <div class="toolbar-info">
        <el-icon class="info-icon"><VideoCamera /></el-icon>
        <span>联赛总览</span>
        <span class="info-sub">全部联赛场次（由新到旧），点击进入录屏上传</span>
      </div>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="sortedSchedules" size="small" @row-click="goRecording">
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
        <el-table-column label="结果" min-width="90">
          <template #default="{ row }">
            <el-tag :type="resultType(row.result)" effect="light">{{ resultLabel(row.result) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" min-width="110">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goRecording(row)">上传录屏</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { VideoCamera } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import { listSchedules } from '@/api/schedules'
import type { ScheduleInfo } from '@/types/schedule'
import { SCHEDULE_RESULTS } from '@/utils/constants'

const router = useRouter()
const loading = ref(false)
const schedules = ref<ScheduleInfo[]>([])

// 由新到旧排序
const sortedSchedules = computed(() =>
  [...schedules.value].sort((a, b) => dayjs(b.match_time).valueOf() - dayjs(a.match_time).valueOf()),
)

const resultLabel = (value: string) => SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
const resultType = (value: string) =>
  value === 'win' ? 'success' : value === 'lose' ? 'danger' : value === 'draw' ? 'primary' : 'info'
const formatDate = (value: string) => dayjs(value).format('YYYY-MM-DD')
const formatClock = (value: string) => dayjs(value).format('HH:mm')

onMounted(load)

async function load() {
  loading.value = true
  try {
    schedules.value = await listSchedules()
  } catch {
    // 错误提示已由 http 拦截器统一处理，此处仅保证 loading 关闭
  } finally {
    loading.value = false
  }
}

function goRecording(schedule: ScheduleInfo) {
  router.push({ name: 'schedule-detail', params: { id: schedule.id }, query: { tab: 'recording', from: 'overview' } })
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

.info-sub {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 400;
  color: var(--ink-400);
  letter-spacing: 0;
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
  .toolbar-info {
    font-size: 15px;
  }

  .info-sub {
    display: none; /* 窄屏隐藏长副标题，避免溢出 */
  }
}
</style>

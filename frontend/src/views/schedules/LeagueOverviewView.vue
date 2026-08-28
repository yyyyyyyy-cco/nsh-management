<template>
  <div class="league-overview page-enter">
    <div class="toolbar">
      <div class="toolbar-info">
        <el-icon class="info-icon"><VideoCamera /></el-icon>
        <span>录屏上传</span>
        <span class="info-sub">{{ filterSubText }}（按距今天由近到远），点击进入录屏上传</span>
      </div>
      <el-radio-group v-model="timeFilter" size="small" class="toolbar-filter">
        <el-radio-button value="month">本月</el-radio-button>
        <el-radio-button value="lastMonth">上个月</el-radio-button>
        <el-radio-button value="all">全部</el-radio-button>
      </el-radio-group>
    </div>

    <el-card shadow="never" class="table-card">
      <el-table v-loading="loading" :data="filteredSchedules" size="small" @row-click="goRecording">
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
import { resultLabel, resultType } from '@/utils/constants'
import { sortSchedulesByProximity } from '@/utils/scheduleSort'

const router = useRouter()
const loading = ref(false)
const schedules = ref<ScheduleInfo[]>([])

/** 时间筛选：本月 / 上个月 / 全部（默认本月）。 */
const timeFilter = ref<'month' | 'lastMonth' | 'all'>('month')

// 按离今天日期绝对值排序（与排表页、首页一致）
const sortedSchedules = computed(() => sortSchedulesByProximity(schedules.value))

/** 按时间窗过滤后的赛程（本月：当月 1 号起；上个月：上月 1 号起至当月 1 号前）。 */
const filteredSchedules = computed(() => {
  if (timeFilter.value === 'all') return sortedSchedules.value
  const thisMonthStart = dayjs().startOf('month')
  const start = timeFilter.value === 'month' ? thisMonthStart : thisMonthStart.subtract(1, 'month')
  const end = timeFilter.value === 'month' ? thisMonthStart.add(1, 'month') : thisMonthStart
  return sortedSchedules.value.filter((s) => {
    const t = dayjs(s.match_time).valueOf()
    return t >= start.valueOf() && t < end.valueOf()
  })
})

const filterSubText = computed(() => {
  if (timeFilter.value === 'month') return '本月场次'
  if (timeFilter.value === 'lastMonth') return '上个月场次'
  return '全部联赛场次'
})

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

.toolbar-filter {
  flex-shrink: 0;
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
  .toolbar {
    flex-wrap: wrap;
    gap: 10px;
  }

  .toolbar-info {
    font-size: 15px;
  }

  .info-sub {
    display: none; /* 窄屏隐藏长副标题，避免溢出 */
  }
}
</style>

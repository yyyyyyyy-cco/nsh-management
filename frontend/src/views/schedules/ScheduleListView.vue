<!-- 行数豁免（连续逻辑）：赛程列表页单职责（月/全部模式 + 新建编辑弹窗）｜登记见 .agent/rules/file-length-rule.md 豁免清单 -->
<template>
  <div class="schedule-list">
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

      <!-- 移动端（≤768px）：赛程行列表（参照联赛总览卡片的信息层级），详情/删除紧凑按钮 -->
      <div v-if="isMobile" class="match-list">
        <SkeletonTable v-if="showSkeleton && !schedules.length" variant="rows" :rows="5" />
        <el-empty v-else-if="!loading && !schedules.length" description="当前筛选下暂无赛程" :image-size="72" />
        <div v-for="row in schedules" :key="row.id" class="match-card">
          <div class="mc-top">
            <span class="time-date num">{{ formatDate(row.match_time) }}</span>
            <span class="time-clock num">{{ formatClock(row.match_time) }}</span>
            <span class="rounds">{{ row.rounds }}局</span>
            <el-tag class="mc-result" :type="resultType(row.result)" effect="light">{{ resultLabel(row.result) }}</el-tag>
          </div>
          <div class="opponent">vs {{ row.opponent }}</div>
          <div class="mc-actions">
            <el-button class="mc-act mc-act--detail" @click="goDetail(row)">详情</el-button>
            <el-button class="mc-act" type="danger" plain @click="onDelete(row)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 桌面端：表格形态保持不变 -->
      <SkeletonTable v-else-if="showSkeleton && !schedules.length" variant="table" :rows="5" />
      <el-table v-else :data="schedules" size="small">
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
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, Plus } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

import { deleteSchedule, listSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { resultLabel, resultType } from '@/utils/constants'
import { sortSchedulesByProximity } from '@/utils/scheduleSort'
import ScheduleCalendar from '@/components/schedules/ScheduleCalendar.vue'
import ScheduleFormDialog from '@/components/schedules/ScheduleFormDialog.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const schedules = ref<ScheduleInfo[]>([])
const viewMode = ref<'month' | 'all'>('month')
const formVisible = ref(false)
const editingSchedule = ref<ScheduleInfo | null>(null)
const defaultDate = ref('')

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

const formatDate = (value: string) => dayjs(value).format('MM-DD')
const formatClock = (value: string) => dayjs(value).format('HH:mm')

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load(dayjs().format('YYYY-MM'))
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))

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
/* finesse · register=product · shell=card-list(≤768px) + table(桌面) */
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

/* ===== 移动端行列表（isMobile 时渲染，替换表格） ===== */
.match-list {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态/加载遮罩的占位高度 */
  touch-action: manipulation;
}

.match-card {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.match-card:last-child {
  border-bottom: none;
}

.mc-top {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.mc-top .time-date {
  font-size: 15px;
}

.mc-top .time-clock,
.mc-top .rounds {
  font-size: 12.5px;
}

.mc-result {
  margin-left: auto;
  flex-shrink: 0;
}

.match-card .opponent {
  margin-top: 5px;
  font-size: 15px;
  overflow-wrap: anywhere;
}

.mc-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

/* 紧凑动作按钮：32px 高、内容宽度，右对齐（与常驻库行列表同款） */
.mc-actions .el-button.mc-act {
  height: 32px;
  margin-left: 0;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
}

/* 详情：鎏金描边 */
.mc-actions .el-button.mc-act--detail {
  background: var(--gold-50);
  border: 1px solid var(--gold-300);
  color: var(--gold-700);
}

.mc-actions .el-button.mc-act--detail:active {
  background: var(--gold-100);
  border-color: var(--gold-400);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 卡片内边距收紧（对齐常驻库/赛程详情），为行列表释放横向空间 */
  .table-card :deep(.el-card__body) {
    padding: 14px;
  }

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

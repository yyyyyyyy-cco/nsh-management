<template>
  <el-card shadow="never" class="rate-panel">
    <template #header>
      <div class="panel-header">
        <span>出勤率统计</span>
        <!-- 移动端：排序分段控件（桌面端用表格表头排序） -->
        <el-radio-group v-if="isMobile" v-model="sortOrder" class="rate-sort" size="small">
          <el-radio-button value="asc">升序</el-radio-button>
          <el-radio-button value="desc">降序</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <!-- 移动端（≤768px）：出勤率行列表（专属排版：ID+职业+出勤率 / 进度条+正常请假） -->
    <div v-if="isMobile" class="rate-rows">
      <EmptyState v-if="!rateItems.length" description="暂无出勤率数据" :image-size="72" />
      <div v-for="row in sortedItems" :key="row.name" class="rate-row">
        <div class="rr-main">
          <span class="rr-name">{{ row.name }}</span>
          <span class="prof-name" :style="{ color: profColor(row.main_profession) }">{{ row.main_profession }}</span>
          <span v-if="row.attendance_rate !== null" class="rr-rate num" :class="{ warn: isLowAttendance(row.attendance_rate) }">
            {{ formatRatePercent(row.attendance_rate) }}
          </span>
          <span v-else class="none rr-none">无记录</span>
        </div>
        <div class="rr-barline">
          <el-progress
            v-if="row.attendance_rate !== null"
            :percentage="row.attendance_rate * 100"
            :stroke-width="8"
            :show-text="false"
            :color="attendanceProgressColor(row.attendance_rate)"
            class="rate-bar"
          />
          <span class="counts">正常 <em class="num">{{ row.normal_count }}</em> · 请假 <em class="num">{{ row.leave_count }}</em></span>
        </div>
      </div>
    </div>

    <!-- 桌面端：表格形态保持不变 -->
    <el-table v-else :data="rateItems" size="small">
      <el-table-column prop="name" label="ID" min-width="110">
        <template #default="{ row }">
          <span class="member-name">{{ row.name }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="main_profession" label="职业" min-width="90">
        <template #default="{ row }">
          <span class="prof-name" :style="{ color: profColor(row.main_profession) }">{{ row.main_profession }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="attendance_rate" label="出勤率" min-width="180" sortable>
        <template #default="{ row }">
          <div v-if="row.attendance_rate !== null" class="rate-cell">
            <el-progress
              :percentage="row.attendance_rate * 100"
              :stroke-width="8"
              :show-text="false"
              :color="attendanceProgressColor(row.attendance_rate)"
              class="rate-bar"
            />
            <span class="rate-num num" :class="{ warn: isLowAttendance(row.attendance_rate) }">
              {{ formatRatePercent(row.attendance_rate) }}
            </span>
          </div>
          <span v-else class="none">无记录</span>
        </template>
      </el-table-column>
      <el-table-column label="正常/请假" min-width="100">
        <template #default="{ row }">
          <span class="counts"><em class="num">{{ row.normal_count }}</em> / <em class="num">{{ row.leave_count }}</em></span>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'

import { getAttendanceRate, type AttendanceRateItem } from '@/api/members'
import { profColor } from '@/utils/profession'
import { attendanceProgressColor, formatRatePercent, isLowAttendance } from '@/utils/attendance'
import EmptyState from '@/components/common/EmptyState.vue'

const rateItems = ref<AttendanceRateItem[]>([])

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

// 移动端排序：默认升序（与接口默认一致：出勤率升序、无记录排最后）；桌面端仍用表格表头排序
const sortOrder = ref<'asc' | 'desc'>('asc')
const sortedItems = computed(() => {
  const dir = sortOrder.value === 'asc' ? 1 : -1
  return [...rateItems.value].sort((a, b) => {
    if (a.attendance_rate === null && b.attendance_rate === null) return 0
    if (a.attendance_rate === null) return 1 // 无记录始终排最后
    if (b.attendance_rate === null) return -1
    return (a.attendance_rate - b.attendance_rate) * dir
  })
})

onMounted(async () => {
  mq.addEventListener('change', onMqChange)
  rateItems.value = await getAttendanceRate()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped>
.panel-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

/* 移动端排序分段控件（仅移动端渲染）：紧凑高度 32px，与全站移动端按钮标准一致 */
.rate-sort {
  margin-left: auto;
}

.rate-sort :deep(.el-radio-button__inner) {
  display: flex;
  align-items: center;
  height: 32px;
  padding: 0 12px;
  font-size: 12.5px;
}

.member-name {
  font-weight: 600;
  color: var(--ink-900);
}

.prof-name {
  font-weight: 600;
  font-size: 12.5px;
}

.rate-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rate-bar {
  flex: 1;
}

.rate-num {
  width: 52px;
  text-align: right;
  font-weight: 700;
  color: var(--gold-700);
}

.warn {
  color: var(--cinnabar);
}

.none {
  color: var(--ink-400);
}

.counts {
  color: var(--ink-500);
}

.counts em {
  font-style: normal;
  font-weight: 600;
  color: var(--ink-700);
}

/* ===== 移动端行列表（isMobile 时渲染，替换表格） ===== */
.rate-rows {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态占位高度 */
  touch-action: manipulation;
}

.rate-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.rate-row:last-child {
  border-bottom: none;
}

.rr-main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rr-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--ink-900);
}

.rr-main .prof-name {
  flex-shrink: 0;
}

.rr-rate {
  margin-left: auto;
  flex-shrink: 0;
  font-weight: 700;
  color: var(--gold-700);
}

.rr-rate.warn {
  color: var(--cinnabar);
}

.rr-none {
  margin-left: auto;
  flex-shrink: 0;
}

.rr-barline {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 8px;
}

.rr-barline .rate-bar {
  flex: 1;
  min-width: 0;
}

.rr-barline .counts {
  flex-shrink: 0;
  font-size: 12px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .panel-header {
    flex-wrap: wrap;
    gap: 4px 12px;
    align-items: center;
  }

  /* 卡片内边距收紧，为行列表释放横向空间 */
  .rate-panel :deep(.el-card__body) {
    padding: 14px;
  }
}
</style>

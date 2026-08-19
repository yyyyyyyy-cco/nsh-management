<template>
  <div class="calendar">
    <div class="calendar-header">
      <el-button-group>
        <el-button size="small" class="nav-btn" @click="changeMonth(-1)"><el-icon><ArrowLeft /></el-icon></el-button>
        <el-button size="small" class="today-btn" @click="goToday">今天</el-button>
        <el-button size="small" class="nav-btn" @click="changeMonth(1)"><el-icon><ArrowRight /></el-icon></el-button>
      </el-button-group>
      <span class="month-title">{{ viewMonth.format('YYYY年MM月') }}</span>
      <span class="header-hint">点击日期创建赛程 · 点击赛程查看详情</span>
    </div>
    <div class="weekdays">
      <span v-for="w in WEEKDAYS" :key="w" class="weekday" :class="{ 'weekday--weekend': w === '六' || w === '日' }">
        {{ w }}
      </span>
    </div>
    <div class="days">
      <div
        v-for="cell in cells"
        :key="cell.key"
        class="day"
        :class="{ muted: !cell.inMonth, today: cell.isToday, 'has-event': cell.schedules.length > 0 }"
        @click="emit('select-date', cell.date.format('YYYY-MM-DD'))"
      >
        <span class="day-num num">{{ cell.date.date() }}</span>
        <div class="events">
          <div
            v-for="s in cell.schedules"
            :key="s.id"
            class="event"
            :class="s.result"
            @click.stop="emit('select-schedule', s)"
          >
            {{ s.opponent }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import dayjs, { type Dayjs } from 'dayjs'

import type { ScheduleInfo } from '@/types/schedule'

const props = defineProps<{ schedules: ScheduleInfo[] }>()
const emit = defineEmits<{
  'select-schedule': [schedule: ScheduleInfo]
  'select-date': [date: string]
  'month-change': [month: string]
}>()

const WEEKDAYS = ['一', '二', '三', '四', '五', '六', '日']
const viewMonth = ref(dayjs().startOf('month'))

interface CalendarCell {
  key: string
  date: Dayjs
  inMonth: boolean
  isToday: boolean
  schedules: ScheduleInfo[]
}

const cells = computed<CalendarCell[]>(() => {
  const monthStart = viewMonth.value
  // dayjs 默认一周从周日开始，需显式换算为周一起始：day()=0(周日)~6(周六)，(day+6)%7 得到距本周一的天数
  const gridStart = monthStart.subtract((monthStart.day() + 6) % 7, 'day')
  const today = dayjs().format('YYYY-MM-DD')
  const list: CalendarCell[] = []
  for (let i = 0; i < 42; i++) {
    const date = gridStart.add(i, 'day')
    list.push({
      key: date.format('YYYY-MM-DD'),
      date,
      inMonth: date.month() === monthStart.month(),
      isToday: date.format('YYYY-MM-DD') === today,
      schedules: props.schedules.filter((s) => dayjs(s.match_time).format('YYYY-MM-DD') === date.format('YYYY-MM-DD')),
    })
  }
  return list
})

function changeMonth(delta: number) {
  viewMonth.value = viewMonth.value.add(delta, 'month')
  emit('month-change', viewMonth.value.format('YYYY-MM'))
}

function goToday() {
  viewMonth.value = dayjs().startOf('month')
  emit('month-change', viewMonth.value.format('YYYY-MM'))
}
</script>

<style scoped>
.calendar {
  background: var(--ink-bg-paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--edge-soft);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--edge-faint);
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 70%);
}

.month-title {
  font-family: var(--font-serif);
  font-size: 18px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 2px;
}

.header-hint {
  margin-left: auto;
  font-size: 11px;
  color: var(--ink-400);
  letter-spacing: 1px;
}

.calendar-header :deep(.el-button-group) {
  display: inline-flex;
}

.calendar-header :deep(.nav-btn) {
  border-radius: var(--radius-md) !important;
  border-color: var(--gold-200);
  color: var(--gold-700);
  background: var(--ink-bg-paper);
  transition: all var(--dur-fast);
}

.calendar-header :deep(.nav-btn:hover) {
  color: #fff;
  background: var(--gold-gradient);
  border-color: transparent;
}

.calendar-header :deep(.today-btn) {
  border-radius: var(--radius-md) !important;
  margin: 0 6px;
  background: transparent;
  border: 1px solid var(--gold-400);
  color: var(--gold-700);
  font-weight: 600;
  transition: all var(--dur-fast);
}

.calendar-header :deep(.today-btn:hover) {
  background: var(--gold-gradient);
  border-color: transparent;
  color: #fff;
  box-shadow: var(--shadow-gold);
  transform: translateY(-1px);
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid var(--edge-faint);
  background: var(--ink-bg-wash);
}

.weekday {
  text-align: center;
  padding: 8px 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-500);
}

.weekday--weekend {
  color: var(--gold-600);
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.day {
  min-height: 92px;
  padding: 6px;
  border-right: 1px solid var(--edge-faint);
  border-bottom: 1px solid var(--edge-faint);
  cursor: pointer;
  overflow: hidden;
  transition: background var(--dur-fast);
}

.day:hover {
  background: var(--gold-50);
}

.day:nth-child(7n) {
  border-right: none;
}

.day.muted {
  background: rgba(244, 238, 225, 0.45);
}

.day.muted .day-num {
  color: var(--ink-300);
}

.day.today {
  background: linear-gradient(180deg, rgba(212, 175, 55, 0.08), transparent 60%);
}

.day.today .day-num {
  background: linear-gradient(135deg, #f0e2b6 0%, #e2c979 100%);
  color: #8a6d1d;
  box-shadow: 0 1px 4px rgba(201, 161, 59, 0.35);
}

.day.has-event .day-num::after {
  content: '';
  display: block;
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--gold-500);
  margin: 1px auto 0;
}

.day-num {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 13px;
  color: var(--ink-600);
}

.events {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.event {
  font-size: 12px;
  padding: 2px 10px;
  border-radius: 999px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: var(--gold-100);
  color: var(--gold-700);
  transition: transform var(--dur-fast), box-shadow var(--dur-fast);
  cursor: pointer;
}

.event:hover {
  transform: translateX(2px);
  box-shadow: var(--shadow-sm);
}

.event.win {
  background: var(--el-color-success-light-9);
  color: var(--jade);
}

.event.lose {
  background: var(--el-color-danger-light-9);
  color: var(--cinnabar);
}

.event.draw {
  background: var(--el-color-info-light-9);
  color: var(--indigo);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .calendar-header {
    gap: 10px;
    padding: 10px 12px;
  }

  .header-hint {
    display: none; /* 窄屏隐藏操作提示，避免溢出 */
  }

  .month-title {
    font-size: 15px;
  }

  .day {
    min-height: 56px;
    padding: 3px;
  }

  .day-num {
    min-width: 20px;
    height: 20px;
    font-size: 12px;
  }

  .event {
    font-size: 10px;
    padding: 1px 6px;
  }

  .weekday {
    padding: 6px 0;
    font-size: 11px;
  }
}
</style>

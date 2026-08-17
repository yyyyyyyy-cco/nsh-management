<template>
  <div class="calendar">
    <div class="calendar-header">
      <el-button-group>
        <el-button size="small" @click="changeMonth(-1)"><el-icon><ArrowLeft /></el-icon></el-button>
        <el-button size="small" @click="goToday">今天</el-button>
        <el-button size="small" @click="changeMonth(1)"><el-icon><ArrowRight /></el-icon></el-button>
      </el-button-group>
      <span class="month-title">{{ viewMonth.format('YYYY年MM月') }}</span>
    </div>
    <div class="weekdays">
      <span v-for="w in WEEKDAYS" :key="w" class="weekday">{{ w }}</span>
    </div>
    <div class="days">
      <div
        v-for="cell in cells"
        :key="cell.key"
        class="day"
        :class="{ muted: !cell.inMonth, today: cell.isToday }"
        @click="emit('select-date', cell.date.format('YYYY-MM-DD'))"
      >
        <span class="day-num">{{ cell.date.date() }}</span>
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
  const gridStart = monthStart.startOf('week').subtract(1, 'day') // 周一起始
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
  background: #fff;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.month-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  border-bottom: 1px solid #f3f4f6;
}

.weekday {
  text-align: center;
  padding: 8px 0;
  font-size: 12px;
  color: #6b7280;
}

.days {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
}

.day {
  min-height: 92px;
  padding: 6px;
  border-right: 1px solid #f3f4f6;
  border-bottom: 1px solid #f3f4f6;
  cursor: pointer;
  overflow: hidden;
}

.day:nth-child(7n) {
  border-right: none;
}

.day.muted {
  background: #fafafa;
}

.day.muted .day-num {
  color: #c0c4cc;
}

.day.today .day-num {
  background: #d4af37;
  color: #fff;
}

.day-num {
  display: inline-block;
  min-width: 22px;
  text-align: center;
  border-radius: 50%;
  font-size: 13px;
  color: #374151;
}

.events {
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.event {
  font-size: 12px;
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  background: #f5f0e8;
  color: #6b5b45;
}

.event.win {
  background: #ecfdf5;
  color: #22c55e;
}

.event.lose {
  background: #fef2f2;
  color: #ef4444;
}

.event.draw {
  background: #eef2ff;
  color: #6366f1;
}
</style>

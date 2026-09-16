<template>
  <div class="today-banner" @click="goTodaySchedule">
    <div class="today-banner__badge">
      <el-icon><Bell /></el-icon>
    </div>
    <div class="today-banner__info">
      <span class="today-banner__title">今日比赛</span>
      <div class="today-banner__matches">
        <span v-for="s in schedules" :key="s.id" class="today-banner__match">
          vs {{ s.opponent }} · {{ formatTime(s.match_time) }}{{ s.rounds ? ` · ${s.rounds}局` : '' }}
        </span>
      </div>
    </div>
    <el-button link type="primary" class="today-banner__link">
      前往查看 <el-icon><ArrowRight /></el-icon>
    </el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight, Bell } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import type { ScheduleInfo } from '@/types/schedule'

const props = defineProps<{ schedules: ScheduleInfo[] }>()

const router = useRouter()

function formatTime(t: string) {
  return dayjs(t).format('HH:mm')
}

/** 跳转今日第一场比赛详情（多条时前往第一条）。 */
function goTodaySchedule() {
  if (props.schedules.length) {
    router.push(`/schedules/${props.schedules[0].id}`)
  }
}
</script>

<style scoped>
.today-banner {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
  padding: 12px 18px;
  background: linear-gradient(135deg, var(--gold-100) 0%, var(--gold-50) 100%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  cursor: pointer;
  transition: box-shadow var(--dur-fast), transform var(--dur-fast);
}

.today-banner:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-1px);
}

.today-banner__badge {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f2dfa0 0%, #d9b64a 60%, #c9a13b 100%);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  flex-shrink: 0;
  box-shadow: var(--shadow-gold);
}

.today-banner__info {
  flex: 1;
  min-width: 0;
}

.today-banner__title {
  font-family: var(--font-serif);
  font-size: 14px;
  font-weight: 700;
  color: var(--gold-700);
  letter-spacing: 1px;
}

.today-banner__matches {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 14px;
  margin-top: 2px;
}

.today-banner__match {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-700);
}

.today-banner__link {
  flex-shrink: 0;
}

@media (max-width: 480px) {
  .today-banner {
    flex-wrap: wrap;
    gap: 10px;
    padding: 12px;
  }

  .today-banner__link {
    margin-left: auto;
  }
}
</style>

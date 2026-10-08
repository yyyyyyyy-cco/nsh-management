<template>
  <div class="card">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><Calendar /></el-icon>
        <span class="card__title">最近比赛</span>
      </div>
      <el-button link type="primary" @click="router.push('/schedules')">
        查看全部 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
    <div class="card__body recent-body">
      <SkeletonTable v-if="showSkeleton && schedules.length === 0" variant="rows" :rows="3" />
      <template v-else-if="schedules.length === 0">
        <div class="empty-state">
          <div class="empty-state__icon">
            <el-icon :size="36"><Calendar /></el-icon>
          </div>
          <div class="empty-state__text">暂无比赛安排</div>
          <el-button type="primary" size="small" @click="router.push('/schedules')">创建比赛</el-button>
        </div>
      </template>
      <template v-else>
        <div v-for="s in schedules" :key="s.id" class="schedule-item" @click="router.push(`/schedules/${s.id}`)">
          <div class="schedule-item__date">
            <span class="schedule-item__day num">{{ formatDay(s.match_time) }}</span>
            <span class="schedule-item__month">{{ formatMonth(s.match_time) }}</span>
          </div>
          <div class="schedule-item__info">
            <div class="schedule-item__opponent">vs {{ s.opponent }}</div>
            <div class="schedule-item__meta">
              <span>{{ formatTime(s.match_time) }}</span>
              <el-tag v-if="s.result" :type="resultType(s.result)" size="small" effect="light">
                {{ resultLabel(s.result) }}
              </el-tag>
            </div>
          </div>
          <el-icon class="schedule-item__arrow"><ArrowRight /></el-icon>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight, Calendar } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import type { ScheduleInfo } from '@/types/schedule'
import { resultLabel, resultType } from '@/utils/constants'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

defineProps<{ showSkeleton: boolean; schedules: ScheduleInfo[] }>()

const router = useRouter()

function formatDay(t: string) {
  return dayjs(t).format('DD')
}

function formatMonth(t: string) {
  return dayjs(t).format('M月')
}

function formatTime(t: string) {
  return dayjs(t).format('HH:mm')
}
</script>

<style scoped src="./home-shared.css"></style>

<style scoped>
/* ===== 最近比赛：固定高度展示 3 场，超出滚动 ===== */
.recent-body {
  height: 208px; /* 3 场 × 64px/场 + 上下 padding 16px */
  overflow-y: auto;
}

.recent-body::-webkit-scrollbar {
  width: 6px;
}

.recent-body::-webkit-scrollbar-thumb {
  background: var(--gold-300);
  border-radius: 3px;
}

.recent-body::-webkit-scrollbar-track {
  background: transparent;
}

/* ===== 比赛列表项 ===== */
.schedule-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--dur-fast);
}

.schedule-item:hover {
  background: var(--gold-50);
}

.schedule-item__date {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: linear-gradient(135deg, #f6ecd0 0%, #eedda4 100%);
  border: 1px solid var(--gold-200);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.schedule-item__day {
  font-size: 16px;
  font-weight: 800;
  color: var(--gold-700);
  line-height: 1;
}

.schedule-item__month {
  font-size: 10px;
  color: var(--gold-600);
  line-height: 1.2;
}

.schedule-item__info {
  flex: 1;
  min-width: 0;
}

.schedule-item__opponent {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.schedule-item__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  font-size: 12px;
  color: var(--ink-400);
}

.schedule-item__arrow {
  color: var(--ink-300);
  font-size: 12px;
}
</style>

<!-- 帮众首页·最近比赛结果（含各局比分，点击进入赛程详情） -->
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
    <div class="card__body">
      <EmptyState v-if="!matches.length" variant="empty" description="暂无已结束的比赛" :image-size="72" />
      <template v-else>
        <div v-for="s in matches" :key="s.id" class="match-row" @click="goDetail(s.id)">
          <div class="match-row__date">
            <span class="match-row__day num">{{ formatDay(s.match_time) }}</span>
            <span class="match-row__month">{{ formatMonth(s.match_time) }}</span>
          </div>
          <div class="match-row__info">
            <div class="match-row__top">
              <span class="match-row__opponent">vs {{ s.opponent }}</span>
              <el-tag :type="resultType(s.result)" effect="light" size="small">{{ resultLabel(s.result) }}</el-tag>
            </div>
            <div class="match-row__rounds">{{ roundsText(s) }}</div>
          </div>
          <el-icon class="match-row__arrow"><ArrowRight /></el-icon>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { ArrowRight, Calendar } from '@element-plus/icons-vue'

import type { ScheduleInfo } from '@/types/schedule'
import { resultLabel, resultType } from '@/utils/constants'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{ matches: ScheduleInfo[] }>()

const router = useRouter()

const formatDay = (t: string) => dayjs(t).format('DD')
const formatMonth = (t: string) => dayjs(t).format('M月')

/** 各局结果（第1局 胜 · 第2局 负）；未记录时退回总局数。 */
function roundsText(s: ScheduleInfo): string {
  const results = (s.round_results ?? []).filter(Boolean)
  if (!results.length) return `${s.rounds} 局`
  return results.map((r, i) => `第${i + 1}局 ${resultLabel(r)}`).join(' · ')
}

function goDetail(id: number) {
  router.push({ name: 'schedule-detail', params: { id }, query: { from: 'home' } })
}
</script>

<style scoped src="./card-shared.css"></style>

<style scoped>
/* finesse · register=product · shell=member-home: 最近比赛列表（行点击进详情，≤768px 触控收敛） */
.match-row {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: background var(--dur-fast);
}

.match-row:hover {
  background: var(--gold-50);
}

.match-row:active {
  background: var(--gold-100);
}

.match-row__date {
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f6ecd0 0%, #eedda4 100%);
  border: 1px solid var(--gold-200);
}

.match-row__day {
  font-size: 16px;
  font-weight: 800;
  line-height: 1;
  color: var(--gold-700);
}

.match-row__month {
  font-size: 10px;
  line-height: 1.2;
  color: var(--gold-600);
}

.match-row__info {
  flex: 1;
  min-width: 0;
}

.match-row__top {
  display: flex;
  align-items: center;
  gap: 8px;
}

.match-row__opponent {
  min-width: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
  overflow-wrap: anywhere;
}

.match-row__rounds {
  margin-top: 2px;
  font-size: 12px;
  color: var(--ink-400);
  overflow-wrap: anywhere;
}

.match-row__arrow {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--ink-300);
}

@media (max-width: 768px) {
  .match-row {
    padding: 10px;
    gap: 10px;
  }
}
</style>

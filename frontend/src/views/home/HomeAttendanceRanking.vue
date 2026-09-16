<template>
  <div class="card">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><Medal /></el-icon>
        <span class="card__title">出勤排行</span>
      </div>
      <el-button link type="primary" @click="router.push({ path: '/members', query: { tab: 'rate' } })">
        查看全部 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>
    <div class="card__body rank-list">
      <SkeletonTable v-if="showSkeleton && topAttendance.length === 0" variant="rows" :rows="5" />
      <template v-else-if="topAttendance.length === 0">
        <div class="empty-state">
          <div class="empty-state__icon"><el-icon :size="36"><UserFilled /></el-icon></div>
          <div class="empty-state__text">暂无出勤数据</div>
        </div>
      </template>
      <template v-else>
        <div v-for="(m, i) in topAttendance" :key="m.member_id" class="rank-item">
          <span class="rank-item__number num" :class="`rank-item__number--${i + 1}`">
            {{ i + 1 }}
          </span>
          <span class="rank-item__dot" :style="{ background: profColor(m.main_profession) }" />
          <span class="rank-item__name">{{ m.name }}</span>
          <el-progress
            :percentage="(m.attendance_rate ?? 0) * 100"
            :stroke-width="6"
            :show-text="false"
            :color="profColor(m.main_profession)"
            style="flex: 1"
          />
          <span class="rank-item__rate num" :style="{ color: profColor(m.main_profession) }">
            {{ m.attendance_rate != null ? `${ratePercent(m.attendance_rate)}%` : '-' }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight, Medal, UserFilled } from '@element-plus/icons-vue'

import type { AttendanceRateItem } from '@/api/members'
import { profColor } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

defineProps<{ showSkeleton: boolean; topAttendance: AttendanceRateItem[] }>()

const router = useRouter()

/** 出勤率小数（0~1）转百分数整数。 */
function ratePercent(rate: number | null | undefined): number | string {
  return rate != null ? Math.round(rate * 100) : '-'
}
</script>

<style scoped src="./home-shared.css"></style>

<style scoped>
/* ===== 出勤排行 ===== */
.rank-list {
  padding: 12px 16px !important;
  height: 252px; /* 6 人 × 38px/人 + 上下 padding 24px */
  overflow-y: auto;
}

.rank-list::-webkit-scrollbar {
  width: 6px;
}

.rank-list::-webkit-scrollbar-thumb {
  background: var(--gold-300);
  border-radius: 3px;
}

.rank-list::-webkit-scrollbar-track {
  background: transparent;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
}

.rank-item:not(:last-child) {
  border-bottom: 1px solid var(--edge-faint);
}

.rank-item__number {
  width: 22px;
  height: 22px;
  text-align: center;
  line-height: 22px;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-300);
  background: var(--edge-faint);
}

.rank-item__number--1 {
  background: linear-gradient(135deg, #f6c94d, #d4a017);
  color: #fff;
  box-shadow: 0 2px 8px rgba(212, 160, 23, 0.5);
  position: relative;
  overflow: hidden;
}

.rank-item__number--1::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.45), transparent);
  animation: medal-shimmer 2.5s ease-in-out infinite;
}

.rank-item__number--2 {
  background: linear-gradient(135deg, #c9c9c9, #9a9a9a);
  color: #fff;
  box-shadow: 0 2px 6px rgba(154, 154, 154, 0.4);
  position: relative;
  overflow: hidden;
}

.rank-item__number--2::after {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 60%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.35), transparent);
  animation: medal-shimmer 3s ease-in-out infinite;
  animation-delay: 0.5s;
}

.rank-item__number--3 {
  background: linear-gradient(135deg, #e0a877, #b97f4b);
  color: #fff;
  box-shadow: 0 2px 6px rgba(185, 127, 75, 0.35);
}

@keyframes medal-shimmer {
  0% { left: -100%; }
  50% { left: 150%; }
  100% { left: 150%; }
}

.rank-item__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.rank-item__name {
  width: 60px;
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.rank-item__rate {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: 700;
}
</style>

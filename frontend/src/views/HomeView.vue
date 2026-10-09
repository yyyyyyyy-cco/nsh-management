<template>
  <div class="dashboard">
    <!-- 欢迎区 -->
    <HomeWelcome />

    <!-- 今日比赛提醒 -->
    <HomeTodayBanner v-if="todaySchedules.length" :schedules="todaySchedules" />

    <!-- 统计卡片 -->
    <HomeStatCards
      :loading="loading"
      :member-count="memberCount"
      :schedule-count="scheduleCount"
      :top-name="topAttendance[0]?.name || '-'"
      :top-rate="topAttendance[0]?.attendance_rate"
    />

    <!-- 主内容区：两栏布局 -->
    <div class="main-grid">
      <!-- 左栏 -->
      <div class="column">
        <HomeRecentSchedules :show-skeleton="showSkeleton" :schedules="recentSchedules" />

        <!-- 职业配置概览（辅助卡片层级） -->
        <HomeProfessionOverview
          v-if="!auth.isDeveloper"
          :show-skeleton="showSkeleton"
          :profession-stats="professionStats"
        />

        <!-- 历史总览 -->
        <div class="overview-bar">
          <div class="overview-item">
            <span v-if="showSkeleton" class="sk sk-line sk-kpi-sm" />
            <div v-else class="overview-item__value num">{{ memberCount }}</div>
            <div class="overview-item__label">帮众总数</div>
          </div>
          <div class="overview-item__sep" />
          <div class="overview-item">
            <span v-if="showSkeleton" class="sk sk-line sk-kpi-sm" />
            <div v-else class="overview-item__value num">{{ scheduleCount }}</div>
            <div class="overview-item__label">历史比赛</div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="column">
        <!-- 出勤率排行 -->
        <HomeAttendanceRanking v-if="!auth.isDeveloper" :show-skeleton="showSkeleton" :top-attendance="topAttendance" />

        <!-- 快捷操作（辅助卡片层级） -->
        <HomeQuickActions />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'

import { useAuthStore } from '@/stores/auth'
import { getProfessionStats, listMembers, getAttendanceRate, type AttendanceRateItem } from '@/api/members'
import { listSchedules } from '@/api/schedules'
import type { ScheduleInfo } from '@/types/schedule'
import { sortSchedulesByProximity, endedSchedules } from '@/utils/scheduleSort'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import { profColor } from '@/utils/profession'
import HomeAttendanceRanking from './home/HomeAttendanceRanking.vue'
import HomeProfessionOverview from './home/HomeProfessionOverview.vue'
import HomeQuickActions from './home/HomeQuickActions.vue'
import HomeRecentSchedules from './home/HomeRecentSchedules.vue'
import HomeStatCards from './home/HomeStatCards.vue'
import HomeTodayBanner from './home/HomeTodayBanner.vue'
import HomeWelcome from './home/HomeWelcome.vue'

const auth = useAuthStore()

const loading = ref(true)
const showSkeleton = useSkeletonLoading(loading)
const memberCount = ref(0)
const scheduleCount = ref(0)
const allSchedules = ref<ScheduleInfo[]>([])
const recentSchedules = ref<ScheduleInfo[]>([])
const topAttendance = ref<AttendanceRateItem[]>([])
const professionStats = ref<{ name: string; count: number; color: string }[]>([])

/** 今日比赛：从完整赛程中筛选（recentSchedules 仅保留 5 条，不能作为判断依据）。 */
const todaySchedules = computed(() => allSchedules.value.filter((s) => dayjs(s.match_time).isSame(dayjs(), 'day')))

onMounted(async () => {
  loading.value = true
  try {
    const tasks: Promise<void>[] = []

    // 获取成员数量
    tasks.push(
      listMembers({ page: 1, page_size: 1 }).then((r) => {
        memberCount.value = r.total
      }),
    )

    // 获取全部赛程（历史比赛统计 + 今日提醒 + 最近 5 场）
    tasks.push(
      listSchedules().then((r) => {
        allSchedules.value = r
        recentSchedules.value = sortSchedulesByProximity(r).slice(0, 5)
        // 「历史比赛」= 已结束（比赛时间已过）的场次，与帮众首页「已赛场次」同口径
        scheduleCount.value = endedSchedules(r).length
      }),
    )

    // 获取出勤率（非开发者）
    if (!auth.isDeveloper) {
      tasks.push(
        getAttendanceRate().then((r) => {
          topAttendance.value = r
            .filter((m) => m.attendance_rate !== null)
            .sort((a, b) => (b.attendance_rate ?? 0) - (a.attendance_rate ?? 0))
            .slice(0, 5)
        }),
      )

      // 获取职业分布
      tasks.push(
        getProfessionStats().then((r) => {
          professionStats.value = r
            .map((s) => ({ name: s.profession, count: s.count, color: profColor(s.profession) }))
            .sort((a, b) => b.count - a.count)
        }),
      )
    }

    await Promise.all(tasks)
  } catch {
    // 静默处理
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

/* ===== 主内容区 ===== */
.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.column {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* 左右两栏底部对齐：栏内最后一张卡片/条弹性填满剩余空间 */
.column > * {
  flex-shrink: 0;
}

.column > .card:last-child,
.column > .overview-bar:last-child {
  flex: 1;
}

/* 信息条层级：历史总览 — 内敛底色 */
.overview-bar {
  background: var(--ink-bg-wash);
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: none;
}

.overview-item {
  text-align: center;
}

.overview-item__value {
  font-size: 26px;
  font-weight: 900;
  color: var(--ink-900);
}

.overview-item__label {
  font-size: 12px;
  color: var(--ink-400);
  margin-top: 2px;
}

.overview-item__sep {
  width: 1px;
  height: 34px;
  background: linear-gradient(180deg, transparent, var(--gold-300), transparent);
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .overview-item__value {
    font-size: 22px;
  }
}
</style>

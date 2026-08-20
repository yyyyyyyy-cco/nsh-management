<template>
  <div class="dashboard page-enter">
    <!-- 欢迎区 -->
    <div class="welcome-section">
      <div class="welcome-left">
        <h2 class="welcome-title">{{ greetingText }}，{{ auth.user?.username }}</h2>
        <p class="welcome-date">{{ dateText }}</p>
      </div>
      <el-tag v-if="auth.user?.role" :type="roleTagType" size="large" effect="plain" round>
        {{ roleLabel }}
      </el-tag>
    </div>

    <!-- 今日比赛提醒 -->
    <div v-if="todaySchedules.length" class="today-banner" @click="goTodaySchedule">
      <div class="today-banner__badge">
        <el-icon><Bell /></el-icon>
      </div>
      <div class="today-banner__info">
        <span class="today-banner__title">今日比赛</span>
        <div class="today-banner__matches">
          <span v-for="s in todaySchedules" :key="s.id" class="today-banner__match">
            vs {{ s.opponent }} · {{ formatTime(s.match_time) }}{{ s.rounds ? ` · ${s.rounds}局` : '' }}
          </span>
        </div>
      </div>
      <el-button link type="primary" class="today-banner__link">
        前往查看 <el-icon><ArrowRight /></el-icon>
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-grid">
      <div v-for="(card, i) in statCards" :key="card.key" class="stat-card" :class="`stat-card--${card.theme}`" :style="{ animationDelay: `${i * 60}ms` }">
        <div class="stat-card__header">
          <span class="stat-card__label">{{ card.label }}</span>
          <el-icon class="stat-card__icon"><component :is="card.icon" /></el-icon>
        </div>
        <div class="stat-card__value">
          <span v-if="loading" class="stat-card__skeleton">-</span>
          <span v-else class="stat-card__number num">{{ card.value }}</span>
          <span class="stat-card__suffix">{{ card.suffix }}</span>
        </div>
        <div class="stat-card__track" />
      </div>
    </div>

    <!-- 主内容区：两栏布局 -->
    <div class="main-grid">
      <!-- 左栏 -->
      <div class="column">
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
            <template v-if="recentSchedules.length === 0">
              <div class="empty-state">
                <div class="empty-state__icon">&#x1F4C5;</div>
                <div class="empty-state__text">暂无比赛安排</div>
                <el-button type="primary" size="small" @click="router.push('/schedules')">创建比赛</el-button>
              </div>
            </template>
            <template v-else>
              <div
                v-for="s in recentSchedules"
                :key="s.id"
                class="schedule-item"
                @click="router.push(`/schedules/${s.id}`)"
              >
                <div class="schedule-item__date">
                  <span class="schedule-item__day num">{{ formatDay(s.match_time) }}</span>
                  <span class="schedule-item__month">{{ formatMonth(s.match_time) }}</span>
                </div>
                <div class="schedule-item__info">
                  <div class="schedule-item__opponent">vs {{ s.opponent }}</div>
                  <div class="schedule-item__meta">
                    <span>{{ formatTime(s.match_time) }}</span>
                    <el-tag v-if="s.result" :type="resultTagType(s.result)" size="small" effect="light">
                      {{ resultLabel(s.result) }}
                    </el-tag>
                  </div>
                </div>
                <el-icon class="schedule-item__arrow"><ArrowRight /></el-icon>
              </div>
            </template>
          </div>
        </div>

        <!-- 职业配置概览 -->
        <div v-if="!auth.isDeveloper" class="card">
          <div class="card__header">
            <div class="card__header-left">
              <el-icon class="card__header-icon"><PieChart /></el-icon>
              <span class="card__title">职业分布</span>
            </div>
          </div>
          <div class="card__body profession-grid">
            <div v-for="p in professionStats" :key="p.name" class="profession-item">
              <div class="profession-item__dot" :style="{ background: p.color }" />
              <span class="profession-item__name">{{ p.name }}</span>
              <span class="profession-item__count num">{{ p.count }}人</span>
            </div>
          </div>
        </div>

        <!-- 历史总览 -->
        <div class="overview-bar">
          <div class="overview-item">
            <div class="overview-item__value num">{{ memberCount }}</div>
            <div class="overview-item__label">帮众总数</div>
          </div>
          <div class="overview-item__sep" />
          <div class="overview-item">
            <div class="overview-item__value num">{{ scheduleCount }}</div>
            <div class="overview-item__label">历史比赛</div>
          </div>
        </div>
      </div>

      <!-- 右栏 -->
      <div class="column">
        <!-- 出勤率排行 -->
        <div v-if="!auth.isDeveloper" class="card">
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
            <template v-if="topAttendance.length === 0">
              <div class="empty-state">
                <div class="empty-state__icon">&#x1F465;</div>
                <div class="empty-state__text">暂无出勤数据</div>
              </div>
            </template>
            <template v-else>
              <div v-for="(m, i) in topAttendance" :key="m.member_id" class="rank-item">
                <span class="rank-item__number num" :class="`rank-item__number--${i + 1}`">
                  {{ i + 1 }}
                </span>
                <span class="rank-item__dot" :style="{ background: getProfColor(m.main_profession) }" />
                <span class="rank-item__name">{{ m.name }}</span>
                <el-progress
                  :percentage="(m.attendance_rate ?? 0) * 100"
                  :stroke-width="6"
                  :show-text="false"
                  :color="getProfColor(m.main_profession)"
                  style="flex: 1"
                />
                <span class="rank-item__rate num" :style="{ color: getProfColor(m.main_profession) }">
                  {{ m.attendance_rate != null ? `${ratePercent(m.attendance_rate)}%` : '-' }}
                </span>
              </div>
            </template>
          </div>
        </div>

        <!-- 快捷操作 -->
        <div class="card">
          <div class="card__header">
            <div class="card__header-left">
              <el-icon class="card__header-icon"><Lightning /></el-icon>
              <span class="card__title">快捷操作</span>
            </div>
          </div>
          <div class="quick-actions">
            <div
              v-for="action in quickActions"
              :key="action.path"
              class="quick-action"
              :style="{ '--action-color': action.color }"
              @click="router.push(action.path)"
            >
              <el-icon class="quick-action__icon" :style="{ background: action.color }"><component :is="action.icon" /></el-icon>
              <span class="quick-action__label">{{ action.label }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import {
  ArrowRight,
  Bell,
  Calendar,
  Lightning,
  Medal,
  PieChart,
  Setting,
  TrendCharts,
  Trophy,
  UserFilled,
} from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import { useAuthStore } from '@/stores/auth'
import { getProfessionStats, listMembers, getAttendanceRate, type AttendanceRateItem } from '@/api/members'
import { listSchedules } from '@/api/schedules'
import type { ScheduleInfo } from '@/types/schedule'

const router = useRouter()
const auth = useAuthStore()

const loading = ref(true)
const memberCount = ref(0)
const scheduleCount = ref(0)
const allSchedules = ref<ScheduleInfo[]>([])
const recentSchedules = ref<ScheduleInfo[]>([])
const topAttendance = ref<AttendanceRateItem[]>([])
const professionStats = ref<{ name: string; count: number; color: string }[]>([])

/** 今日比赛：从完整赛程中筛选（recentSchedules 仅保留 5 条，不能作为判断依据）。 */
const todaySchedules = computed(() =>
  allSchedules.value.filter((s) => dayjs(s.match_time).isSame(dayjs(), 'day')),
)

/** 职业色映射（依据 ui-style-guide，全站一致）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

/** 出勤率小数（0~1）转百分数整数。 */
function ratePercent(rate: number | null | undefined): number | string {
  return rate != null ? Math.round(rate * 100) : '-'
}

const dateText = dayjs().format('YYYY年M月D日 dddd')

const greetingText = computed(() => {
  const h = dayjs().hour()
  if (h < 6) return '深夜了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const roleTagType = computed(() => {
  const r = auth.user?.role
  return r === 'developer' ? 'info' : r === 'admin' ? 'danger' : ''
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  return r === 'developer' ? '开发者' : r === 'admin' ? '管理员' : '帮众'
})

const statCards = computed(() => {
  const topRate = topAttendance.value[0]?.attendance_rate
  return [
    { key: 'members', label: '帮众总数', value: memberCount.value, suffix: '人', icon: UserFilled, theme: 'primary' },
    { key: 'matches', label: '历史比赛', value: scheduleCount.value, suffix: '场', icon: Calendar, theme: 'gold' },
    { key: 'top', label: '出勤之星', value: topAttendance.value[0]?.name || '-', suffix: '', icon: Trophy, theme: 'success' },
    { key: 'rate', label: '最高出勤', value: topRate != null ? Math.round(topRate * 100) : '-', suffix: topRate != null ? '%' : '', icon: TrendCharts, theme: 'warning' },
  ]
})

const quickActions = computed(() => {
  if (auth.isDeveloper) {
    return [
      { label: '系统配置', icon: Setting, path: '/config', color: '#D97706' },
    ]
  }
  return [
    { label: '常驻库', icon: UserFilled, path: '/members', color: '#2E8B57' },
    { label: '联赛日程', icon: Calendar, path: '/schedules', color: '#c9a13b' },
    { label: '系统配置', icon: Setting, path: '/config', color: '#D97706' },
  ]
})

function getProfColor(prof: string) {
  return PROF_COLORS[prof] || '#999'
}

function formatDay(t: string) {
  return dayjs(t).format('DD')
}

function formatMonth(t: string) {
  return dayjs(t).format('M月')
}

function formatTime(t: string) {
  return dayjs(t).format('HH:mm')
}

function resultTagType(r: string) {
  return r === 'win' ? 'success' : r === 'lose' ? 'danger' : 'info'
}

function resultLabel(r: string) {
  return r === 'win' ? '胜利' : r === 'lose' ? '失败' : r === 'draw' ? '平局' : '待定'
}

/** 跳转今日第一场比赛详情（多条时前往第一条）。 */
function goTodaySchedule() {
  if (todaySchedules.value.length) {
    router.push(`/schedules/${todaySchedules.value[0].id}`)
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const tasks: Promise<void>[] = []

    // 获取成员数量
    tasks.push(
      listMembers({ page: 1, page_size: 1 }).then((r) => { memberCount.value = r.total })
    )

    // 获取近期比赛
    const start = dayjs().subtract(1, 'month').format('YYYY-MM-DD')
    const end = dayjs().add(1, 'month').format('YYYY-MM-DD')
    tasks.push(
      listSchedules({ start, end }).then((r) => {
        allSchedules.value = r
        recentSchedules.value = r.slice(0, 5)
        scheduleCount.value = r.length
      })
    )

    // 获取出勤率（非开发者）
    if (!auth.isDeveloper) {
      tasks.push(
        getAttendanceRate().then((r) => {
          topAttendance.value = r
            .filter((m) => m.attendance_rate !== null)
            .sort((a, b) => (b.attendance_rate ?? 0) - (a.attendance_rate ?? 0))
            .slice(0, 5)
        })
      )

      // 获取职业分布
      tasks.push(
        getProfessionStats().then((r) => {
          professionStats.value = r
            .map((s) => ({ name: s.profession, count: s.count, color: PROF_COLORS[s.profession] || '#999' }))
            .sort((a, b) => b.count - a.count)
        })
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

/* ===== 欢迎区 ===== */
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  margin: 0 0 4px 0;
}

.welcome-date {
  font-size: 13px;
  color: var(--ink-400);
  margin: 0;
}

/* ===== 今日比赛提醒横幅 ===== */
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

/* ===== 统计卡片 ===== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 18px 20px 16px;
  box-shadow: var(--shadow-sm);
  animation: card-rise 0.4s var(--ease-out) both;
  transition: transform var(--dur-normal) var(--ease-out), box-shadow var(--dur-normal) var(--ease-out);
}

@keyframes card-rise {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

/* 卡片底部渐变条 */
.stat-card__track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: var(--gold-line);
  opacity: 0.85;
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.stat-card__label {
  font-size: 13px;
  color: var(--ink-400);
}

.stat-card__icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  background: var(--gold-50);
}

.stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-card__number {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #d9b64a 0%, #c9a13b 55%, #b18c2c 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stat-card__suffix {
  font-size: 13px;
  color: var(--ink-400);
  font-weight: 400;
}

.stat-card__skeleton {
  font-size: 28px;
  color: var(--edge-strong);
}

.stat-card--success .stat-card__number {
  background: linear-gradient(135deg, #4da87b 0%, #2e8b57 60%, #3d9d6d 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stat-card--warning .stat-card__number {
  background: linear-gradient(135deg, #e2a33d 0%, #d97706 60%, #c26a05 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
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

/* ===== 通用卡片：顶部鎏金细条 ===== */
.card {
  position: relative;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gold-line);
  opacity: 0.6;
}

.card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--edge-faint);
}

.card__header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card__header-icon {
  font-size: 15px;
}

.card__title {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 1px;
}

.card__body {
  padding: 8px;
}

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

/* ===== 空状态 ===== */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px;
  gap: 8px;
}

.empty-state__icon {
  font-size: 32px;
  opacity: 0.5;
}

.empty-state__text {
  font-size: 13px;
  color: var(--ink-400);
}

/* ===== 职业分布 ===== */
.profession-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 16px !important;
}

.profession-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.profession-item__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.profession-item__name {
  color: var(--ink-600);
  flex: 1;
}

.profession-item__count {
  color: var(--ink-400);
  font-size: 12px;
}

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
  box-shadow: 0 2px 6px rgba(212, 160, 23, 0.4);
}

.rank-item__number--2 {
  background: linear-gradient(135deg, #c9c9c9, #9a9a9a);
  color: #fff;
  box-shadow: 0 2px 6px rgba(154, 154, 154, 0.35);
}

.rank-item__number--3 {
  background: linear-gradient(135deg, #e0a877, #b97f4b);
  color: #fff;
  box-shadow: 0 2px 6px rgba(185, 127, 75, 0.35);
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

/* ===== 快捷操作 ===== */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 16px;
  align-content: center; /* 卡片拉高时图标组垂直居中 */
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: var(--radius-md);
  border: 1px solid var(--edge-faint);
  cursor: pointer;
  transition: all var(--dur-normal) var(--ease-out);
}

.quick-action:hover {
  border-color: var(--gold-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-action__icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  color: #fff !important;
  box-shadow: var(--shadow-sm);
}

.quick-action__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-600);
}

/* ===== 历史总览 ===== */
.overview-bar {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  box-shadow: var(--shadow-sm);
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
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .main-grid {
    grid-template-columns: 1fr;
  }
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
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

  .stat-grid {
    grid-template-columns: 1fr;
  }
  .stat-card__number {
    font-size: 24px;
  }
  .welcome-title {
    font-size: 18px;
  }
  /* 欢迎区：角色标签换行，避免溢出 */
  .welcome-section {
    flex-wrap: wrap;
    gap: 8px;
  }
  .welcome-date {
    font-size: 12px;
  }
  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 12px;
  }
  .quick-action {
    padding: 12px 4px;
  }
  .quick-action__icon {
    width: 36px;
    height: 36px;
    font-size: 17px;
  }
  .profession-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .overview-item__value {
    font-size: 22px;
  }
  .card__header {
    padding: 12px;
  }
  .card__body {
    padding: 6px;
  }
}
</style>

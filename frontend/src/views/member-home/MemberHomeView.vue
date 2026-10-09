<!-- 帮众专属首页（/member-home，登录默认落点）：帮会战绩看板 + 录屏待办 + 快捷入口 -->
<template>
  <div class="member-home">
    <!-- 欢迎区：问候 + 日期一行铺开（页面标题用衬线，见 ui-style-guide §3.2） -->
    <div class="welcome">
      <h2 class="welcome-title">{{ greeting }}，{{ auth.user?.guild_name || auth.user?.username }}</h2>
      <p class="welcome-date">{{ dateText }}</p>
    </div>

    <div class="home-stack">
      <!-- 慢加载骨架（>200ms 才出现，避免快请求闪烁） -->
      <div v-if="showSkeleton" class="sk sk-block page-skeleton" />

      <!-- 加载失败 -->
      <div v-else-if="loadFailed" class="panel">
        <EmptyState variant="error" description="数据加载失败，请稍后重试" :image-size="72">
          <el-button @click="load">重试</el-button>
        </EmptyState>
      </div>

      <template v-else-if="!loading">
        <!-- 战绩统计卡（已赛场次 / 近5场战绩 / 局胜率 / 录屏完成） -->
        <GuildStatCards :stats="stats" />

        <!-- 录屏待办：一行状态条（赛后 7 天内存在未交齐/驳回时出现） -->
        <RecordingTodoStrip v-if="todo" :todo="todo" />

        <!-- 最近比赛结果 + 数据亮点 -->
        <div class="home-main">
          <RecentMatchesCard :matches="recentMatches" />
          <DataHighlightCard :data="highlight" :ready="highlightReady" />
        </div>

        <!-- 快捷操作 -->
        <MemberQuickActions />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import dayjs from 'dayjs'

import { getRecordings } from '@/api/recording'
import { listSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { endedSchedules } from '@/utils/scheduleSort'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import EmptyState from '@/components/common/EmptyState.vue'
import DataHighlightCard from './DataHighlightCard.vue'
import GuildStatCards from './GuildStatCards.vue'
import MemberQuickActions from './MemberQuickActions.vue'
import RecentMatchesCard from './RecentMatchesCard.vue'
import RecordingTodoStrip from './RecordingTodoStrip.vue'
import { fetchHighlight } from './highlight'
import { computeGuildStats, submittedRate, summarizeRecordings } from './stats'
import type { GuildStats, HighlightData, RecordingTodo } from './types'

const auth = useAuthStore()

const loading = ref(true) // 初始即加载态，避免先渲染空态再切骨架的闪烁
const showSkeleton = useSkeletonLoading(loading)
const loadFailed = ref(false)
const schedules = ref<ScheduleInfo[]>([])
const recordingRate = ref<number | null>(null)
const todo = ref<RecordingTodo | null>(null)
const highlight = ref<HighlightData | null>(null)
const highlightReady = ref(false)

const dateText = dayjs().format('YYYY年M月D日 dddd')
const greeting = computed(() => {
  const h = dayjs().hour()
  if (h < 6) return '深夜了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

/** 战绩统计（近 5 场口径）+ 最近一场录屏已交率 */
const stats = computed<GuildStats>(() => ({
  ...computeGuildStats(schedules.value),
  recordingRate: recordingRate.value,
}))

/** 最近比赛：已结束，取最近 5 场 */
const recentMatches = computed(() => endedSchedules(schedules.value).slice(0, 5))

onMounted(load)

// 请求序号：重试快速连点时丢弃过期响应
let loadSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  loadFailed.value = false
  highlightReady.value = false
  highlight.value = null
  recordingRate.value = null
  todo.value = null
  try {
    const list = await listSchedules()
    if (seq !== loadSeq) return
    schedules.value = list
    await loadRecordingTask(seq)
  } catch {
    // 错误提示由 HTTP 层统一处理，此处展示页内错误态
    if (seq === loadSeq) loadFailed.value = true
  } finally {
    if (seq === loadSeq) loading.value = false
  }
  // 数据亮点独立加载：不阻塞主骨架（卡片自带骨架态）
  if (!loadFailed.value && seq === loadSeq) void loadHighlight(seq)
}

/** 最近一场已结束比赛（仅赛后 7 天内）的录屏：已交率 + 待办名单；失败静默降级。 */
async function loadRecordingTask(seq: number) {
  const recent = endedSchedules(schedules.value)[0]
  if (!recent) return
  // 用户确认口径：仅赛后 7 天内提示，超期不再显示
  if (dayjs(recent.match_time).isBefore(dayjs().subtract(7, 'day'))) return
  try {
    const res = await getRecordings(recent.id)
    if (seq !== loadSeq) return
    const activeRounds = res.progress.filter((p) => p.total > 0)
    if (!activeRounds.length) return
    recordingRate.value = submittedRate(res.progress)
    const { missing, rejected } = summarizeRecordings(res.items, activeRounds.length)
    if (missing.length || rejected.length) {
      todo.value = {
        scheduleId: recent.id,
        dateText: dayjs(recent.match_time).format('M月D日'),
        missingNames: missing,
        rejectedNames: rejected,
      }
    }
  } catch {
    // 录屏进度为辅助信息：失败不阻断首页；统一错误提示仍由 HTTP 层负责
  }
}

/** 数据亮点：最近有比赛数据的一场（战报同源口径） */
async function loadHighlight(seq: number) {
  highlight.value = await fetchHighlight(schedules.value, () => seq !== loadSeq)
  if (seq === loadSeq) highlightReady.value = true
}
</script>

<style scoped>
/* finesse · register=product · shell=member-home: 全宽纵排看板（统计卡 → 录屏状态条 → 最近比赛+数据亮点双栏 → 快捷入口）；≤900px 单列 */
.member-home {
  max-width: 1200px;
}

.welcome {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 4px 16px;
  margin-bottom: 20px;
}

.welcome-title {
  margin: 0;
  font-family: var(--font-serif);
  font-size: 22px;
  font-weight: 700;
  letter-spacing: 2px;
  overflow-wrap: anywhere;
}

.welcome-date {
  margin: 0;
  font-size: 13px;
  color: var(--ink-400);
}

.home-stack {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-skeleton {
  height: 320px;
  border-radius: var(--radius-lg);
}

.panel {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

/* 最近比赛（左，自适应）+ 数据亮点（右，380px） */
.home-main {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 16px;
  align-items: start;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .home-main {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome {
    margin-bottom: 14px;
  }

  .welcome-title {
    font-size: 19px;
  }

  .home-stack {
    gap: 12px;
  }

  .home-main {
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 17px;
  }
}
</style>

<template>
  <div class="schedule-detail">
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <div class="card-header__left">
            <el-icon class="card-header__icon"><Calendar /></el-icon>
            <span>赛程详情</span>
            <span v-if="schedule" class="card-header__opponent">vs {{ schedule.opponent }}</span>
          </div>
          <div>
            <el-button @click="goBack">返回</el-button>
            <el-button v-if="auth.isAdmin" type="primary" @click="formVisible = true">编辑</el-button>
            <el-button v-if="auth.isAdmin" type="danger" plain @click="onDelete">删除赛程</el-button>
          </div>
        </div>
      </template>
      <!-- 信息卡骨架 -->
      <div v-if="showSkeleton && !schedule" class="sk-desc">
        <div v-for="i in 4" :key="i" class="sk-desc__row">
          <span class="sk sk-line" style="width:80px" />
          <span class="sk sk-line" style="width:1fr;flex:1" />
        </div>
      </div>
      <el-descriptions v-else-if="schedule" :column="2" border>
        <el-descriptions-item label="对手">{{ schedule.opponent }}</el-descriptions-item>
        <el-descriptions-item label="比赛时间">{{ formatTime(schedule.match_time) }}</el-descriptions-item>
        <el-descriptions-item label="局数">{{ schedule.rounds }}局</el-descriptions-item>
        <el-descriptions-item label="比赛结果">
          <el-tag :type="resultType(schedule.result)" effect="light">{{ resultLabel(schedule.result) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="每局结果">
          <template v-if="schedule.round_results?.length">
            <el-tag
              v-for="(r, index) in schedule.round_results"
              :key="index"
              :type="resultType(r)"
              effect="light"
              class="round-tag"
            >
              第{{ index + 1 }}局：{{ resultLabel(r) }}
            </el-tag>
          </template>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>
    </el-card>

    <el-card shadow="never" class="tabs-card">
      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- lazy：tab-pane 首次激活时才渲染挂载（避免进入页面同时挂载 4 个主 Tab
             并发发请求；首次激活由子组件 onMounted 加载，后续切回由 onTabChange reload 刷新） -->
        <el-tab-pane v-if="!isMember" lazy label="出勤库" name="attendance">
          <AttendanceTab v-if="schedule" :schedule-id="schedule.id" :schedule="schedule" />
        </el-tab-pane>
        <el-tab-pane v-if="!isMember" lazy label="排表" name="lineup">
          <LineupTab ref="lineupTabRef" v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
        <el-tab-pane lazy label="录屏审核" name="recording">
          <RecordingTab ref="recordingTabRef" v-if="schedule" :schedule-id="schedule.id" />
        </el-tab-pane>
        <el-tab-pane lazy label="数据分析" name="analysis">
          <MatchDataTab v-if="schedule" :schedule-id="schedule.id" :schedule="schedule" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <ScheduleFormDialog v-model="formVisible" :schedule="schedule" @success="load" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Calendar } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'

import { deleteSchedule, getSchedule } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { resultLabel, resultType } from '@/utils/constants'
import AttendanceTab from '@/components/attendance/AttendanceTab.vue'
import LineupTab from '@/components/lineups/LineupTab.vue'
import RecordingTab from '@/components/recording/RecordingTab.vue'
import MatchDataTab from '@/components/match-data/MatchDataTab.vue'
import ScheduleFormDialog from '@/components/schedules/ScheduleFormDialog.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const isMember = computed(() => auth.user?.role === 'member')
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const schedule = ref<ScheduleInfo | null>(null)
const formVisible = ref(false)

// 初始 Tab：支持 ?tab=recording 直达录屏；帮众默认录屏页
const VALID_TABS = ['attendance', 'lineup', 'recording', 'analysis']
const defaultTab = auth.user?.role === 'member' ? 'recording' : 'attendance'
const activeTab = ref(VALID_TABS.includes(String(route.query.tab)) ? String(route.query.tab) : defaultTab)

const formatTime = (value: string) => dayjs(value).format('YYYY-MM-DD HH:mm')

onMounted(load)

/** 返回：带 from 来源参数时显式回跳（联赛总览/帮众首页），避免依赖浏览器历史栈导致后退异常。 */
function goBack() {
  if (route.query.from === 'overview') {
    router.push({ name: 'league-overview' })
  } else if (route.query.from === 'home') {
    router.push({ name: 'member-home' })
  } else {
    router.back()
  }
}

const lineupTabRef = ref<InstanceType<typeof LineupTab>>()
const recordingTabRef = ref<InstanceType<typeof RecordingTab>>()

/** 切到排表/录屏 Tab 时刷新（同步出勤库新增的补人/成员），并把当前 Tab 写入 URL 便于刷新后保持。 */
function onTabChange(name: string | number) {
  if (name === 'lineup') lineupTabRef.value?.reload()
  if (name === 'recording') recordingTabRef.value?.reload()
  router.replace({ query: { ...route.query, tab: String(name) } })
}

async function load() {
  loading.value = true
  try {
    schedule.value = await getSchedule(Number(route.params.id))
  } catch {
    // 错误提示已由 http 拦截器统一处理，此处仅保证 loading 关闭
  } finally {
    loading.value = false
  }
}

async function onDelete() {
  if (!schedule.value) return
  await ElMessageBox.confirm(
    `确定删除赛程「${schedule.value.opponent}」吗？将同时删除关联的出勤、排表、录屏和分析数据。`,
    '提示',
    { type: 'warning' },
  )
  await deleteSchedule(schedule.value.id)
  ElMessage.success('删除成功')
  router.push({ name: 'schedules' })
}
</script>

<style scoped>
/* finesse · register=product · shell=member-detail: row-list(≤768px) + table(桌面) */

/* ===== 信息卡骨架：2×2 描述格占位 ===== */
.sk-desc { display: flex; flex-direction: column; gap: 12px; padding: 4px 0; }
.sk-desc__row { display: flex; align-items: center; gap: 16px; }
.sk-desc__row .sk { height: 14px; }

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header__left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-serif);
  font-weight: 700;
  letter-spacing: 1px;
}

.card-header__icon {
  font-size: 15px;
}

.card-header__opponent {
  font-size: 12px;
  font-weight: 400;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 1px 10px;
}

.round-tag {
  margin-right: 8px;
}

.tabs-card {
  margin-top: 16px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .card-header__left {
    font-size: 14px;
  }

  .card-header > div:last-child {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-end;
    gap: 6px;
    width: 100%;
  }

  /* 页头按钮紧凑化（32px、内容宽度右对齐），与列表行操作按钮同款 */
  .card-header > div:last-child .el-button {
    height: 32px;
    margin-left: 0;
    padding: 0 14px;
    font-size: 13px;
  }

  /* 卡片内边距收紧，释放手机端内容宽度 */
  .info-card :deep(.el-card__header),
  .tabs-card :deep(.el-card__header) {
    padding: 12px 14px;
  }

  .info-card :deep(.el-card__body),
  .tabs-card :deep(.el-card__body) {
    padding: 14px;
  }

  /* 将带 border 的描述列表从表格布局转为网格布局，
     让每组 label + content 保持同行排列，避免窄屏两列挤压。 */
  .info-card :deep(.el-descriptions__body table),
  .info-card :deep(.el-descriptions__table) {
    display: block;
  }

  .info-card :deep(tbody) {
    display: block;
  }

  .info-card :deep(tr) {
    display: grid;
    grid-template-columns: auto 1fr;
    gap: 0;
    border-bottom: 1px solid var(--edge-faint);
    padding: 6px 0;
  }

  .info-card :deep(tr:last-child) {
    border-bottom: none;
    padding-bottom: 0;
  }

  .info-card :deep(.el-descriptions__cell) {
    border: none !important;
    padding: 2px 6px;
    background: transparent !important;
    font-size: 13px;
    word-break: break-word;
  }

  .info-card :deep(.el-descriptions__label.is-bordered-label) {
    color: var(--ink-400);
    font-weight: 500;
    font-size: 12px;
    white-space: nowrap;
    min-width: 3em;
  }

  /* 每局结果标签换行 */
  .round-tag {
    margin-right: 0;
    margin-bottom: 4px;
    display: inline-block;
  }
}
</style>

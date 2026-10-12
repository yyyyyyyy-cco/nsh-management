<!-- 成员详情页（管理员）：成员信息卡 + 档案 Tabs（历史战绩 / 出勤档案 / 录屏记录 / 排表历史） -->
<template>
  <div class="member-detail">
    <!-- 成员信息卡 -->
    <el-card shadow="never" class="info-card">
      <template #header>
        <div class="card-header">
          <div class="card-header__left">
            <el-icon class="card-header__icon"><UserFilled /></el-icon>
            <span>成员详情</span>
          </div>
          <el-button @click="goBack">返回常驻库</el-button>
        </div>
      </template>

      <!-- 信息卡骨架 -->
      <div v-if="showSkeleton && !member && !loadFailed" class="sk-desc">
        <div v-for="i in 2" :key="i" class="sk-desc__row">
          <span class="sk sk-line" style="width: 80px" />
          <span class="sk sk-line" style="flex: 1" />
        </div>
      </div>

      <!-- 成员不存在/加载失败（错误提示由 http 拦截器统一处理） -->
      <EmptyState v-else-if="loadFailed" variant="error" description="成员不存在或已删除" :image-size="72">
        <el-button @click="goBack">返回常驻库</el-button>
      </EmptyState>

      <MemberDetailHeader v-else-if="member" :member="member" :attendance-rate="attendanceRate" />
    </el-card>

    <!-- 档案 Tabs：历史战绩（默认，原有组件区迁入；合并新旧 ID，冲突时提示并跳转精确查询）
         + 三个档案 Tab（lazy 首次激活才挂载与请求） -->
    <el-tabs v-if="member" v-model="activeTab" class="archive-tabs">
      <el-tab-pane label="历史战绩" name="stats">
        <template v-if="summary && records.length > 0">
          <StatsIdentityNotice :identity="identity" />
          <StatsOverview :summary="summary" class="section" />
          <StatsTrendChart :records="records" class="section" />
          <StatsRankingPosition :records="records" class="section" />
          <StatsMatchTable :records="records" class="section" />
        </template>
        <el-card v-else-if="statsConflict" shadow="never" class="empty-card">
          <EmptyState variant="error" :description="statsConflict" :image-size="72">
            <el-button type="primary" plain @click="goExactStats">前往个人战绩精确查询</el-button>
          </EmptyState>
        </el-card>
        <el-card v-else shadow="never" class="empty-card">
          <EmptyState variant="chart" description="该成员暂无比赛数据" :image-size="72" />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="出勤档案" name="attendance" lazy>
        <MemberAttendanceHistory :member-id="memberId" />
      </el-tab-pane>
      <el-tab-pane label="录屏记录" name="recording" lazy>
        <MemberRecordingHistory :member-id="memberId" />
      </el-tab-pane>
      <el-tab-pane label="排表历史" name="lineup" lazy>
        <MemberLineupHistory :member-id="memberId" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UserFilled } from '@element-plus/icons-vue'

import { getAttendanceRate, getMember } from '@/api/members'
import { getMyStats } from '@/api/myStats'
import type { MemberInfo } from '@/types/member'
import type { PlayerIdentity, PlayerRecord, PlayerSummary } from '@/types/myStats'
import MemberAttendanceHistory from '@/components/members/MemberAttendanceHistory.vue'
import MemberDetailHeader from '@/components/members/MemberDetailHeader.vue'
import MemberLineupHistory from '@/components/members/MemberLineupHistory.vue'
import MemberRecordingHistory from '@/components/members/MemberRecordingHistory.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatsIdentityNotice from '@/components/my-stats/StatsIdentityNotice.vue'
import StatsMatchTable from '@/components/my-stats/StatsMatchTable.vue'
import StatsOverview from '@/components/my-stats/StatsOverview.vue'
import StatsRankingPosition from '@/components/my-stats/StatsRankingPosition.vue'
import StatsTrendChart from '@/components/my-stats/StatsTrendChart.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const route = useRoute()
const router = useRouter()
const memberId = Number(route.params.id)

// 档案 Tab 切换（历史战绩默认；档案 Tab lazy 首次激活加载）
const activeTab = ref('stats')

// 初始即加载态，避免先渲染空态再切骨架的闪烁
const loading = ref(true)
const showSkeleton = useSkeletonLoading(loading)
const loadFailed = ref(false)
const member = ref<MemberInfo | null>(null)
const attendanceRate = ref<number | null>(null)
const records = ref<PlayerRecord[]>([])
const summary = ref<PlayerSummary | null>(null)
const identity = ref<PlayerIdentity | null>(null)
const statsConflict = ref<string | null>(null)

async function load() {
  loading.value = true
  loadFailed.value = false
  statsConflict.value = null
  try {
    const m = await getMember(memberId)
    member.value = m
    // 战绩：默认合并已确认的新旧 ID；单独捕获冲突，避免与“成员不存在”共用错误态
    const [rates, stats] = await Promise.all([
      getAttendanceRate(),
      getMyStats(m.name).catch((error) => {
        const status = (error as { response?: { status?: number } })?.response?.status
        if (status === 409) {
          statsConflict.value =
            (error as { response?: { data?: { message?: string } } })?.response?.data?.message ||
            '该 ID 存在名称归属冲突，无法自动合并'
        }
        return null
      }),
    ])
    attendanceRate.value = rates.find((r) => r.member_id === memberId)?.attendance_rate ?? null
    if (stats) {
      records.value = stats.records
      summary.value = stats.summary
      identity.value = stats.identity
    }
  } catch {
    loadFailed.value = true
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/members')
}

/** 冲突退路：到个人战绩按该 ID 精确查询（不合并历史 ID，不冒认归属） */
function goExactStats() {
  if (!member.value) return
  router.push({ name: 'my-stats', query: { player_name: member.value.name, merge_aliases: 'false' } })
}

onMounted(load)
</script>

<style scoped>
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card-header__left {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--ink-900);
}

.card-header__icon {
  font-size: 18px;
  color: var(--gold-600);
}

.sk-desc {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.sk-desc__row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section {
  margin-top: 16px;
}

.archive-tabs {
  margin-top: 16px;
}

.archive-tabs :deep(.el-tabs__content) {
  padding-top: 4px;
}

/* finesse · register=product · shell=member-detail: info-card（header + 骨架/错误态）+ my-stats 战绩区复用；≤768px 卡片内边距收紧 */
@media (max-width: 768px) {
  .info-card :deep(.el-card__body),
  .empty-card :deep(.el-card__body) {
    padding: 14px;
  }
}
</style>

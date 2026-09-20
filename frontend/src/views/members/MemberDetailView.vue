<!-- 成员详情页（管理员）：成员信息卡 + 历史战绩（复用个人战绩组件，最近 10 场） -->
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
          <span class="sk sk-line" style="width:80px" />
          <span class="sk sk-line" style="flex:1" />
        </div>
      </div>

      <!-- 成员不存在/加载失败（错误提示由 http 拦截器统一处理） -->
      <EmptyState v-else-if="loadFailed" variant="error" description="成员不存在或已删除" :image-size="72">
        <el-button @click="goBack">返回常驻库</el-button>
      </EmptyState>

      <MemberDetailHeader v-else-if="member" :member="member" :attendance-rate="attendanceRate" />
    </el-card>

    <!-- 历史战绩（按成员名=游戏 ID 精确匹配，复用个人战绩组件） -->
    <template v-if="member">
      <template v-if="summary && records.length > 0">
        <StatsOverview :summary="summary" class="section" />
        <StatsTrendChart :records="records" class="section" />
        <StatsRankingPosition :records="records" class="section" />
        <StatsMatchTable :records="records" class="section" />
      </template>
      <el-card v-else shadow="never" class="empty-card section">
        <EmptyState variant="chart" description="该成员暂无比赛数据" :image-size="72" />
      </el-card>
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { UserFilled } from '@element-plus/icons-vue'

import { getAttendanceRate, getMember } from '@/api/members'
import { getMyStats } from '@/api/myStats'
import type { MemberInfo } from '@/types/member'
import type { PlayerRecord, PlayerSummary } from '@/types/myStats'
import MemberDetailHeader from '@/components/members/MemberDetailHeader.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import StatsMatchTable from '@/components/my-stats/StatsMatchTable.vue'
import StatsOverview from '@/components/my-stats/StatsOverview.vue'
import StatsRankingPosition from '@/components/my-stats/StatsRankingPosition.vue'
import StatsTrendChart from '@/components/my-stats/StatsTrendChart.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const route = useRoute()
const router = useRouter()

// 初始即加载态，避免先渲染空态再切骨架的闪烁
const loading = ref(true)
const showSkeleton = useSkeletonLoading(loading)
const loadFailed = ref(false)
const member = ref<MemberInfo | null>(null)
const attendanceRate = ref<number | null>(null)
const records = ref<PlayerRecord[]>([])
const summary = ref<PlayerSummary | null>(null)

async function load() {
  const id = Number(route.params.id)
  loading.value = true
  loadFailed.value = false
  try {
    const m = await getMember(id)
    // 战绩与出勤率并行加载（战绩按成员名精确匹配游戏 ID）
    const [stats, rates] = await Promise.all([getMyStats(m.name), getAttendanceRate()])
    member.value = m
    records.value = stats.records
    summary.value = stats.summary
    attendanceRate.value = rates.find((r) => r.member_id === id)?.attendance_rate ?? null
  } catch {
    loadFailed.value = true
  } finally {
    loading.value = false
  }
}

function goBack() {
  router.push('/members')
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

/* finesse · register=product · shell=member-detail: info-card（header + 骨架/错误态）+ my-stats 战绩区复用；≤768px 卡片内边距收紧 */
@media (max-width: 768px) {
  .info-card :deep(.el-card__body),
  .empty-card :deep(.el-card__body) {
    padding: 14px;
  }
}
</style>

<template>
  <div class="my-stats">
    <div class="toolbar">
      <div class="toolbar-info">
        <el-icon class="info-icon"><TrendCharts /></el-icon>
        <span>个人战绩</span>
        <span v-if="summary" class="info-sub">查询结果：{{ summary.player_name }}</span>
      </div>
    </div>

    <PlayerSearch :loading="loading" @search="onSearch" />

    <!-- 查询中 -->
    <div v-if="showSkeleton" class="stats-skeleton">
      <div class="sk sk-block" style="height:88px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:300px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:220px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:280px;border-radius:var(--radius-lg)" />
    </div>

    <!-- 空状态 -->
    <EmptyState v-else-if="queried && records.length === 0" variant="search" description="未找到该 ID 的比赛数据，请确认 ID 是否正确" />

    <!-- 结果 -->
    <div v-else-if="records.length > 0" class="soft-appear">
      <StatsOverview v-if="summary" :summary="summary" class="section" />
      <StatsTrendChart :records="records" class="section" />
      <StatsRankingPosition :records="records" class="section" />
      <StatsMatchTable :records="records" class="section" />
    </div>

    <!-- 初始状态 -->
    <EmptyState v-else variant="search" description="输入你的游戏 ID，查看个人历史战绩" />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { TrendCharts } from '@element-plus/icons-vue'

import { getMyStats } from '@/api/myStats'
import EmptyState from '@/components/common/EmptyState.vue'
import type { PlayerRecord, PlayerSummary } from '@/types/myStats'
import PlayerSearch from '@/components/my-stats/PlayerSearch.vue'
import StatsOverview from '@/components/my-stats/StatsOverview.vue'
import StatsTrendChart from '@/components/my-stats/StatsTrendChart.vue'
import StatsMatchTable from '@/components/my-stats/StatsMatchTable.vue'
import StatsRankingPosition from '@/components/my-stats/StatsRankingPosition.vue'

import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const queried = ref(false)
const records = ref<PlayerRecord[]>([])
const summary = ref<PlayerSummary | null>(null)

async function onSearch(name: string) {
  loading.value = true
  queried.value = true
  records.value = []
  summary.value = null
  try {
    const data = await getMyStats(name)
    records.value = data.records
    summary.value = data.summary
  } catch {
    // 错误提示已由 http 拦截器统一处理
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.toolbar-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 1px;
}

.info-icon {
  font-size: 18px;
}

.info-sub {
  font-family: var(--font-sans);
  font-size: 12px;
  font-weight: 400;
  color: var(--ink-400);
  letter-spacing: 0;
}

.section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    gap: 10px;
  }
  .toolbar-info {
    font-size: 15px;
  }
  .info-sub {
    display: none;
  }
}
</style>

<template>
  <div class="my-stats">
    <div class="toolbar">
      <div class="toolbar-info">
        <el-icon class="info-icon"><TrendCharts /></el-icon>
        <span>个人战绩</span>
        <span v-if="summary" class="info-sub">查询结果：{{ summary.player_name }}</span>
      </div>
      <!-- 合并历史 ID / 仅查此 ID（默认合并） -->
      <el-radio-group v-model="mergeAliases" size="small" class="mode-switch" @change="onModeChange">
        <el-radio-button :value="true">合并历史 ID</el-radio-button>
        <el-radio-button :value="false">仅查此 ID</el-radio-button>
      </el-radio-group>
    </div>

    <PlayerSearch :loading="loading" :initial-name="inputName" @search="onSearch" />

    <!-- 查询中 -->
    <div v-if="showSkeleton" class="stats-skeleton">
      <div class="sk sk-block" style="height:88px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:300px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:220px;margin-bottom:16px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:280px;border-radius:var(--radius-lg)" />
    </div>

    <template v-else>
      <!-- 合并冲突：不展示旧结果，提供仅查此 ID -->
      <EmptyState v-if="conflict" variant="error" :description="conflict" :image-size="72" class="section">
        <el-button type="primary" plain @click="useExactMode">仅查此 ID</el-button>
      </EmptyState>

      <!-- 名称归属/关联说明 -->
      <StatsIdentityNotice v-else-if="identity" class="section" :identity="identity" @exact="useExactMode" />

      <!-- 空状态（已查询但无数据） -->
      <EmptyState
        v-if="!conflict && queried && records.length === 0"
        variant="search"
        description="未找到该 ID 的比赛数据，请确认 ID 是否正确"
        class="section"
      />

      <!-- 结果 -->
      <div v-else-if="!conflict && records.length > 0" class="soft-appear">
        <StatsOverview v-if="summary" :summary="summary" class="section" />
        <StatsTrendChart :records="records" class="section" />
        <StatsRankingPosition :records="records" class="section" />
        <StatsMatchTable :records="records" class="section" />
      </div>

      <!-- 初始状态 -->
      <EmptyState
        v-else-if="!conflict && !queried"
        variant="search"
        description="输入当前或历史游戏 ID，查看个人历史战绩"
        class="section"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { TrendCharts } from '@element-plus/icons-vue'

import { getMyStats } from '@/api/myStats'
import EmptyState from '@/components/common/EmptyState.vue'
import type { PlayerIdentity, PlayerRecord, PlayerSummary } from '@/types/myStats'
import PlayerSearch from '@/components/my-stats/PlayerSearch.vue'
import StatsIdentityNotice from '@/components/my-stats/StatsIdentityNotice.vue'
import StatsOverview from '@/components/my-stats/StatsOverview.vue'
import StatsTrendChart from '@/components/my-stats/StatsTrendChart.vue'
import StatsMatchTable from '@/components/my-stats/StatsMatchTable.vue'
import StatsRankingPosition from '@/components/my-stats/StatsRankingPosition.vue'

import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const route = useRoute()

const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const queried = ref(false)
const records = ref<PlayerRecord[]>([])
const summary = ref<PlayerSummary | null>(null)
const identity = ref<PlayerIdentity | null>(null)
const conflict = ref<string | null>(null)
const inputName = ref('')
const mergeAliases = ref(true)

// 请求序号：模式/名称快速切换时丢弃过期响应
let loadSeq = 0

/** 错误响应中提取 message（http 拦截器已提示，这里仅用于冲突态展示）。 */
function errorMessage(error: unknown): string {
  const data = (error as { response?: { data?: { message?: string } } })?.response?.data
  return data?.message || '查询失败，请稍后重试'
}

async function query(name: string, merge = mergeAliases.value) {
  const seq = ++loadSeq
  loading.value = true
  queried.value = true
  records.value = []
  summary.value = null
  identity.value = null
  conflict.value = null
  try {
    const data = await getMyStats(name, merge)
    if (seq !== loadSeq) return
    records.value = data.records
    summary.value = data.summary
    identity.value = data.identity
  } catch (error) {
    if (seq !== loadSeq) return
    const status = (error as { response?: { status?: number } })?.response?.status
    // 合并冲突：明确提示并可切换到「仅查此 ID」（其余错误由拦截器统一提示）
    if (status === 409) conflict.value = errorMessage(error)
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

function onSearch(name: string) {
  inputName.value = name
  query(name)
}

/** 切换合并/精确模式：有输入时立即按新模式重查 */
function onModeChange() {
  if (inputName.value.trim()) query(inputName.value.trim())
}

/** 冲突退路：改用精确查询（不合并历史 ID） */
function useExactMode() {
  mergeAliases.value = false
  if (inputName.value.trim()) query(inputName.value.trim(), false)
}

onMounted(() => {
  // 支持从成员详情跳转：?player_name=xxx&merge_aliases=false
  const name = String(route.query.player_name || '').trim()
  if (route.query.merge_aliases === 'false') mergeAliases.value = false
  if (name) {
    inputName.value = name
    query(name)
  }
})
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
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

.mode-switch :deep(.el-radio-button__inner) {
  height: 32px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  font-size: 12.5px;
}

.section {
  margin-top: 16px;
}

@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    align-items: center;
  }
  .toolbar-info {
    font-size: 15px;
    width: 100%;
  }
  .info-sub {
    display: none;
  }
  .mode-switch {
    width: 100%;
  }
  .mode-switch :deep(.el-radio-button) {
    flex: 1;
  }
  .mode-switch :deep(.el-radio-button__inner) {
    width: 100%;
    justify-content: center;
  }
}
</style>

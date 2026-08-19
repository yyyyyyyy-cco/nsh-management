<template>
  <div class="match-data-tab">
    <!-- 阵营统计 -->
    <div v-if="camps.length > 0" class="stats-bar">
      <div v-for="(camp, i) in camps" :key="camp.camp" class="stat">
        <span class="stat-label">
          <i class="stat-dot" :style="{ background: campColor(i) }" />
          {{ camp.camp }}
        </span>
        <span class="value num">{{ camp.player_count }} 人</span>
        <span class="detail">击杀 <em class="num">{{ camp.total_kills }}</em> · 伤害 <em class="num">{{ formatNumber(camp.total_damage) }}</em></span>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <el-button v-if="auth.isAdmin" type="primary" :loading="importing" @click="onImport">
        导入 CSV
      </el-button>
      <el-select v-model="selectedCamp" placeholder="阵营筛选" clearable style="width: 150px">
        <el-option v-for="camp in camps" :key="camp.camp" :label="camp.camp" :value="camp.camp" />
      </el-select>
      <el-input v-model="nameFilter" placeholder="按ID搜索" clearable style="width: 180px" :prefix-icon="Search" />
      <div class="spacer" />
      <el-button v-if="items.length > 0" @click="onExportReport">导出报告</el-button>
    </div>

    <!-- 数据为空提示 -->
    <el-empty v-if="!loading && items.length === 0" description="暂无比赛数据，请导入 CSV 文件">
      <el-button v-if="auth.isAdmin" type="primary" @click="onImport">导入 CSV</el-button>
    </el-empty>

    <!-- 标签页切换 -->
    <el-tabs v-else v-model="activeTab">
      <!-- 数据总览 -->
      <el-tab-pane label="数据总览" name="overview">
        <OverviewTab :items="filteredItems" :camps="camps" />
      </el-tab-pane>

      <!-- 数据列表 -->
      <el-tab-pane label="数据列表" name="list">
        <el-table v-loading="loading" :data="filteredItems" max-height="500">
          <el-table-column prop="player_name" label="ID" min-width="100" />
          <el-table-column prop="profession" label="职业" min-width="70" />
          <el-table-column prop="camp" label="阵营" min-width="100" />
          <el-table-column prop="kills" label="击杀" min-width="70" align="right" sortable />
          <el-table-column prop="assists" label="助攻" min-width="70" align="right" sortable />
          <el-table-column prop="player_damage" label="伤害" min-width="90" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.player_damage) }}</template>
          </el-table-column>
          <el-table-column prop="healing" label="治疗" min-width="90" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.healing) }}</template>
          </el-table-column>
          <el-table-column prop="damage_taken" label="承伤" min-width="90" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.damage_taken) }}</template>
          </el-table-column>
          <el-table-column prop="deaths" label="重伤" min-width="70" align="right" sortable />
          <el-table-column prop="fen_gu" label="焚骨" min-width="70" align="right" sortable />
        </el-table>
      </el-tab-pane>

      <!-- 排行榜（折线图 + 四榜） -->
      <el-tab-pane label="排行榜" name="ranking">
        <RankingTab :items="filteredItems" :rankings="rankings" />
      </el-tab-pane>

      <!-- 职业分析 -->
      <el-tab-pane label="职业分析" name="profession">
        <ProfessionTab :items="filteredItems" />
      </el-tab-pane>

      <!-- 综合评分 -->
      <el-tab-pane label="综合评分" name="score">
        <ScoreTab :items="filteredItems" />
      </el-tab-pane>
    </el-tabs>

    <!-- 隐藏的文件输入 -->
    <input ref="fileInput" type="file" accept=".csv" style="display: none" @change="onFileChange" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

import { getMatchData, getRankings, getReportUrl, importCsv } from '@/api/matchData'
import type { CampStats, MatchData, RankingsResponse } from '@/types/matchData'
import { useAuthStore } from '@/stores/auth'
import { CAMP_COLORS } from './analysis'
import OverviewTab from './OverviewTab.vue'
import RankingTab from './RankingTab.vue'
import ProfessionTab from './ProfessionTab.vue'
import ScoreTab from './ScoreTab.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const importing = ref(false)
const items = ref<MatchData[]>([])
const camps = ref<CampStats[]>([])
const selectedCamp = ref('')
const nameFilter = ref('')
const activeTab = ref('overview')
const fileInput = ref<HTMLInputElement | null>(null)
const rankings = ref<RankingsResponse>({
  kills_ranking: [],
  damage_ranking: [],
  healing_ranking: [],
  fen_gu_ranking: [],
})

function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}

const filteredItems = computed(() => {
  let list = items.value
  if (selectedCamp.value) {
    list = list.filter((r) => r.camp === selectedCamp.value)
  }
  const kw = nameFilter.value.trim()
  if (kw) {
    list = list.filter((r) => r.player_name.includes(kw))
  }
  return list
})

onMounted(load)

async function load() {
  loading.value = true
  try {
    const data = await getMatchData(props.scheduleId)
    items.value = data.items
    camps.value = data.camps
    await loadRankings()
  } finally {
    loading.value = false
  }
}

async function loadRankings() {
  rankings.value = await getRankings(props.scheduleId, {
    camp: selectedCamp.value || undefined,
    limit: 10,
  })
}

function onImport() {
  fileInput.value?.click()
}

async function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  importing.value = true
  try {
    const result = await importCsv(props.scheduleId, file)
    ElMessage.success(result.message)
    load()
  } finally {
    importing.value = false
    input.value = ''  // 重置 input
  }
}

function onExportReport() {
  const url = getReportUrl(props.scheduleId)
  window.open(url, '_blank')
}

function formatNumber(value: number): string {
  if (value >= 10000) {
    return (value / 10000).toFixed(1) + '万'
  }
  return value.toLocaleString()
}
</script>

<style scoped>
.stats-bar {
  display: flex;
  gap: 24px;
  padding: 14px 20px;
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 60%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-700);
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.value {
  font-size: 20px;
  font-weight: 800;
  color: var(--gold-700);
}

.detail {
  font-size: 11px;
  color: var(--ink-400);
}

.detail em {
  font-style: normal;
  font-weight: 700;
  color: var(--ink-600);
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.spacer {
  flex: 1;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .stats-bar {
    flex-wrap: wrap;
    gap: 10px 20px;
    padding: 12px 14px;
  }

  .stat {
    flex: 1 1 calc(50% - 10px);
    min-width: 0;
  }

  .value {
    font-size: 18px;
  }

  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .toolbar .el-select,
  .toolbar .el-input {
    flex: 1 1 calc(50% - 4px);
    width: auto !important;
  }

  .toolbar .el-button {
    flex: 1 1 calc(50% - 4px);
    margin-left: 0 !important;
  }
}
</style>

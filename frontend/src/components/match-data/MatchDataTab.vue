<template>
  <div class="match-data-tab">
    <!-- 阵营统计 -->
    <div v-if="camps.length > 0" class="stats-bar">
      <div v-for="camp in camps" :key="camp.camp" class="stat">
        <span class="label">{{ camp.camp }}</span>
        <span class="value">{{ camp.player_count }} 人</span>
        <span class="detail">击杀 {{ camp.total_kills }} | 伤害 {{ formatNumber(camp.total_damage) }}</span>
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
      <div class="spacer" />
      <el-button v-if="items.length > 0" @click="onExportReport">导出报告</el-button>
    </div>

    <!-- 数据为空提示 -->
    <el-empty v-if="!loading && items.length === 0" description="暂无比赛数据，请导入 CSV 文件">
      <el-button v-if="auth.isAdmin" type="primary" @click="onImport">导入 CSV</el-button>
    </el-empty>

    <!-- 标签页切换 -->
    <el-tabs v-else v-model="activeTab">
      <!-- 数据列表 -->
      <el-tab-pane label="数据列表" name="list">
        <el-table v-loading="loading" :data="filteredItems" max-height="500">
          <el-table-column prop="player_name" label="玩家" min-width="100" fixed />
          <el-table-column prop="profession" label="职业" width="80" />
          <el-table-column prop="camp" label="阵营" width="120" />
          <el-table-column prop="kills" label="击杀" width="80" align="right" sortable />
          <el-table-column prop="assists" label="助攻" width="80" align="right" sortable />
          <el-table-column prop="player_damage" label="伤害" width="100" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.player_damage) }}</template>
          </el-table-column>
          <el-table-column prop="healing" label="治疗" width="100" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.healing) }}</template>
          </el-table-column>
          <el-table-column prop="damage_taken" label="承伤" width="100" align="right" sortable>
            <template #default="{ row }">{{ formatNumber(row.damage_taken) }}</template>
          </el-table-column>
          <el-table-column prop="deaths" label="重伤" width="80" align="right" sortable />
          <el-table-column prop="fen_gu" label="焚骨" width="80" align="right" sortable />
        </el-table>
      </el-tab-pane>

      <!-- 排行榜 -->
      <el-tab-pane label="排行榜" name="ranking">
        <div class="ranking-grid">
          <div v-for="(ranking, key) in rankings" :key="key" class="ranking-card">
            <h4>{{ rankingTitles[key] }}</h4>
            <el-table :data="ranking" size="small" max-height="300">
              <el-table-column type="index" width="50" label="#" />
              <el-table-column prop="player_name" label="玩家" min-width="80" />
              <el-table-column prop="profession" label="职业" width="70" />
              <el-table-column prop="value" label="数值" width="80" align="right">
                <template #default="{ row }">{{ formatNumber(row.value) }}</template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </el-tab-pane>

      <!-- 职业统计 -->
      <el-tab-pane label="职业统计" name="profession">
        <el-table :data="professionStats" size="small">
          <el-table-column prop="profession" label="职业" width="100" />
          <el-table-column prop="count" label="人数" width="80" align="right" />
          <el-table-column prop="avg_kills" label="平均击杀" width="100" align="right" />
          <el-table-column prop="avg_damage" label="平均伤害" width="120" align="right">
            <template #default="{ row }">{{ formatNumber(row.avg_damage) }}</template>
          </el-table-column>
          <el-table-column prop="avg_healing" label="平均治疗" width="120" align="right">
            <template #default="{ row }">{{ formatNumber(row.avg_healing) }}</template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 隐藏的文件输入 -->
    <input ref="fileInput" type="file" accept=".csv" style="display: none" @change="onFileChange" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { getMatchData, getProfessionStats, getRankings, getReportUrl, importCsv } from '@/api/matchData'
import type { CampStats, MatchData, ProfessionStats, RankingsResponse } from '@/types/matchData'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const loading = ref(false)
const importing = ref(false)
const items = ref<MatchData[]>([])
const camps = ref<CampStats[]>([])
const selectedCamp = ref('')
const activeTab = ref('list')
const fileInput = ref<HTMLInputElement | null>(null)
const rankings = ref<RankingsResponse>({
  kills_ranking: [],
  damage_ranking: [],
  healing_ranking: [],
  fen_gu_ranking: [],
})
const professionStats = ref<ProfessionStats[]>([])

const rankingTitles: Record<string, string> = {
  kills_ranking: '击杀榜',
  damage_ranking: '伤害榜',
  healing_ranking: '治疗榜',
  fen_gu_ranking: '焚骨榜',
}

const filteredItems = computed(() => {
  if (!selectedCamp.value) return items.value
  return items.value.filter((r) => r.camp === selectedCamp.value)
})

onMounted(load)

watch(selectedCamp, () => {
  loadRankings()
  loadProfessionStats()
})

async function load() {
  loading.value = true
  try {
    const data = await getMatchData(props.scheduleId)
    items.value = data.items
    camps.value = data.camps
    await Promise.all([loadRankings(), loadProfessionStats()])
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

async function loadProfessionStats() {
  const data = await getProfessionStats(props.scheduleId, {
    camp: selectedCamp.value || undefined,
  })
  professionStats.value = data.items
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
  padding: 12px 16px;
  background: #fff8e7;
  border-radius: 8px;
  margin-bottom: 12px;
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.label {
  font-size: 12px;
  color: #6b7280;
}

.value {
  font-size: 18px;
  font-weight: 700;
  color: #b8960e;
}

.detail {
  font-size: 11px;
  color: #9ca3af;
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

.ranking-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.ranking-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
}

.ranking-card h4 {
  margin: 0 0 12px 0;
  color: #374151;
  font-size: 14px;
}
</style>

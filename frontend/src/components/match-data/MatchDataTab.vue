<!-- 行数豁免（连续逻辑）：分析页控制器（导入/切局/筛选/加载围绕同一数据流，子 Tab 已组件化）｜登记见 .agent/rules/file-length-rule.md 豁免清单 -->
<template>
  <div class="match-data-tab">
    <!-- 局切换：赛程有几局即可切换几局，已导入的局打勾标记 -->
    <div v-if="rounds > 1" class="round-bar">
      <span class="round-bar__label">当前局</span>
      <el-radio-group v-model="roundNo" size="small" @change="onRoundChange">
        <el-radio-button v-for="n in roundOptions" :key="n" :value="n">
          第{{ n }}局<template v-if="importedRounds.includes(n)"><i class="round-bar__check"> ✓</i></template>
        </el-radio-button>
      </el-radio-group>
      <span class="round-bar__hint">
        {{ importedRounds.includes(roundNo) ? '该局已导入，重新导入将覆盖数据' : '该局暂未导入数据' }}
      </span>
    </div>

    <!-- 阵营统计（切局/加载时遮罩，避免旧局数据闪现） -->
    <div v-if="camps.length > 0" v-loading="loading" class="stats-bar">
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
      <el-select aria-label="阵营筛选" v-model="selectedCamp" placeholder="阵营筛选" clearable style="width: 150px">
        <el-option v-for="camp in camps" :key="camp.camp" :label="camp.camp" :value="camp.camp" />
      </el-select>
      <el-input aria-label="按ID搜索" v-model="nameFilter" placeholder="按ID搜索" clearable style="width: 180px" :prefix-icon="Search" />
      <div class="spacer" />
      <!-- 生成战报：整场聚合（不随当前局），无任何已导入局时禁用 -->
      <el-tooltip
        v-if="auth.isAdmin"
        :content="importedRounds.length === 0 ? '请先导入比赛数据' : ''"
        :disabled="importedRounds.length > 0"
        placement="top"
      >
        <span>
          <el-button :icon="Trophy" :disabled="importedRounds.length === 0" @click="reportVisible = true">
            生成战报
          </el-button>
        </span>
      </el-tooltip>
      <el-button text type="primary" @click="guideRef?.open()">
        <el-icon><InfoFilled /></el-icon>
        指标说明
      </el-button>
    </div>

    <!-- 该局无任何数据（加载中保持空态并叠加遮罩，避免视图切换闪烁） -->
    <EmptyState
      v-if="items.length === 0"
      v-loading="loading"
      variant="chart"
      :description="`第 ${roundNo} 局暂无比赛数据，请导入 CSV 文件`"
    >
      <el-button v-if="auth.isAdmin" type="primary" @click="onImport">导入 CSV</el-button>
    </EmptyState>
    <!-- 有数据但被筛选过滤为空 -->
    <EmptyState v-else-if="filteredItems.length === 0" v-loading="loading" variant="search" description="无符合当前筛选条件的数据" />

    <!-- 标签页切换（切局/加载时整体遮罩）；lazy：子 Tab 首次激活时才挂载并发请求，
         不再进入页面即并发 8 个子 Tab 的加载请求与聚合计算 -->
    <el-tabs v-else v-loading="loading" v-model="activeTab">
      <!-- 数据总览 -->
      <el-tab-pane lazy label="数据总览" name="overview">
        <OverviewTab :items="filteredItems" :camps="camps" />
      </el-tab-pane>

      <!-- 数据列表（16 项衍生指标） -->
      <el-tab-pane lazy label="数据列表" name="list">
        <IndicatorsTab :schedule-id="scheduleId" :round-no="roundNo" />
      </el-tab-pane>

      <!-- 排行榜（折线图 + 四榜） -->
      <el-tab-pane lazy label="排行榜" name="ranking">
        <RankingTab :items="filteredItems" :rankings="rankings" />
      </el-tab-pane>

      <!-- 阵营对比 -->
      <el-tab-pane lazy label="阵营对比" name="camp-compare">
        <CampCompareTab :schedule-id="scheduleId" :round-no="roundNo" />
      </el-tab-pane>

      <!-- 小队分析 -->
      <el-tab-pane lazy label="小队分析" name="squad">
        <SquadAnalysisTab :schedule-id="scheduleId" :round-no="roundNo" />
      </el-tab-pane>

      <!-- 职业分析 -->
      <el-tab-pane lazy label="职业分析" name="profession">
        <ProfessionTab :items="filteredItems" />
      </el-tab-pane>

      <!-- 职业深度（17 项指标） -->
      <el-tab-pane lazy label="职业深度" name="profession-detail">
        <ProfessionDetailTab :schedule-id="scheduleId" :round-no="roundNo" />
      </el-tab-pane>

      <!-- 综合评分 -->
      <el-tab-pane lazy label="综合评分" name="score">
        <ScoreTab :items="filteredItems" />
      </el-tab-pane>
    </el-tabs>

    <!-- 指标说明弹窗 -->
    <MetricsGuideDialog ref="guideRef" />

    <!-- 单场图文战报弹窗 -->
    <MatchReportDialog v-model="reportVisible" :schedule-id="scheduleId" :schedule="schedule ?? null" />

    <!-- 隐藏的文件输入 -->
    <input ref="fileInput" type="file" accept=".csv" style="display: none" @change="onFileChange" />
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled, Search, Trophy } from '@element-plus/icons-vue'

import { getMatchData, getRankings, importCsv } from '@/api/matchData'
import type { CampStats, MatchData, RankingsResponse } from '@/types/matchData'
import type { ScheduleInfo } from '@/types/schedule'
import { useAuthStore } from '@/stores/auth'
import { CAMP_COLORS } from './analysis'
import OverviewTab from './OverviewTab.vue'
import RankingTab from './RankingTab.vue'
import ProfessionTab from './ProfessionTab.vue'
import ScoreTab from './ScoreTab.vue'
import IndicatorsTab from './IndicatorsTab.vue'
import CampCompareTab from './CampCompareTab.vue'
import SquadAnalysisTab from './SquadAnalysisTab.vue'
import ProfessionDetailTab from './ProfessionDetailTab.vue'
import MatchReportDialog from './MatchReportDialog.vue'
import MetricsGuideDialog from './MetricsGuideDialog.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{ scheduleId: number; schedule?: ScheduleInfo | null }>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const loading = ref(true) // 初始即加载态，避免空局先渲染空态再切遮罩的闪烁
const importing = ref(false)
const items = ref<MatchData[]>([])
const camps = ref<CampStats[]>([])
const rounds = ref(1) // 赛程总局数（1~3）
const importedRounds = ref<number[]>([]) // 已导入的局号列表
const roundNo = ref(1) // 当前展示/导入目标局
const selectedCamp = ref('')
const nameFilter = ref('')
/** 防抖后的搜索词：过滤与图表重算延迟 250ms，避免每敲一个字符触发全量重算 + ECharts 重绘 */
const appliedNameFilter = ref('')
let nameFilterTimer: ReturnType<typeof setTimeout> | null = null
watch(nameFilter, (v) => {
  if (nameFilterTimer) clearTimeout(nameFilterTimer)
  nameFilterTimer = setTimeout(() => {
    appliedNameFilter.value = v
  }, 250)
})
onBeforeUnmount(() => {
  if (nameFilterTimer) clearTimeout(nameFilterTimer)
})
// 注意：子 tab 用独立参数名 matchTab，避免覆盖外层 ScheduleDetailView 的 tab 参数（否则刷新后会掉回默认的出勤库）
const activeTab = ref(String(route.query.matchTab || 'overview'))
const fileInput = ref<HTMLInputElement | null>(null)
const guideRef = ref<InstanceType<typeof MetricsGuideDialog> | null>(null)
const reportVisible = ref(false) // 单场图文战报弹窗
const rankings = ref<RankingsResponse>({
  kills_ranking: [],
  damage_ranking: [],
  building_ranking: [],
  healing_ranking: [],
  taken_ranking: [],
  fen_gu_ranking: [],
})

const roundOptions = computed(() => Array.from({ length: rounds.value }, (_, i) => i + 1))

function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}

const filteredItems = computed(() => {
  let list = items.value
  if (selectedCamp.value) {
    list = list.filter((r) => r.camp === selectedCamp.value)
  }
  const kw = appliedNameFilter.value.trim()
  if (kw) {
    list = list.filter((r) => r.player_name.includes(kw))
  }
  return list
})

/** activeTab 变化时同步到 URL query（独立参数名 matchTab） */
watch(activeTab, (tab) => {
  router.replace({ query: { ...route.query, matchTab: tab } })
})

onMounted(load)

// 请求序号：切局/切筛选快速连续触发时，丢弃过期响应，避免旧数据覆盖新数据
let loadSeq = 0
let rankingSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  try {
    const data = await getMatchData(props.scheduleId, roundNo.value)
    if (seq !== loadSeq) return
    items.value = data.items
    camps.value = data.camps
    importedRounds.value = data.imported_rounds
    rounds.value = data.rounds
    if (roundNo.value > rounds.value) roundNo.value = rounds.value
    await loadRankings()
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

/** 切换局时重新加载当前局数据 */
function onRoundChange() {
  load()
}

async function loadRankings() {
  const seq = ++rankingSeq
  const data = await getRankings(props.scheduleId, {
    roundNo: roundNo.value,
    camp: selectedCamp.value || undefined,
    limit: 10,
  })
  if (seq !== rankingSeq) return
  rankings.value = data
}

/** 阵营筛选变化时重载排行榜 */
watch(selectedCamp, () => {
  if (items.value.length > 0) loadRankings()
})

function onImport() {
  fileInput.value?.click()
}

async function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 该局已有数据时确认覆盖（一局一表）
  if (importedRounds.value.includes(roundNo.value)) {
    try {
      await ElMessageBox.confirm(
        `第 ${roundNo.value} 局已导入过数据，重新导入将覆盖该局原有数据，是否继续？`,
        '覆盖确认',
        { type: 'warning' },
      )
    } catch {
      input.value = '' // 取消覆盖，重置 input
      return
    }
  }

  importing.value = true
  try {
    const result = await importCsv(props.scheduleId, file, roundNo.value)
    ElMessage.success(result.message)
    load()
  } finally {
    importing.value = false
    input.value = '' // 重置 input
  }
}

function formatNumber(value: number): string {
  if (value >= 10000) {
    return (value / 10000).toFixed(1) + '万'
  }
  return value.toLocaleString()
}
</script>

<style scoped>
/* finesse · register=product · shell=member-detail: analysis round-switcher touch */
.round-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px 12px;
  padding: 10px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  background: var(--ink-bg-wash);
}

.round-bar__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
}

.round-bar__check {
  font-style: normal;
  font-weight: 700;
  color: var(--gold-700);
}

.round-bar__hint {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-400);
}

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

  /* 导入 / 阵营筛选：两两均分一行（指标说明除外） */
  .toolbar .el-button:not(.is-text),
  .toolbar .el-select {
    flex: 1 1 calc(50% - 4px);
    width: auto !important;
    margin-left: 0 !important;
  }

  /* 按ID搜索占满剩余宽度，指标说明贴右 */
  .toolbar .el-input {
    flex: 1 1 auto;
    width: auto !important;
    min-width: 0;
  }

  .toolbar .spacer {
    display: none;
  }

  .toolbar .el-button.is-text {
    flex-shrink: 0;
    padding: 0 4px;
  }

  /* 局切换：紧凑高度 32px（与全站移动端按钮标准一致） */
  .round-bar :deep(.el-radio-button__inner) {
    display: flex;
    align-items: center;
    height: 32px;
    padding: 0 12px;
  }
}
</style>

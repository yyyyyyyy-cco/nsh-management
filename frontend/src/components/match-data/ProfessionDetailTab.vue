<template>
  <div class="profession-detail-tab">
    <el-empty v-if="!loading && profStats.length === 0" description="暂无比赛数据，请先导入 CSV" />
    <template v-else>
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-select v-model="campFilter" placeholder="阵营筛选" clearable style="width: 150px" @change="load">
          <el-option v-for="c in campOptions" :key="c" :label="c" :value="c" />
        </el-select>
        <span class="toolbar__count">{{ profStats.length }} 个职业 · 17 项指标</span>
      </div>

      <!-- 图表行 1：人数分布饼图 + 平均击杀 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">职业人数分布</div>
          <EChart :option="countPieOption" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">职业平均击杀（我方 / 敌方）</div>
          <EChart :option="metricBarOption('avg_kills')" :height="340" />
        </div>
      </div>

      <!-- 图表行 2：平均伤害 + 平均治疗 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">职业平均玩家伤害（我方 / 敌方）</div>
          <EChart :option="metricBarOption('avg_player_damage')" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">职业平均治疗</div>
          <EChart :option="metricBarOption('avg_healing', { filterProf: isHealer, fmt: fmtNum })" :height="340" />
        </div>
      </div>

      <!-- 图表行 3：平均承伤 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">职业平均承伤（承伤职业：铁衣 / 血河 / 沧澜 / 素问）</div>
          <EChart :option="metricBarOption('avg_damage_taken', { filterProf: isTank, fmt: fmtNum })" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">职业技能使用率（清泉羽化率 / 焚骨率）</div>
          <EChart :option="skillBarOption" :height="340" />
        </div>
      </div>

      <!-- 17 项指标明细表（拆分为子标签） -->
      <div class="chart-card">
        <el-tabs v-model="metricSubTab" class="metric-sub-tabs">
          <!-- 效率指标 -->
          <el-tab-pane label="效率指标" name="efficiency">
            <el-table :data="profStats" v-loading="loading" size="small" max-height="480" border>
              <el-table-column prop="profession" label="职业" min-width="80" fixed="left">
                <template #default="{ row }">
                  <span class="prof-cell">
                    <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
                    {{ row.profession }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="人数" min-width="60" align="right" sortable />
              <el-table-column prop="avg_kda" label="KDA" min-width="70" align="right" sortable>
                <template #default="{ row }">{{ row.avg_kda.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column prop="avg_dps" label="秒伤" min-width="75" align="right" sortable>
                <template #default="{ row }">{{ row.avg_dps.toFixed(0) }}</template>
              </el-table-column>
              <el-table-column prop="avg_kpa_damage" label="参与击杀均伤" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.avg_kpa_damage.toFixed(0) }}</template>
              </el-table-column>
              <el-table-column prop="avg_damage_per_death" label="每死输出值" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.avg_damage_per_death.toFixed(0) }}</template>
              </el-table-column>
              <el-table-column prop="avg_taken_per_death" label="每死承伤" min-width="90" align="right" sortable>
                <template #default="{ row }">{{ row.avg_taken_per_death.toFixed(0) }}</template>
              </el-table-column>
              <el-table-column prop="avg_healing_per_death" label="死亡治疗量" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.avg_healing_per_death.toFixed(0) }}</template>
              </el-table-column>
              <el-table-column prop="avg_heal_conversion" label="治疗转化率" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.avg_heal_conversion.toFixed(2) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 占比指标 -->
          <el-tab-pane label="占比指标" name="ratio">
            <el-table :data="profStats" v-loading="loading" size="small" max-height="480" border>
              <el-table-column prop="profession" label="职业" min-width="80" fixed="left">
                <template #default="{ row }">
                  <span class="prof-cell">
                    <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
                    {{ row.profession }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column prop="count" label="人数" min-width="60" align="right" sortable />
              <el-table-column prop="avg_kill_ratio" label="击杀占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_kill_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_assist_ratio" label="助攻占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_assist_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_player_damage_ratio" label="人伤占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_player_damage_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_building_ratio" label="拆塔占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_building_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_taken_ratio" label="承伤占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_taken_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_death_ratio" label="死亡占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_death_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_heal_ratio" label="治疗占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.avg_heal_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="avg_revive_rate" label="清泉羽化率" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.avg_revive_rate.toFixed(2) }}<em class="unit">次/分</em></template>
              </el-table-column>
              <el-table-column prop="avg_fen_gu_rate" label="焚骨率" min-width="90" align="right" sortable>
                <template #default="{ row }">{{ row.avg_fen_gu_rate.toFixed(2) }}<em class="unit">次/分</em></template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
      </div>

      <!-- 职业差值/波动值表 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <span class="chart-card__title">职业差值 / 波动值（基于分阵营均值）</span>
          <el-select v-model="profFilter" placeholder="按职业筛选" clearable size="small" style="width: 160px">
            <el-option v-for="p in allProfs" :key="p" :label="p" :value="p" />
          </el-select>
        </div>
        <el-table :data="comparisonRows" size="small" max-height="360">
          <el-table-column prop="profession" label="职业" min-width="80" />
          <el-table-column prop="label" label="指标" min-width="90" />
          <el-table-column prop="value1" label="我方" min-width="90" align="right">
            <template #default="{ row }">{{ fmtCmpValue(row, row.value1) }}</template>
          </el-table-column>
          <el-table-column prop="value2" label="敌方" min-width="90" align="right">
            <template #default="{ row }">{{ fmtCmpValue(row, row.value2) }}</template>
          </el-table-column>
          <el-table-column label="差值" min-width="90" align="right">
            <template #default="{ row }">
              <span :class="row.diff >= 0 ? 'diff-pos' : 'diff-neg'">{{ row.diff >= 0 ? '+' : '' }}{{ fmtCmpValue(row, row.diff) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="波动值" min-width="150">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.min(Math.abs(row.wave), 100)"
                :stroke-width="12"
                :format="() => `${row.wave.toFixed(2)}%`"
                :status="row.wave > 20 ? 'exception' : row.wave > 5 ? 'warning' : 'success'"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getProfessionStats } from '@/api/matchData'
import type { ProfessionStats } from '@/types/matchData'
import { CAMP_COLORS, fmtNum, profColor, PROF_COLORS } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const profStats = ref<ProfessionStats[]>([])
const campFilter = ref('')
const profFilter = ref('')
const metricSubTab = ref((route.query.metricSub as string) || 'efficiency')
const campOptions = ref<string[]>([])
const allProfs = computed(() => profStats.value.map((p) => p.profession))

watch(metricSubTab, (v) => { router.replace({ query: { ...route.query, metricSub: v } }) })

async function load() {
  loading.value = true
  try {
    const data = await getProfessionStats(props.scheduleId, {
      roundNo: props.roundNo,
      camp: campFilter.value || undefined,
    })
    profStats.value = data.items
    // 首次加载时记录所有阵营选项（后续筛选不再更新，保证可切换回全部）
    if (campOptions.value.length === 0) {
      campOptions.value = [...new Set(data.items.flatMap((p) => p.camps.map((c) => c.camp)))]
    }
  } finally {
    loading.value = false
  }
}

watch(() => props.roundNo, () => { campOptions.value = []; campFilter.value = ''; load() }, { immediate: true })

const HEALERS = new Set(['素问', '鸿音', '潮光'])
const TANKS = new Set(['铁衣', '血河', '沧澜', '素问'])

/** 治疗职业判定：职业名在候选列表中，且该职业整体治疗量 > 伤害量。 */
function isHealer(p: ProfessionStats) {
  return HEALERS.has(p.profession) && p.avg_healing > p.avg_damage
}

function isTank(p: ProfessionStats) {
  return TANKS.has(p.profession) && p.camps.some((c) => c.avg_damage_taken > 0)
}

function hex(c: string): string {
  return c.length > 7 ? c.slice(0, 7) : c
}

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}

const countPieOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'item', ...CHART_THEME.tooltip, formatter: '{b}: {c}人 ({d}%)' },
  legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
  series: [
    {
      type: 'pie',
      radius: ['45%', '72%'],
      center: ['40%', '50%'],
      data: profStats.value.map((p) => ({
        name: p.profession,
        value: p.count,
        itemStyle: { color: hex(PROF_COLORS[p.profession] || '#999'), borderColor: '#fff', borderWidth: 2 },
      })),
      label: { show: false },
      emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
    },
  ],
}))

type MetricKey = 'avg_kills' | 'avg_player_damage' | 'avg_healing' | 'avg_damage_taken'

function metricBarOption(
  metric: MetricKey,
  opts?: { filterProf?: (p: ProfessionStats) => boolean; fmt?: (v: number) => string },
) {
  const list = profStats.value.filter((p) => !opts?.filterProf || opts.filterProf(p))
  const campNames = [...new Set(list.flatMap((p) => p.camps.map((c) => c.camp)))]
  const fmt = opts?.fmt ?? ((v: number) => v.toFixed(1))
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      valueFormatter: (v: number) => fmt(v),
    },
    legend: { top: 0, data: campNames, ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((p) => p.profession),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: campNames.map((camp, i) => ({
      name: camp,
      type: 'bar',
      barWidth: 16,
      barGap: '40%',
      itemStyle: { color: campColor(i), borderRadius: [3, 3, 0, 0] },
      data: list.map((p) => p.camps.find((c) => c.camp === camp)?.[metric] ?? 0),
    })),
  }
}

const skillBarOption = computed(() => {
  const list = profStats.value.filter((p) => p.camps.some((c) => c.count > 0))
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      valueFormatter: (v: number) => v.toFixed(2) + ' 次/分钟',
    },
    legend: { bottom: 0, data: ['清泉羽化率', '焚骨率'], ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((p) => p.profession),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
    },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => v.toFixed(1) }, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '清泉羽化率', type: 'bar', barWidth: 14, itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] }, data: list.map((p) => p.avg_revive_rate) },
      { name: '焚骨率', type: 'bar', barWidth: 14, itemStyle: { color: '#5b7a9d', borderRadius: [3, 3, 0, 0] }, data: list.map((p) => p.avg_fen_gu_rate) },
    ],
  }
})

const METRIC_LABELS: Record<string, string> = {
  avg_kills: '平均击杀',
  avg_player_damage: '平均伤害',
  avg_building_damage: '平均塔伤',
  avg_healing: '平均治疗',
  avg_damage_taken: '平均承伤',
  avg_kda: '平均KDA',
}

const comparisonRows = computed(() => {
  const rows: { profession: string; label: string; value1: number; value2: number; diff: number; wave: number; metric: string }[] = []
  const list = profFilter.value
    ? profStats.value.filter((p) => p.profession === profFilter.value)
    : profStats.value
  for (const p of list) {
    for (const cmp of p.comparison) {
      rows.push({
        profession: p.profession,
        label: METRIC_LABELS[cmp.metric] ?? cmp.metric,
        value1: cmp.value1,
        value2: cmp.value2,
        diff: cmp.diff,
        wave: cmp.wave,
        metric: cmp.metric,
      })
    }
  }
  return rows
})

function fmtCmpValue(row: { metric: string }, v: number): string {
  if (row.metric === 'avg_kda') return v.toFixed(2)
  if (row.metric === 'avg_kills') return v.toFixed(1)
  if (
    row.metric === 'avg_player_damage' ||
    row.metric === 'avg_building_damage' ||
    row.metric === 'avg_healing' ||
    row.metric === 'avg_damage_taken'
  ) {
    return fmtNum(v)
  }
  return String(v)
}
</script>

<style scoped>
.profession-detail-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar__count {
  font-size: 13px;
  color: var(--ink-500);
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
  margin-bottom: 10px;
}

.chart-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-card__head .chart-card__title {
  margin-bottom: 0;
}

.prof-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.unit {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 2px;
}

.diff-pos {
  color: var(--gold-700);
  font-weight: 700;
}

.diff-neg {
  color: #c0392b;
  font-weight: 700;
}

/* 子标签页样式 */
.metric-sub-tabs :deep(.el-tabs__header) {
  margin-bottom: 10px;
}

.metric-sub-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.metric-sub-tabs :deep(.el-tabs__content) {
  padding: 0;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

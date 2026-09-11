<template>
  <div class="camp-compare-tab">
    <el-empty v-if="!loading && campNames.length === 0" description="暂无比赛数据，请先导入 CSV" />
    <template v-else>
      <el-alert
        v-if="campNames.length === 1"
        title="当前数据仅有一个阵营，无法进行双方对比"
        type="info"
        :closable="false"
        show-icon
        class="mb"
      />

      <!-- 图表行：核心数据对比 + 伤害对比 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">阵营核心数据对比</div>
          <EChart :option="coreBarOption" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">阵营伤害分布对比（万）</div>
          <EChart :option="damageBarOption" :height="340" />
        </div>
      </div>

      <!-- 差值/波动值进度条 -->
      <div class="chart-card">
        <div class="chart-card__title">指标差值 / 波动值</div>
        <el-table :data="compareRows" size="small" max-height="420">
          <el-table-column prop="label" label="指标" min-width="90" />
          <el-table-column
            v-for="name in campNames"
            :key="name"
            :label="`${name}（${campCountText(name)}）`"
            min-width="110"
            align="right"
          >
            <template #default="{ row }">{{ fmtValue(row[name], name) }}</template>
          </el-table-column>
          <el-table-column label="差值" min-width="90" align="right">
            <template #default="{ row }">
              <span :class="row['差值'] >= 0 ? 'diff-pos' : 'diff-neg'">
                {{ row['差值'] >= 0 ? '+' : '' }}{{ fmtValue(row['差值'], row.label) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="波动值" min-width="150">
            <template #default="{ row }">
              <el-progress
                :percentage="Math.min(Math.abs(row['波动值']), 100)"
                :stroke-width="12"
                :format="() => `${row['波动值'].toFixed(2)}%`"
                :status="row['波动值'] > 20 ? 'exception' : row['波动值'] > 5 ? 'warning' : 'success'"
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

import { getCampCompare } from '@/api/matchData'
import type { CampCompareResponse } from '@/types/matchData'
import { CAMP_COLORS, fmtNum } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const loading = ref(false)
const data = ref<CampCompareResponse | null>(null)

const campNames = computed(() => (data.value ? Object.keys(data.value.camps) : []))

const compareRows = computed(() =>
  data.value ? Object.entries(data.value.comparison).map(([label, row]) => ({ label, ...row })) : [],
)

const DAMAGE_LABELS = new Set(['玩家伤害', '建筑伤害', '治疗', '承伤'])

function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}

function campCountText(name: string) {
  const c = data.value?.camps[name]
  return c ? `${c.player_count} 人` : ''
}

/** 伤害类指标显示为“万”，其余显示为整数。 */
function fmtValue(v: number, label: string): string {
  if (DAMAGE_LABELS.has(label)) return fmtNum(v)
  return (v ?? 0).toLocaleString()
}

// 请求序号：快速切局时丢弃过期响应，避免旧局数据覆盖新局
let loadSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  try {
    const resp = await getCampCompare(props.scheduleId, props.roundNo)
    if (seq !== loadSeq) return
    data.value = resp
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

watch(() => props.roundNo, load, { immediate: true })

const coreBarOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
  legend: { top: 0, data: campNames.value, ...CHART_THEME.legend },
  grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
  xAxis: {
    type: 'category',
    data: ['击杀', '助攻', '死亡', '破泉', '化羽', '焚骨'],
    axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
  },
  yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
  series: campNames.value.map((name, i) => {
    const c = data.value!.camps[name]
    return {
      name,
      type: 'bar',
      barWidth: 18,
      barGap: '40%',
      itemStyle: { color: campColor(i), borderRadius: [4, 4, 0, 0] },
      data: [c.kills, c.assists, c.deaths, c.springs, c.revives, c.fen_gu],
    }
  }),
}))

const damageBarOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    trigger: 'axis',
    ...CHART_THEME.tooltip,
    valueFormatter: (v: number) => fmtNum(v * 10000),
  },
  legend: { top: 0, data: campNames.value, ...CHART_THEME.legend },
  grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
  xAxis: {
    type: 'category',
    data: ['玩家伤害', '建筑伤害', '治疗', '承伤'],
    axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 },
  },
  yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
  series: campNames.value.map((name, i) => {
    const c = data.value!.camps[name]
    return {
      name,
      type: 'bar',
      barWidth: 26,
      barGap: '40%',
      itemStyle: { color: campColor(i), borderRadius: [4, 4, 0, 0] },
      data: [
        +(c.player_damage / 10000).toFixed(0),
        +(c.building_damage / 10000).toFixed(0),
        +(c.healing / 10000).toFixed(0),
        +(c.damage_taken / 10000).toFixed(0),
      ],
    }
  }),
}))
</script>

<style scoped>
.camp-compare-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mb {
  margin-bottom: 4px;
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

.diff-pos {
  color: var(--gold-700);
  font-weight: 700;
}

.diff-neg {
  color: #c0392b;
  font-weight: 700;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

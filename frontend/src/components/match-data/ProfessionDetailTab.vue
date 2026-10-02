<template>
  <div class="profession-detail-tab">
    <EmptyState v-if="!loading && profStats.length === 0" variant="chart" description="暂无比赛数据，请先导入 CSV" />
    <template v-else>
      <!-- 工具栏 -->
      <div class="toolbar">
        <el-select aria-label="阵营筛选" v-model="campFilter" placeholder="阵营筛选" clearable style="width: 150px" @change="load">
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
          <div class="chart-card__title">职业平均承伤（承伤职业：{{ TANK_LABEL }}）</div>
          <EChart :option="metricBarOption('avg_damage_taken', { filterProf: isTank, fmt: fmtNum })" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">职业技能使用率（清泉羽化率 / 焚骨率）</div>
          <EChart :option="skillBarOption" :height="340" />
        </div>
      </div>

      <!-- 17 项指标明细表（拆分为子标签，子标签状态由子组件持久化到 URL） -->
      <ProfessionMetricTables :prof-stats="profStats" :loading="loading" />

      <!-- 职业差值/波动值表 -->
      <ProfessionCompareTable :prof-stats="profStats" />
    </template>
  </div>
</template>

<script setup lang="ts">
const TANK_LABEL = [...TANK_PROFESSIONS].join(' / ')
import { computed, ref, watch } from 'vue'

import { getProfessionStats } from '@/api/matchData'
import type { ProfessionStats } from '@/types/matchData'
import { fmtNum } from './analysis'
import EChart from './EChart.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import ProfessionCompareTable from './ProfessionCompareTable.vue'
import ProfessionMetricTables from './ProfessionMetricTables.vue'
import { TANK_PROFESSIONS, buildCountPieOption, buildMetricBarOption, buildSkillBarOption, isHealer, isTank } from './professionDetailCharts'
import type { MetricKey } from './professionDetailCharts'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const loading = ref(false)
const profStats = ref<ProfessionStats[]>([])
const campFilter = ref('')
const campOptions = ref<string[]>([])

// 请求序号：快速切局/切阵营时丢弃过期响应，避免旧数据覆盖新数据
let loadSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  try {
    const data = await getProfessionStats(props.scheduleId, {
      roundNo: props.roundNo,
      camp: campFilter.value || undefined,
    })
    if (seq !== loadSeq) return
    profStats.value = data.items
    // 首次加载时记录所有阵营选项（后续筛选不再更新，保证可切换回全部）
    if (campOptions.value.length === 0) {
      campOptions.value = [...new Set(data.items.flatMap((p) => p.camps.map((c) => c.camp)))]
    }
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

watch(() => props.roundNo, () => { campOptions.value = []; campFilter.value = ''; load() }, { immediate: true })

// 图表 option（构建逻辑见 professionDetailCharts）
const countPieOption = computed(() => buildCountPieOption(profStats.value))

function metricBarOption(
  metric: MetricKey,
  opts?: { filterProf?: (p: ProfessionStats) => boolean; fmt?: (v: number) => string },
) {
  return buildMetricBarOption(profStats.value, metric, opts)
}

const skillBarOption = computed(() => buildSkillBarOption(profStats.value))
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

@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

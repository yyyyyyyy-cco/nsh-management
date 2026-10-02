<template>
  <el-dialog
    v-model="visible"
    :title="'小队对比（' + names.join(' vs ') + '）'"
    width="80%"
    top="4vh"
    destroy-on-close
    class="compare-dialog"
  >
    <div class="chart-row">
      <div>
        <div class="chart-card__title">汇总对比</div>
        <EChart :option="compareSummaryBar" :height="300" />
      </div>
      <div>
        <div class="chart-card__title">均值指标雷达图</div>
        <EChart :option="compareRadar" :height="300" />
      </div>
    </div>

    <!-- 差值表（恰好选 2 队时） -->
    <div v-if="names.length === 2" class="diff-table-wrap">
      <div class="chart-card__title">差值 / 波动值</div>
      <el-table :data="compareDiffRows" size="small" border max-height="260">
        <el-table-column prop="label" label="指标" min-width="110" />
        <el-table-column :label="names[0]" min-width="90" align="right">
          <template #default="{ row }">{{ row.v1 }}</template>
        </el-table-column>
        <el-table-column :label="names[1]" min-width="90" align="right">
          <template #default="{ row }">{{ row.v2 }}</template>
        </el-table-column>
        <el-table-column label="差值" min-width="90" align="right">
          <template #default="{ row }">
            <span :class="row.diff >= 0 ? 'diff-pos' : 'diff-neg'">{{ row.diff >= 0 ? '+' : '' }}{{ row.diffStr }}</span>
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
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { SquadAnalysis } from '@/types/matchData'

import EChart from './EChart.vue'
import { buildCompareDiffRows, compareRadarOption, compareSummaryBarOption } from './squadCompareCharts'

const props = defineProps<{ squads: SquadAnalysis[]; names: string[] }>()

const visible = defineModel<boolean>({ required: true })

const compareSummaryBar = computed(() => compareSummaryBarOption(props.squads))
const compareRadar = computed(() => compareRadarOption(props.squads))

const compareDiffRows = computed(() => {
  if (props.squads.length !== 2) return []
  const [a, b] = props.squads
  return buildCompareDiffRows(a, b)
})
</script>

<style scoped>
.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
}

/* ===== 对比差值 ===== */
.diff-table-wrap {
  margin-top: 12px;
}

.diff-table-wrap .chart-card__title {
  margin-bottom: 8px;
}

.diff-pos {
  color: var(--gold-700);
  font-weight: 700;
}

.diff-neg {
  color: #c0392b;
  font-weight: 700;
}

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }

  /* 弹窗宽度覆盖已迁移至 element-plus.css 全局 media query */
}
</style>

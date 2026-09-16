<template>
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

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { ProfessionStats } from '@/types/matchData'

import { buildComparisonRows, fmtCmpValue } from './professionDetailCharts'

const props = defineProps<{ profStats: ProfessionStats[] }>()

const profFilter = ref('')
const allProfs = computed(() => props.profStats.map((p) => p.profession))
const comparisonRows = computed(() => buildComparisonRows(props.profStats, profFilter.value))
</script>

<style scoped>
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

.diff-pos {
  color: var(--gold-700);
  font-weight: 700;
}

.diff-neg {
  color: #c0392b;
  font-weight: 700;
}

@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }
}
</style>

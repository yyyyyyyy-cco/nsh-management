<template>
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
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import type { ProfessionStats } from '@/types/matchData'

import { profColor } from './analysis'
import { pct } from './professionDetailCharts'

defineProps<{ profStats: ProfessionStats[]; loading: boolean }>()

const route = useRoute()
const router = useRouter()

// 子标签状态经 URL query 持久化（刷新后保持）
const metricSubTab = ref((route.query.metricSub as string) || 'efficiency')

watch(metricSubTab, (v) => { router.replace({ query: { ...route.query, metricSub: v } }) })
</script>

<style scoped>
.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
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
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }
}
</style>

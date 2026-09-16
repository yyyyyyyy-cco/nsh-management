<template>
  <el-tabs v-model="activeTab" class="detail-sub-tabs detail-tabs-wrap" style="margin-top: 6px">
    <el-tab-pane label="基础数据" name="basic">
      <el-table :data="members" size="small" border max-height="300">
        <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
        <el-table-column prop="profession" label="职业" min-width="70" />
        <el-table-column prop="kills" label="击杀" min-width="55" align="right" sortable />
        <el-table-column prop="assists" label="助攻" min-width="55" align="right" sortable />
        <el-table-column prop="deaths" label="重伤" min-width="55" align="right" sortable />
        <el-table-column prop="kda" label="KDA" min-width="65" align="right" sortable>
          <template #default="{ row }">{{ row.kda.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="player_damage" label="玩家伤害" min-width="90" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.player_damage) }}</template>
        </el-table-column>
        <el-table-column prop="building_damage" label="建筑伤害" min-width="90" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.building_damage) }}</template>
        </el-table-column>
        <el-table-column prop="healing" label="治疗" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.healing) }}</template>
        </el-table-column>
        <el-table-column prop="damage_taken" label="承伤" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ fmtNum(row.damage_taken) }}</template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <el-tab-pane label="效率指标" name="efficiency">
      <el-table :data="members" size="small" border max-height="300">
        <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
        <el-table-column prop="profession" label="职业" min-width="70" />
        <el-table-column prop="dps" label="秒伤" min-width="70" align="right" sortable />
        <el-table-column prop="kpa_damage" label="参与击杀均伤" min-width="100" align="right" sortable />
        <el-table-column prop="damage_per_death" label="每死输出值" min-width="100" align="right" sortable />
        <el-table-column prop="taken_per_death" label="每死承伤" min-width="90" align="right" sortable />
        <el-table-column prop="healing_per_death" label="每死治疗量" min-width="100" align="right" sortable />
        <el-table-column prop="heal_conversion" label="治疗转化率" min-width="100" align="right" sortable>
          <template #default="{ row }">{{ row.heal_conversion.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column prop="revive_rate" label="清泉羽化率" min-width="100" align="right" sortable>
          <template #default="{ row }">{{ row.revive_rate.toFixed(2) }}<em class="unit">次/分</em></template>
        </el-table-column>
        <el-table-column prop="fen_gu_rate" label="焚骨率" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ row.fen_gu_rate.toFixed(2) }}<em class="unit">次/分</em></template>
        </el-table-column>
      </el-table>
    </el-tab-pane>

    <el-tab-pane label="占比指标" name="ratio">
      <el-table :data="members" size="small" border max-height="300">
        <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
        <el-table-column prop="profession" label="职业" min-width="70" />
        <el-table-column prop="kill_ratio" label="击杀占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.kill_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="assist_ratio" label="助攻占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.assist_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="player_damage_ratio" label="人伤占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.player_damage_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="building_ratio" label="拆塔占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.building_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="taken_ratio" label="承伤占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.taken_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="death_ratio" label="死亡占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.death_ratio) }}</template>
        </el-table-column>
        <el-table-column prop="heal_ratio" label="治疗占比" min-width="80" align="right" sortable>
          <template #default="{ row }">{{ pct(row.heal_ratio) }}</template>
        </el-table-column>
      </el-table>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import type { SquadMember } from '@/types/matchData'

import { fmtNum } from './analysis'

defineProps<{ members: SquadMember[] }>()

const activeTab = ref('basic')

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}
</script>

<style scoped>
/* 成员表区：固定高度（表格内部滚动） */
.detail-tabs-wrap {
  flex-shrink: 0;
}

.detail-sub-tabs :deep(.el-tabs__header) {
  margin-bottom: 10px;
}

.detail-sub-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 600;
}

.detail-sub-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.unit {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 2px;
}
</style>

<template>
  <el-card shadow="never" class="table-card">
    <template #header>
      <div class="table-header">
        <span class="table-title">各场明细</span>
        <span class="table-sub">共 {{ records.length }} 局（最近 10 场）</span>
      </div>
    </template>
    <el-tabs v-model="activeTab" class="detail-tabs">
      <!-- 基础数据 -->
      <el-tab-pane label="基础数据" name="basic">
        <el-table :data="records" size="small" stripe :default-sort="{ prop: 'match_time', order: 'descending' }">
          <el-table-column label="赛程" min-width="130">
            <template #default="{ row }">
              <span class="opponent-cell">
                <el-tag :type="resultType(row.schedule_result)" size="small" effect="light">{{ resultLabel(row.schedule_result) }}</el-tag>
                vs {{ row.opponent }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="局" width="45" align="center">
            <template #default="{ row }">{{ row.round_no }}</template>
          </el-table-column>
          <el-table-column label="时间" min-width="90" sortable sort-by="match_time">
            <template #default="{ row }"><span class="time-cell num">{{ formatDate(row.match_time) }}</span></template>
          </el-table-column>
          <el-table-column label="职业" min-width="75">
            <template #default="{ row }">
              <span class="prof-cell">
                <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
                {{ row.profession || '-' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="KDA" min-width="65" align="right" sortable sort-by="kda">
            <template #default="{ row }">
              <span class="num" :class="{ highlight: row.kda >= 5 }">{{ row.kda.toFixed(1) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="击/助/死" min-width="95" align="center">
            <template #default="{ row }">
              <span class="kda-split">
                <em class="num kda-k">{{ row.kills }}</em>
                <span class="kda-sep">/</span>
                <em class="num kda-a">{{ row.assists }}</em>
                <span class="kda-sep">/</span>
                <em class="num kda-d">{{ row.deaths }}</em>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="秒伤" min-width="65" align="right" sortable sort-by="dps">
            <template #default="{ row }"><span class="num">{{ row.dps }}</span></template>
          </el-table-column>
          <el-table-column label="每死输出" min-width="85" align="right" sortable sort-by="damage_per_death">
            <template #default="{ row }"><span class="num">{{ fmtNum(row.damage_per_death) }}</span></template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 战斗数据 -->
      <el-tab-pane label="战斗数据" name="combat">
        <el-table :data="records" size="small" stripe :default-sort="{ prop: 'match_time', order: 'descending' }">
          <el-table-column label="赛程" min-width="130">
            <template #default="{ row }">
              <span class="opponent-cell">
                <el-tag :type="resultType(row.schedule_result)" size="small" effect="light">{{ resultLabel(row.schedule_result) }}</el-tag>
                vs {{ row.opponent }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="局" width="45" align="center">
            <template #default="{ row }">{{ row.round_no }}</template>
          </el-table-column>
          <el-table-column label="对玩家伤害" min-width="100" align="right" sortable sort-by="player_damage">
            <template #default="{ row }"><span class="num">{{ fmtNum(row.player_damage) }}</span></template>
          </el-table-column>
          <el-table-column label="对建筑伤害" min-width="100" align="right" sortable sort-by="building_damage">
            <template #default="{ row }"><span class="num">{{ fmtNum(row.building_damage) }}</span></template>
          </el-table-column>
          <el-table-column label="治疗" min-width="90" align="right" sortable sort-by="healing">
            <template #default="{ row }"><span class="num">{{ fmtNum(row.healing) }}</span></template>
          </el-table-column>
          <el-table-column label="承伤" min-width="90" align="right" sortable sort-by="damage_taken">
            <template #default="{ row }"><span class="num">{{ fmtNum(row.damage_taken) }}</span></template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <!-- 占比与排名 -->
      <el-tab-pane label="占比与排名" name="ratio">
        <el-table :data="records" size="small" stripe :default-sort="{ prop: 'match_time', order: 'descending' }">
          <el-table-column label="赛程" min-width="130">
            <template #default="{ row }">
              <span class="opponent-cell">
                <el-tag :type="resultType(row.schedule_result)" size="small" effect="light">{{ resultLabel(row.schedule_result) }}</el-tag>
                vs {{ row.opponent }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="局" width="45" align="center">
            <template #default="{ row }">{{ row.round_no }}</template>
          </el-table-column>
          <el-table-column label="击杀占比" min-width="80" align="right" sortable sort-by="kill_ratio">
            <template #default="{ row }"><span class="num">{{ pctStr(row.kill_ratio) }}</span></template>
          </el-table-column>
          <el-table-column label="对玩家伤害占比" min-width="110" align="right" sortable sort-by="player_damage_ratio">
            <template #default="{ row }"><span class="num">{{ pctStr(row.player_damage_ratio) }}</span></template>
          </el-table-column>
          <el-table-column label="对建筑伤害占比" min-width="110" align="right" sortable sort-by="building_ratio">
            <template #default="{ row }"><span class="num">{{ pctStr(row.building_ratio) }}</span></template>
          </el-table-column>
          <el-table-column label="击杀排名" min-width="90" align="center">
            <template #default="{ row }">
              <span v-if="row.rankings?.length" class="rank-cell">
                <span class="rank-best" :class="rankClass(row.rankings[0])">
                  #{{ row.rankings[0].rank }}<span class="rank-total">/{{ row.rankings[0].total }}</span>
                </span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="对玩家伤害排名" min-width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.rankings?.length" class="rank-cell">
                <span class="rank-best" :class="rankClass(row.rankings[1])">
                  #{{ row.rankings[1]?.rank }}<span class="rank-total">/{{ row.rankings[1]?.total }}</span>
                </span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="对建筑伤害排名" min-width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.rankings?.length" class="rank-cell">
                <span class="rank-best" :class="rankClass(row.rankings[2])">
                  #{{ row.rankings[2]?.rank }}<span class="rank-total">/{{ row.rankings[2]?.total }}</span>
                </span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="治疗排名" min-width="90" align="center">
            <template #default="{ row }">
              <span v-if="row.rankings?.length" class="rank-cell">
                <span class="rank-best" :class="rankClass(row.rankings[3])">
                  #{{ row.rankings[3]?.rank }}<span class="rank-total">/{{ row.rankings[3]?.total }}</span>
                </span>
              </span>
            </template>
          </el-table-column>
          <el-table-column label="承伤排名" min-width="90" align="center">
            <template #default="{ row }">
              <span v-if="row.rankings?.length" class="rank-cell">
                <span class="rank-best" :class="rankClass(row.rankings[4])">
                  #{{ row.rankings[4]?.rank }}<span class="rank-total">/{{ row.rankings[4]?.total }}</span>
                </span>
              </span>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'

import type { PlayerRecord, RankingItem } from '@/types/myStats'
import { profColor, fmtNum } from '@/components/match-data/analysis'
import { SCHEDULE_RESULTS } from '@/utils/constants'

defineProps<{ records: PlayerRecord[] }>()

const activeTab = ref('basic')

const resultLabel = (value: string) => SCHEDULE_RESULTS.find((r) => r.value === value)?.label || value
const resultType = (value: string) =>
  value === 'win' ? 'success' : value === 'lose' ? 'danger' : value === 'draw' ? 'primary' : 'info'
const formatDate = (value: string) => value.slice(0, 10)
const pctStr = (v: number) => (v * 100).toFixed(1) + '%'

function rankClass(r: RankingItem): string {
  if (!r) return ''
  const pct = r.rank / r.total
  if (pct <= 0.1) return 'rank--top'
  if (pct <= 0.3) return 'rank--good'
  return ''
}
</script>

<style scoped>
.table-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.table-title {
  font-family: var(--font-serif);
  font-weight: 700;
  letter-spacing: 1px;
}

.table-sub {
  font-size: 12px;
  color: var(--ink-400);
}

.detail-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  letter-spacing: 0.5px;
}

.detail-tabs :deep(.el-tabs__active-bar) {
  background: var(--gold-gradient);
}

.opponent-cell {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: var(--ink-900);
}

.time-cell {
  font-size: 12px;
  color: var(--ink-500);
}

.prof-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.highlight {
  color: var(--gold-700);
  font-weight: 700;
}

.kda-split {
  display: inline-flex;
  align-items: center;
  gap: 1px;
  font-size: 12px;
}

.kda-k { color: var(--cinnabar); font-weight: 600; }
.kda-a { color: var(--ink-600); }
.kda-d { color: var(--ink-400); }
.kda-sep { color: var(--ink-300); margin: 0 1px; }

.rank-cell {
  font-size: 12px;
}

.rank-best {
  font-weight: 600;
  color: var(--ink-600);
}

.rank-best.rank--top {
  color: var(--gold-700);
  font-weight: 700;
}

.rank-best.rank--good {
  color: var(--gold-600);
}

.rank-total {
  font-size: 10px;
  color: var(--ink-400);
  font-weight: 400;
}
</style>

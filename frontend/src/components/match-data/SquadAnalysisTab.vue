<template>
  <div class="squad-analysis-tab">
    <el-empty v-if="!loading && squads.length === 0" description="暂无数据或未关联排表（需先导入 CSV 与排表）" />
    <template v-else>
      <!-- 图表行 1：击杀 + 伤害 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">小队击杀对比</div>
          <EChart :option="killsBarOption" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__title">小队伤害对比（万）</div>
          <EChart :option="damageBarOption" :height="340" />
        </div>
      </div>

      <!-- 图表行 2：塔伤 + 职业分布 -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-card__title">小队塔伤贡献（万）</div>
          <EChart :option="towerBarOption" :height="340" />
        </div>
        <div class="chart-card">
          <div class="chart-card__head">
            <span class="chart-card__title">小队职业分布</span>
            <el-select v-model="selectedSquad" size="small" style="width: 180px">
              <el-option v-for="s in squads" :key="s.squad_name" :label="s.squad_name" :value="s.squad_name" />
            </el-select>
          </div>
          <EChart :option="profPieOption" :height="300" />
        </div>
      </div>

      <!-- 小队明细表（展开行查看成员） -->
      <div class="chart-card">
        <div class="chart-card__title">小队明细（点击行展开成员）</div>
        <el-table :data="squads" size="small" max-height="420" row-key="squad_name">
          <el-table-column type="expand">
            <template #default="{ row }">
              <div class="squad-members">
                <div class="squad-members__title">{{ row.squad_name }} · 成员明细（{{ row.members.length }} 人）</div>
                <el-table :data="row.members" size="small" border max-height="360">
                  <el-table-column prop="player_name" label="ID" min-width="110" />
                  <el-table-column prop="profession" label="职业" min-width="70" />
                  <el-table-column prop="camp" label="阵营" min-width="70" />
                  <el-table-column prop="kills" label="击杀" min-width="60" align="right" sortable />
                  <el-table-column prop="assists" label="助攻" min-width="60" align="right" sortable />
                  <el-table-column prop="deaths" label="重伤" min-width="60" align="right" sortable />
                  <el-table-column prop="kda" label="KDA" min-width="70" align="right" sortable>
                    <template #default="{ row: m }">{{ m.kda.toFixed(2) }}</template>
                  </el-table-column>
                  <el-table-column prop="dps" label="秒伤" min-width="70" align="right" sortable />
                  <el-table-column prop="kpa_damage" label="参与击杀均伤" min-width="95" align="right" sortable />
                  <el-table-column prop="damage_per_death" label="每死输出值" min-width="90" align="right" sortable />
                  <el-table-column prop="taken_per_death" label="每死承伤" min-width="85" align="right" sortable />
                  <el-table-column prop="healing_per_death" label="死亡治疗量" min-width="90" align="right" sortable />
                  <el-table-column prop="heal_conversion" label="治疗转化率" min-width="90" align="right" sortable>
                    <template #default="{ row: m }">{{ m.heal_conversion.toFixed(2) }}</template>
                  </el-table-column>
                  <el-table-column prop="kill_ratio" label="击杀占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.kill_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="assist_ratio" label="助攻占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.assist_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="player_damage_ratio" label="人伤占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.player_damage_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="building_ratio" label="拆塔占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.building_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="taken_ratio" label="承伤占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.taken_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="death_ratio" label="死亡占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.death_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="heal_ratio" label="治疗占比" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.heal_ratio) }}</template>
                  </el-table-column>
                  <el-table-column prop="revive_rate" label="清泉羽化率" min-width="90" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.revive_rate) }}</template>
                  </el-table-column>
                  <el-table-column prop="fen_gu_rate" label="焚骨率" min-width="80" align="right" sortable>
                    <template #default="{ row: m }">{{ pct(m.fen_gu_rate) }}</template>
                  </el-table-column>
                  <el-table-column prop="player_damage" label="玩家伤害" min-width="100" align="right" sortable>
                    <template #default="{ row: m }">{{ fmtNum(m.player_damage) }}</template>
                  </el-table-column>
                  <el-table-column prop="building_damage" label="建筑伤害" min-width="100" align="right" sortable>
                    <template #default="{ row: m }">{{ fmtNum(m.building_damage) }}</template>
                  </el-table-column>
                  <el-table-column prop="healing" label="治疗" min-width="90" align="right" sortable>
                    <template #default="{ row: m }">{{ fmtNum(m.healing) }}</template>
                  </el-table-column>
                  <el-table-column prop="damage_taken" label="承伤" min-width="90" align="right" sortable>
                    <template #default="{ row: m }">{{ fmtNum(m.damage_taken) }}</template>
                  </el-table-column>
                  <el-table-column prop="revives" label="复活/清泉" min-width="80" align="right" sortable />
                  <el-table-column prop="fen_gu" label="焚骨" min-width="70" align="right" sortable />
                </el-table>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="squad_name" label="小队" min-width="120" fixed="left" />
          <el-table-column prop="totals.player_count" label="人数" min-width="60" align="right" sortable />
          <el-table-column prop="totals.kills" label="击杀" min-width="70" align="right" sortable />
          <el-table-column prop="totals.assists" label="助攻" min-width="70" align="right" sortable />
          <el-table-column prop="totals.player_damage" label="伤害" min-width="100" align="right" sortable>
            <template #default="{ row }">{{ fmtNum(row.totals.player_damage) }}</template>
          </el-table-column>
          <el-table-column prop="totals.building_damage" label="塔伤" min-width="100" align="right" sortable>
            <template #default="{ row }">{{ fmtNum(row.totals.building_damage) }}</template>
          </el-table-column>
          <el-table-column prop="totals.healing" label="治疗" min-width="90" align="right" sortable>
            <template #default="{ row }">{{ fmtNum(row.totals.healing) }}</template>
          </el-table-column>
          <el-table-column prop="totals.damage_taken" label="承伤" min-width="90" align="right" sortable>
            <template #default="{ row }">{{ fmtNum(row.totals.damage_taken) }}</template>
          </el-table-column>
          <el-table-column prop="totals.deaths" label="死亡" min-width="60" align="right" sortable />
          <el-table-column prop="indicators.kda" label="KDA" min-width="70" align="right" sortable>
            <template #default="{ row }">{{ row.indicators.kda.toFixed(2) }}</template>
          </el-table-column>
          <el-table-column prop="indicators.dps" label="秒伤" min-width="70" align="right" sortable>
            <template #default="{ row }">{{ row.indicators.dps.toFixed(0) }}</template>
          </el-table-column>
        </el-table>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { getSquadAnalysis } from '@/api/matchData'
import type { SquadAnalysis } from '@/types/matchData'
import { fmtNum, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const loading = ref(false)
const squads = ref<SquadAnalysis[]>([])
const selectedSquad = ref('')

async function load() {
  loading.value = true
  try {
    const data = await getSquadAnalysis(props.scheduleId, props.roundNo)
    squads.value = data.squads
    if (!squads.value.some((s) => s.squad_name === selectedSquad.value)) {
      selectedSquad.value = squads.value[0]?.squad_name ?? ''
    }
  } finally {
    loading.value = false
  }
}

watch(() => props.roundNo, load, { immediate: true })

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

function barBase(data: number[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    grid: { left: 16, right: 20, top: 30, bottom: 56, containLabel: true },
    xAxis: {
      type: 'category',
      data: squads.value.map((s) => s.squad_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 30, fontSize: 10, width: 60, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      {
        name: '数值',
        type: 'bar',
        barWidth: 16,
        itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] },
        data,
      },
    ],
  }
}

const killsBarOption = computed(() =>
  barBase(squads.value.map((s) => s.totals.kills)),
)

const damageBarOption = computed(() =>
  barBase(squads.value.map((s) => +(s.totals.player_damage / 10000).toFixed(0))),
)

const towerBarOption = computed(() =>
  barBase(squads.value.map((s) => +(s.totals.building_damage / 10000).toFixed(0))),
)

const selected = computed(() => squads.value.find((s) => s.squad_name === selectedSquad.value))

const profPieOption = computed(() => {
  const counts = new Map<string, number>()
  for (const m of selected.value?.members ?? []) {
    const prof = m.profession || '未知'
    counts.set(prof, (counts.get(prof) ?? 0) + 1)
  }
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', ...CHART_THEME.tooltip, formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
    series: [
      {
        type: 'pie',
        radius: ['45%', '72%'],
        center: ['40%', '50%'],
        data: [...counts.entries()].map(([name, value]) => ({
          name,
          value,
          itemStyle: { color: profColor(name), borderColor: '#fff', borderWidth: 2 },
        })),
        label: { show: false },
        emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
      },
    ],
  }
})
</script>

<style scoped>
.squad-analysis-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
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

.chart-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
}

.squad-members {
  padding: 10px 16px 14px 44px;
  background: var(--ink-bg-wash);
}

.squad-members__title {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
  margin-bottom: 8px;
}

@media (max-width: 768px) {
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

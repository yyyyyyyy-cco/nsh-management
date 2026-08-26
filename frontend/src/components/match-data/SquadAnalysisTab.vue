<template>
  <div class="squad-analysis-tab">
    <el-empty v-if="!loading && squads.length === 0" description="暂无数据或未关联排表（需先导入 CSV 与排表）" />
    <template v-else>
      <el-tabs v-model="mainTab" class="squad-main-tabs">
        <!-- 子 tab 1：总览图表 -->
        <el-tab-pane label="总览图表" name="overview">
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
                <el-select v-model="pieSquad" size="small" style="width: 180px">
                  <el-option v-for="s in squads" :key="s.squad_name" :label="s.squad_name" :value="s.squad_name" />
                </el-select>
              </div>
              <EChart :option="profPieOption" :height="300" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 子 tab 2：小队明细 -->
        <el-tab-pane label="小队明细" name="detail">

      <!-- 小队卡片网格 -->
      <div class="chart-card">
        <div class="chart-card__head">
          <span class="chart-card__title">小队概览</span>
          <div class="card-toolbar">
            <span class="card-toolbar__count">共 {{ squads.length }} 个小队 · {{ totalPlayers }} 人</span>
            <el-checkbox v-model="compareMode" label="对比模式" />
          </div>
        </div>

        <div class="squad-grid">
          <div
            v-for="s in squads"
            :key="s.squad_name"
            class="squad-card"
            :class="{ 'squad-card--active': detailSquad === s.squad_name }"
            @click="openDetail(s.squad_name)"
          >
            <div class="squad-card__header">
              <el-checkbox
                v-if="compareMode"
                v-model="compareChecked[s.squad_name]"
                @click.stop
              />
              <span class="squad-card__name">{{ s.squad_name }}</span>
              <span class="squad-card__count">{{ s.totals.player_count }}人</span>
            </div>
            <div class="squad-card__metrics">
              <div class="metric-item">
                <span class="metric-label">击杀</span>
                <span class="metric-value num">{{ s.totals.kills }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">伤害</span>
                <span class="metric-value num">{{ fmtNum(s.totals.player_damage) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">塔伤</span>
                <span class="metric-value num">{{ fmtNum(s.totals.building_damage) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">治疗</span>
                <span class="metric-value num">{{ fmtNum(s.totals.healing) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">承伤</span>
                <span class="metric-value num">{{ fmtNum(s.totals.damage_taken) }}</span>
              </div>
              <div class="metric-item">
                <span class="metric-label">KDA</span>
                <span class="metric-value num">{{ s.indicators.kda.toFixed(2) }}</span>
              </div>
            </div>
            <div class="squad-card__footer">
              <el-button text type="primary" size="small">查看详情 →</el-button>
            </div>
          </div>
        </div>

        <!-- 对比按钮 -->
        <div v-if="compareMode && compareSelectedNames.length >= 2" class="compare-bar">
          <span>已选 {{ compareSelectedNames.length }} 个小队</span>
          <el-button type="primary" size="small" @click="openCompare">对比所选小队</el-button>
        </div>
      </div>

      <!-- 小队详情面板 -->
      <div v-if="detailSquad" class="chart-card detail-panel">
        <div class="chart-card__head">
          <span class="chart-card__title">{{ detailSquad }} · 成员明细</span>
          <el-button text size="small" @click="detailSquad = ''">关闭</el-button>
        </div>

        <!-- 成员表：3 个子标签 -->
        <el-tabs v-model="detailSubTab" class="detail-sub-tabs">
          <el-tab-pane label="基础数据" name="basic">
            <el-table :data="detailMembers" size="small" border max-height="360">
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
            <el-table :data="detailMembers" size="small" border max-height="360">
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
            <el-table :data="detailMembers" size="small" border max-height="360">
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

        <!-- 成员贡献可视化 -->
        <div class="chart-row" style="margin-top: 12px">
          <div class="chart-card" style="border: none; padding: 0; box-shadow: none">
            <div class="chart-card__title">成员贡献构成</div>
            <EChart :option="detailContribOption" :height="260" />
          </div>
          <div class="chart-card" style="border: none; padding: 0; box-shadow: none">
            <div class="chart-card__title">成员职业分布</div>
            <EChart :option="detailProfPie" :height="260" />
          </div>
        </div>
      </div>

      <!-- 多小队对比面板 -->
      <div v-if="compareVisible" class="chart-card compare-panel">
        <div class="chart-card__head">
          <span class="chart-card__title">小队对比（{{ compareSelectedNames.join(' vs ') }}）</span>
          <el-button text size="small" @click="compareVisible = false">关闭</el-button>
        </div>

        <div class="chart-row">
          <div class="chart-card" style="border: none; padding: 0; box-shadow: none">
            <div class="chart-card__title">汇总对比</div>
            <EChart :option="compareSummaryBar" :height="300" />
          </div>
          <div class="chart-card" style="border: none; padding: 0; box-shadow: none">
            <div class="chart-card__title">均值指标雷达图</div>
            <EChart :option="compareRadar" :height="300" />
          </div>
        </div>

        <!-- 差值表（恰好选 2 队时） -->
        <div v-if="compareSelectedNames.length === 2" class="diff-table-wrap">
          <div class="chart-card__title">差值 / 波动值</div>
          <el-table :data="compareDiffRows" size="small" border max-height="260">
            <el-table-column prop="label" label="指标" min-width="110" />
            <el-table-column :label="compareSelectedNames[0]" min-width="90" align="right">
              <template #default="{ row }">{{ row.v1 }}</template>
            </el-table-column>
            <el-table-column :label="compareSelectedNames[1]" min-width="90" align="right">
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
      </div>
      </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'

import { getSquadAnalysis } from '@/api/matchData'
import type { SquadAnalysis } from '@/types/matchData'
import { fmtNum, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const loading = ref(false)
const squads = ref<SquadAnalysis[]>([])
const pieSquad = ref('')
const mainTab = ref('overview')

// 详情面板
const detailSquad = ref('')
const detailSubTab = ref('basic')

// 对比模式
const compareMode = ref(false)
const compareChecked = reactive<Record<string, boolean>>({})
const compareVisible = ref(false)

const totalPlayers = computed(() => squads.value.reduce((s, sq) => s + sq.totals.player_count, 0))

async function load() {
  loading.value = true
  try {
    const data = await getSquadAnalysis(props.scheduleId, props.roundNo)
    squads.value = data.squads
    if (!squads.value.some((s) => s.squad_name === pieSquad.value)) {
      pieSquad.value = squads.value[0]?.squad_name ?? ''
    }
    // 初始化 checkbox 状态
    for (const s of squads.value) {
      if (!(s.squad_name in compareChecked)) compareChecked[s.squad_name] = false
    }
    // 关闭已不存在的面板
    if (detailSquad.value && !squads.value.some((s) => s.squad_name === detailSquad.value)) {
      detailSquad.value = ''
    }
  } finally {
    loading.value = false
  }
}

watch(() => props.roundNo, load, { immediate: true })

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

// ==================== 顶部图表 ====================

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
    series: [{
      name: '数值', type: 'bar', barWidth: 16,
      itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] },
      data,
    }],
  }
}

const killsBarOption = computed(() => barBase(squads.value.map((s) => s.totals.kills)))
const damageBarOption = computed(() => barBase(squads.value.map((s) => +(s.totals.player_damage / 10000).toFixed(0))))
const towerBarOption = computed(() => barBase(squads.value.map((s) => +(s.totals.building_damage / 10000).toFixed(0))))

const selectedForPie = computed(() => squads.value.find((s) => s.squad_name === pieSquad.value))

const profPieOption = computed(() => {
  const counts = new Map<string, number>()
  for (const m of selectedForPie.value?.members ?? []) {
    const prof = m.profession || '未知'
    counts.set(prof, (counts.get(prof) ?? 0) + 1)
  }
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', ...CHART_THEME.tooltip, formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
    series: [{
      type: 'pie', radius: ['45%', '72%'], center: ['40%', '50%'],
      data: [...counts.entries()].map(([name, value]) => ({
        name, value,
        itemStyle: { color: profColor(name), borderColor: '#fff', borderWidth: 2 },
      })),
      label: { show: false },
      emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
    }],
  }
})

// ==================== 详情面板 ====================

function openDetail(name: string) {
  detailSquad.value = detailSquad.value === name ? '' : name
  detailSubTab.value = 'basic'
}

const detailSquadData = computed(() => squads.value.find((s) => s.squad_name === detailSquad.value))
const detailMembers = computed(() => detailSquadData.value?.members ?? [])

const CONTRIB_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57']

const detailContribOption = computed(() => {
  const members = detailMembers.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: ['玩家伤害', '建筑伤害', '治疗'], ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '玩家伤害', type: 'bar', barWidth: 8, barGap: '20%', itemStyle: { color: CONTRIB_COLORS[0], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.player_damage) },
      { name: '建筑伤害', type: 'bar', barWidth: 8, itemStyle: { color: CONTRIB_COLORS[1], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.building_damage) },
      { name: '治疗', type: 'bar', barWidth: 8, itemStyle: { color: CONTRIB_COLORS[2], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.healing) },
    ],
  }
})

const detailProfPie = computed(() => {
  const counts = new Map<string, number>()
  for (const m of detailMembers.value) {
    const prof = m.profession || '未知'
    counts.set(prof, (counts.get(prof) ?? 0) + 1)
  }
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'item', ...CHART_THEME.tooltip, formatter: '{b}: {c}人 ({d}%)' },
    legend: { orient: 'vertical', right: 5, top: 'center', ...CHART_THEME.legend },
    series: [{
      type: 'pie', radius: ['45%', '72%'], center: ['40%', '50%'],
      data: [...counts.entries()].map(([name, value]) => ({
        name, value,
        itemStyle: { color: profColor(name), borderColor: '#fff', borderWidth: 2 },
      })),
      label: { show: false },
      emphasis: { label: { show: true, fontWeight: 'bold' }, itemStyle: { shadowBlur: 10, shadowColor: 'rgba(0,0,0,0.3)' } },
    }],
  }
})

// ==================== 对比面板 ====================

const compareSelectedNames = computed(() =>
  squads.value.filter((s) => compareChecked[s.squad_name]).map((s) => s.squad_name),
)

const compareSelectedSquads = computed(() =>
  squads.value.filter((s) => compareChecked[s.squad_name]),
)

function openCompare() {
  compareVisible.value = true
}

const COMPARE_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b']

const compareSummaryBar = computed(() => {
  const sel = compareSelectedSquads.value
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'assists', label: '助攻' },
    { key: 'player_damage', label: '玩家伤害' },
    { key: 'building_damage', label: '建筑伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { top: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: metrics.map((m) => m.label), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine },
    series: sel.map((s, i) => ({
      name: s.squad_name,
      type: 'bar',
      barWidth: 14,
      barGap: '30%',
      itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length], borderRadius: [3, 3, 0, 0] },
      data: metrics.map((m) => s.totals[m.key as keyof typeof s.totals]),
    })),
  }
})

const compareRadar = computed(() => {
  const sel = compareSelectedSquads.value
  const dims = [
    { name: 'KDA', max: 0 },
    { name: '秒伤', max: 0 },
    { name: '每死输出', max: 0 },
    { name: '每死承伤', max: 0 },
    { name: '治疗转化', max: 0 },
  ]
  const keys: (keyof SquadAnalysis['indicators'])[] = ['kda', 'dps', 'damage_per_death', 'taken_per_death', 'heal_conversion']
  // 动态 max
  for (const d of dims) d.max = 1
  for (const s of sel) {
    keys.forEach((k, i) => {
      const v = s.indicators[k] as number
      if (v > dims[i].max) dims[i].max = v
    })
  }
  // 留余量
  for (const d of dims) d.max = Math.ceil(d.max * 1.15)

  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    radar: {
      center: ['50%', '46%'],
      radius: '60%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 50 },
      indicator: dims,
    },
    series: [{
      type: 'radar',
      data: sel.map((s, i) => ({
        name: s.squad_name,
        value: keys.map((k) => s.indicators[k] as number),
        areaStyle: { opacity: 0.1 },
        lineStyle: { width: 2.5, color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
        itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
        symbol: 'circle',
        symbolSize: 5,
      })),
    }],
  }
})

const COMPARE_METRIC_LABELS: Record<string, string> = {
  kills: '总击杀', assists: '总助攻', player_damage: '玩家伤害',
  building_damage: '建筑伤害', healing: '治疗', damage_taken: '承伤',
  deaths: '总死亡', kda: '均 KDA', dps: '均秒伤',
  damage_per_death: '均每死输出', taken_per_death: '均每死承伤',
  heal_conversion: '均治疗转化',
}

const compareDiffRows = computed(() => {
  const sel = compareSelectedSquads.value
  if (sel.length !== 2) return []
  const [a, b] = sel
  const rows: { label: string; v1: string; v2: string; diff: number; diffStr: string; wave: number }[] = []

  // 汇总指标
  const totalKeys: (keyof SquadAnalysis['totals'])[] = ['kills', 'assists', 'player_damage', 'building_damage', 'healing', 'damage_taken', 'deaths']
  for (const k of totalKeys) {
    const v1 = a.totals[k] as number
    const v2 = b.totals[k] as number
    const diff = v1 - v2
    const base = Math.min(v1, v2)
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: fmtNum(v1), v2: fmtNum(v2),
      diff, diffStr: fmtNum(Math.abs(diff)),
      wave: base > 0 ? Math.abs(diff) / base * 100 : 0,
    })
  }

  // 均值指标
  const indKeys: (keyof SquadAnalysis['indicators'])[] = ['kda', 'dps', 'damage_per_death', 'taken_per_death', 'heal_conversion']
  for (const k of indKeys) {
    const v1 = a.indicators[k] as number
    const v2 = b.indicators[k] as number
    const diff = +(v1 - v2).toFixed(2)
    const base = Math.min(v1, v2)
    const isDecimal = k === 'kda' || k === 'heal_conversion'
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: isDecimal ? v1.toFixed(2) : fmtNum(Math.round(v1)),
      v2: isDecimal ? v2.toFixed(2) : fmtNum(Math.round(v2)),
      diff, diffStr: isDecimal ? Math.abs(diff).toFixed(2) : fmtNum(Math.round(Math.abs(diff))),
      wave: base > 0 ? Math.abs(diff) / base * 100 : 0,
    })
  }

  return rows
})
</script>

<style scoped>
.squad-analysis-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.squad-main-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.squad-main-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.squad-main-tabs :deep(.el-tabs__content) {
  padding: 0;
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

.card-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-toolbar__count {
  font-size: 12px;
  color: var(--ink-400);
}

/* ===== 卡片网格 ===== */
.squad-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.squad-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 12px 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--ink-bg-paper);
}

.squad-card:hover {
  border-color: var(--gold-400);
  box-shadow: var(--shadow-sm);
}

.squad-card--active {
  border-color: var(--gold-500);
  box-shadow: 0 0 0 1px var(--gold-200);
}

.squad-card__header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
}

.squad-card__name {
  font-weight: 700;
  font-size: 13px;
  color: var(--ink-800);
}

.squad-card__count {
  margin-left: auto;
  font-size: 11px;
  color: var(--ink-400);
}

.squad-card__metrics {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px 8px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.metric-label {
  font-size: 10px;
  color: var(--ink-400);
}

.metric-value {
  font-size: 14px;
  font-weight: 800;
  color: var(--gold-700);
}

.squad-card__footer {
  margin-top: 8px;
  text-align: right;
}

/* ===== 对比栏 ===== */
.compare-bar {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--edge-faint);
  font-size: 13px;
  color: var(--ink-500);
}

/* ===== 详情面板 ===== */
.detail-panel,
.compare-panel {
  border-color: var(--gold-300);
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

  .squad-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>

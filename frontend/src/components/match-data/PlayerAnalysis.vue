<template>
  <div class="player-analysis">
    <!-- 第一行：击杀 vs 伤害散点图 + 治疗 vs 承伤散点图（并排） -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-card__title">击杀 vs 伤害分析</div>
        <EChart :option="scatterOption" :height="320" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">治疗 vs 承伤分析</div>
        <EChart :option="healTakenOption" :height="320" />
      </div>
    </div>

    <!-- 玩家维度图表：KDA 分布散点 + 伤害-治疗气泡 -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-card__title">击杀 vs 重伤（KDA 分布）</div>
        <EChart :option="kdaScatterOption" :height="320" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">伤害 vs 治疗气泡（气泡大小 = 承伤）</div>
        <EChart :option="dmgHealBubbleOption" :height="320" />
      </div>
    </div>

    <!-- 玩家综合能力雷达图 -->
    <div class="chart-card">
      <div class="chart-card__head">
        <span class="chart-card__title">玩家综合能力雷达图（对比）</span>
        <div class="radar-selectors">
          <el-select
            v-model="radarLeft"
            filterable
            placeholder="搜索左侧玩家"
            size="small"
            style="width: 180px"
          >
            <el-option
              v-for="p in allPlayers"
              :key="'L-' + p.player_name"
              :label="p.player_name"
              :value="p.player_name"
            />
          </el-select>
          <span class="radar-vs">VS</span>
          <el-select
            v-model="radarRight"
            filterable
            placeholder="搜索右侧玩家"
            size="small"
            style="width: 180px"
          >
            <el-option
              v-for="p in allPlayers"
              :key="'R-' + p.player_name"
              :label="p.player_name"
              :value="p.player_name"
            />
          </el-select>
        </div>
      </div>
      <EChart :option="radarOption" :height="380" />
    </div>

    <!-- 职业×指标热力图 -->
    <div class="chart-card">
      <div class="chart-card__title">职业×指标热力图</div>
      <EChart :option="heatmapOption" :height="heatmapHeight" />
    </div>

    <!-- 玩家四维构成（Top10） -->
    <div class="chart-card">
      <div class="chart-card__title">玩家四维数据（Top 10）</div>
      <EChart :option="playerBarsOption" :height="320" />
    </div>

    <!-- 阵营职业伤害/治疗构成堆叠柱状图 -->
    <div v-if="camps.length >= 2" class="stack-row">
      <div class="chart-card">
        <div class="chart-card__title">阵营职业伤害构成</div>
        <EChart :option="stackOption('player_damage')" :height="300" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">阵营职业治疗构成</div>
        <EChart :option="stackOption('healing')" :height="300" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { MatchData } from '@/types/matchData'
import { aggregateCamps, calcKDA, computeScores, fmtNum, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const camps = computed(() => aggregateCamps(props.items))
const allProfs = computed(() => [...new Set(props.items.map((r) => r.profession || '未知'))].sort())

const scatterOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = (p as { data: number[] }).data
      return `<b>${d[3]}</b> (${d[4]})<br/>击杀: ${d[0]}<br/>伤害: ${fmtNum(d[1])}<br/>治疗: ${fmtNum(d[2])}<br/>KDA: ${d[5].toFixed(1)}`
    },
  },
  grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
  xAxis: {
    name: '击杀',
    nameLocation: 'middle',
    nameGap: 32,
    axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 12 },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
  },
  yAxis: {
    name: '玩家伤害',
    nameLocation: 'middle',
    nameGap: 50,
    axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(6, Math.min(13, data[5] * 2)),
      data: props.items.map((r) => [
        r.kills,
        r.player_damage,
        r.healing,
        r.player_name,
        r.profession || '未知',
        calcKDA(r),
      ]),
      itemStyle: {
        color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
        opacity: 0.75,
        borderColor: 'rgba(0,0,0,0.08)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      markLine: {
        silent: true,
        lineStyle: { color: 'rgba(0,0,0,0.1)', type: 'dashed', width: 1 },
        data: [
          { type: 'average', name: '平均击杀' },
          { type: 'average', valueIndex: 1, name: '平均伤害' },
        ],
        label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
      },
    },
  ],
}))

const heatmapHeight = computed(() => Math.max(340, allProfs.value.length * 44 + 120))

const heatmapOption = computed(() => {
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'player_damage', label: '伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
    { key: 'assists', label: '助攻' },
  ]
  const raw: { xi: number; yi: number; avg: number; label: string; prof: string }[] = []
  allProfs.value.forEach((prof, yi) => {
    const players = props.items.filter((r) => (r.profession || '未知') === prof)
    if (!players.length) return
    metrics.forEach((m, xi) => {
      const avg = players.reduce((s, r) => s + (r[m.key as keyof MatchData] as number), 0) / players.length
      raw.push({ xi, yi, avg, label: m.label, prof })
    })
  })
  const maxVals = metrics.map((_, xi) => Math.max(...raw.filter((r) => r.xi === xi).map((r) => r.avg)))
  // 按平均值归一化：avg / 该列最高均值 * 100，颜色直接反映平均值大小（非列内 min-max 拉伸）
  const data = raw.map((r) => {
    const normalized = maxVals[r.xi] > 0 ? Math.round((r.avg / maxVals[r.xi]) * 100) : 0
    return [r.xi, r.yi, normalized, fmtNum(r.avg), r.label, r.prof]
  })
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: number[] }).data
        return `<b>${d[5]}</b> · ${d[4]}<br/>平均值: ${d[3]}<br/>相对水平: ${d[2]}%`
      },
    },
    grid: { left: 72, right: 24, top: 12, bottom: 64 },
    xAxis: {
      type: 'category',
      data: metrics.map((m) => m.label),
      axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0, fontSize: 13 },
      axisTick: { show: false },
      splitArea: { show: true, areaStyle: { color: ['transparent', 'rgba(0,0,0,0.015)'] } },
    },
    yAxis: {
      type: 'category',
      data: allProfs.value,
      axisLabel: { ...CHART_THEME.axis.axisLabel, fontSize: 13, fontWeight: 600, width: 56, overflow: 'truncate' },
      axisTick: { show: false },
      axisLine: { show: false },
    },
    visualMap: {
      min: 0,
      max: 100,
      dimension: 2, // 显式绑定归一化值维度（data 第 3 项），否则默认取第一维 xi 导致颜色失效
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: 4,
      itemWidth: 14,
      itemHeight: 100,
      inRange: { color: ['#fbe6a0', '#f6c043', '#ef9121', '#dd6c0d', '#b95205', '#7a2604'] },
      textStyle: { color: '#8a8378', fontSize: 11 },
    },
    series: [
      {
        type: 'heatmap',
        data,
        label: {
          show: true,
          fontSize: 11,
          color: '#333',
          fontWeight: 500,
          formatter: (p: unknown) => (p as { data: number[] }).data[3],
        },
        itemStyle: {
          borderColor: '#fff',
          borderWidth: 3,
          borderRadius: 4,
        },
        emphasis: { itemStyle: { shadowBlur: 12, shadowColor: 'rgba(0, 0, 0, 0.4)', borderColor: '#fff', borderWidth: 2 } },
      },
    ],
  }
})

/** 治疗 vs 承伤散点：气泡大小=综合评分，颜色=职业，评估治疗职业表现。 */
const healTakenOption = computed(() => {
  const scored = computeScores(props.items)
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: number[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>治疗: ${fmtNum(d[0])}<br/>承伤: ${fmtNum(d[1])}<br/>评分: ${d[2]}<br/>KDA: ${d[5].toFixed(1)}`
      },
    },
    grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
    xAxis: {
      name: '治疗量',
      nameLocation: 'middle',
      nameGap: 32,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), margin: 12 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
    },
    yAxis: {
      name: '承受伤害',
      nameLocation: 'middle',
      nameGap: 50,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [
      {
        type: 'scatter',
        symbolSize: (data: number[]) => Math.max(6, Math.min(13, (data[5] as number) * 2)),
        data: scored.map((s) => [s.player.healing, s.player.damage_taken, s.total, s.player.player_name, s.player.profession || '未知', s.kda]),
        itemStyle: {
          color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
          opacity: 0.75,
          borderColor: 'rgba(0,0,0,0.08)',
          borderWidth: 1,
        },
        emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
        markLine: {
          silent: true,
          lineStyle: { color: 'rgba(0,0,0,0.1)', type: 'dashed', width: 1 },
          data: [
            { type: 'average', name: '平均治疗' },
            { type: 'average', valueIndex: 1, name: '平均承伤' },
          ],
          label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
        },
      },
    ],
  }
})

/** 玩家四维数据：Top10 按综合评分降序，玩家伤害/建筑伤害/治疗/承伤分组柱。 */
const playerBarsOption = computed(() => {
  const top = computeScores(props.items).slice(0, 10).map((s) => s.player)
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: ['玩家伤害', '建筑伤害', '治疗', '承伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 24, top: 30, bottom: 40, containLabel: true },
    xAxis: {
      type: 'category',
      data: top.map((r) => r.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 35, fontSize: 11, width: 60, overflow: 'truncate' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: [
      { name: '玩家伤害', type: 'bar', barWidth: 8, barGap: '25%', itemStyle: { color: '#c9a13b', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.player_damage) },
      { name: '建筑伤害', type: 'bar', barWidth: 8, itemStyle: { color: '#5b7a9d', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.building_damage) },
      { name: '治疗', type: 'bar', barWidth: 8, itemStyle: { color: '#2e8b57', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.healing) },
      { name: '承伤', type: 'bar', barWidth: 8, itemStyle: { color: '#c0392b', borderRadius: [2, 2, 0, 0] }, data: top.map((r) => r.damage_taken) },
    ],
  }
})

function stackOption(field: 'player_damage' | 'healing') {
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      ...CHART_THEME.tooltip,
      formatter: (params: unknown) => {
        const list = params as { axisValue: string; marker: string; seriesName: string; value: number }[]
        let html = `<b>${list[0].axisValue}</b><br/>`
        list.forEach((p) => {
          html += `${p.marker} ${p.seriesName}: ${fmtNum(p.value)}<br/>`
        })
        return html
      },
    },
    legend: { top: 0, ...CHART_THEME.legend, type: 'scroll' },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: camps.value.map((c) => c.camp), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: allProfs.value.map((prof) => ({
      name: prof,
      type: 'bar',
      stack: 'total',
      barWidth: 40,
      itemStyle: { color: profColor(prof), borderRadius: 0 },
      data: camps.value.map((c) =>
        props.items.filter((r) => r.camp === c.camp && (r.profession || '未知') === prof).reduce((s, r) => s + r[field], 0),
      ),
    })),
  }
}

// ==================== 玩家维度图表（设计文档 图表13/14/15） ====================

/** 击杀 vs 重伤散点（KDA 分布）。 */
const kdaScatterOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = (p as { data: (number | string)[] }).data
      return `<b>${d[2]}</b> (${d[3]})<br/>击杀: ${d[0]}<br/>重伤: ${d[1]}<br/>KDA: ${Number(d[4]).toFixed(2)}`
    },
  },
  grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
  xAxis: {
    name: '击杀', nameLocation: 'middle', nameGap: 32,
    axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 12 },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
  },
  yAxis: {
    name: '重伤（死亡）', nameLocation: 'middle', nameGap: 50,
    axisLabel: { ...CHART_THEME.axis.axisLabel, width: 60, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: 9,
      data: props.items.map((r) => [r.kills, r.deaths, r.player_name, r.profession || '未知', calcKDA(r)]),
      itemStyle: {
        color: (p: { data: (number | string)[] }) => profColor(String(p.data[3])),
        opacity: 0.75,
        borderColor: 'rgba(0,0,0,0.08)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      markLine: {
        silent: true,
        lineStyle: { color: 'rgba(0,0,0,0.1)', type: 'dashed', width: 1 },
        data: [
          { type: 'average', name: '平均击杀' },
          { type: 'average', valueIndex: 1, name: '平均重伤' },
        ],
        label: { show: true, position: 'end', fontSize: 10, color: '#aaa' },
      },
    },
  ],
}))

/** 伤害 vs 治疗气泡：气泡大小 = 承伤（开根号缩放）。 */
const dmgHealBubbleOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = (p as { data: (number | string)[] }).data
      return `<b>${d[3]}</b> (${d[4]})<br/>伤害: ${fmtNum(Number(d[0]))}<br/>治疗: ${fmtNum(Number(d[1]))}<br/>承伤: ${fmtNum(Number(d[2]))}`
    },
  },
  grid: { left: 16, right: 24, top: 32, bottom: 16, containLabel: true },
  xAxis: {
    name: '玩家伤害', nameLocation: 'middle', nameGap: 32,
    axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), margin: 12 },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
  },
  yAxis: {
    name: '治疗量', nameLocation: 'middle', nameGap: 50,
    axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 60, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(6, Math.min(30, Math.sqrt(data[2]) / 100)),
      data: props.items.map((r) => [r.player_damage, r.healing, r.damage_taken, r.player_name, r.profession || '未知']),
      itemStyle: {
        color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
        opacity: 0.7,
        borderColor: 'rgba(0,0,0,0.08)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
    },
  ],
}))

/** 全部玩家列表（用于搜索选择器）。 */
const allPlayers = computed(() => [...props.items])

const radarLeft = ref('')
const radarRight = ref('')

watch(
  () => props.items,
  (list) => {
    if (!list.length) return
    // 左侧默认击杀第一
    const sorted = [...list].sort((a, b) => b.kills - a.kills)
    if (!radarLeft.value || !list.some((p) => p.player_name === radarLeft.value)) {
      radarLeft.value = sorted[0]?.player_name ?? ''
    }
    // 右侧默认击杀第二（如果只有一人则同人）
    if (!radarRight.value || !list.some((p) => p.player_name === radarRight.value)) {
      radarRight.value = sorted[1]?.player_name ?? sorted[0]?.player_name ?? ''
    }
  },
  { immediate: true },
)

const RADAR_COLORS = ['#c9a13b', '#5b7a9d']

const radarOption = computed(() => {
  const pL = props.items.find((r) => r.player_name === radarLeft.value)
  const pR = props.items.find((r) => r.player_name === radarRight.value)
  const players = [pL, pR].filter(Boolean) as MatchData[]
  if (!players.length) return {}
  const maxOf = (key: 'kills' | 'assists' | 'player_damage' | 'healing' | 'damage_taken' | 'kda') => {
    const vals =
      key === 'kda'
        ? props.items.map((r) => calcKDA(r))
        : props.items.map((r) => r[key] as number)
    return Math.max(...vals, 1) * 1.15
  }
  const dims = [
    { name: '击杀', max: maxOf('kills') },
    { name: '助攻', max: maxOf('assists') },
    { name: '伤害', max: maxOf('player_damage') },
    { name: '治疗', max: maxOf('healing') },
    { name: '承伤', max: maxOf('damage_taken') },
    { name: 'KDA', max: maxOf('kda') },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: players.map((p) => p.player_name), ...CHART_THEME.legend },
    radar: {
      center: ['50%', '46%'],
      radius: '62%',
      axisName: { ...CHART_THEME.axis.axisName, color: '#6d665c' },
      splitArea: { areaStyle: { color: ['rgba(0,0,0,0.02)', 'transparent'] } },
      indicator: dims.map((d) => ({ name: d.name, max: Math.round(d.max) })),
    },
    series: [
      {
        type: 'radar',
        data: players.map((p, i) => ({
          name: p.player_name,
          value: [p.kills, p.assists, p.player_damage, p.healing, p.damage_taken, calcKDA(p)],
          areaStyle: { opacity: 0.1 },
          lineStyle: { width: 2.5, color: RADAR_COLORS[i] },
          itemStyle: { color: RADAR_COLORS[i] },
          symbol: 'circle',
          symbolSize: 5,
        })),
      },
    ],
  }
})
</script>

<style scoped>
.player-analysis {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.stack-row,
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

.radar-selectors {
  display: flex;
  align-items: center;
  gap: 10px;
}

.radar-vs {
  font-size: 13px;
  font-weight: 800;
  color: var(--ink-400);
  letter-spacing: 1px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .stack-row,
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

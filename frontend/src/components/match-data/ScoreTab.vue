<template>
  <div class="score-tab">
    <!-- 评分雷达图 + 散点图 -->
    <div class="score-row">
      <div class="chart-card">
        <div class="chart-card__title">TOP10 贡献雷达（100 = 同职业平均）</div>
        <EChart :option="radarOption" :height="350" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">评分 × 重伤倍数</div>
        <EChart :option="scatterOption" :height="350" />
      </div>
    </div>

    <!-- 综合评分排名表 -->
    <div class="chart-card">
      <div class="chart-card__title">综合评分排名</div>
      <el-table :data="scores" size="small" max-height="500" :cell-style="{ textAlign: 'center' }" :header-cell-style="{ textAlign: 'center' }" @row-click="showDetail">
        <el-table-column label="排名" width="55" align="center">
          <template #default="{ $index }">
            <span class="rank-badge num" :class="`rank-badge--${$index + 1}`">{{ $index + 1 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="ID" min-width="110">
          <template #default="{ row }">
            <span class="player-cell">
              <i class="prof-dot" :style="{ background: profColor(row.player.profession) }" />
              <span class="rank-player">{{ row.player.player_name }}</span>
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="player.profession" label="职业" min-width="70" />
        <el-table-column prop="player.camp" label="阵营" min-width="55" />
        <el-table-column label="总分" min-width="65" align="right" sortable :sort-by="'total'">
          <template #default="{ row }">
            <span class="score-num" :class="scoreClass(row.total)">{{ row.total }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="archetype" label="原型" min-width="85">
          <template #default="{ row }">
            <span v-if="row.archetype !== row.player.profession" class="archetype-tag">{{ row.archetype }}</span>
            <span v-else class="archetype-same">—</span>
          </template>
        </el-table-column>
        <el-table-column label="重伤倍数" min-width="75" align="right" sortable :sort-by="'deathMult'">
          <template #default="{ row }">
            <span :class="row.deathMult > 1.5 ? 'death-high' : 'death-normal'">{{ row.deathMult.toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="KDA" min-width="60" align="right" sortable :sort-by="'kda'">
          <template #default="{ row }">{{ row.kda.toFixed(1) }}</template>
        </el-table-column>
      </el-table>
    </div>

    <!-- 得分分解弹窗 -->
    <el-dialog v-model="detailVisible" :title="detailTitle" width="520px" append-to-body>
      <el-table :data="detailRows" size="small" border :row-class-name="detailRowClass">
        <el-table-column prop="name" label="项目" min-width="90" />
        <el-table-column prop="mult" label="贡献倍数" min-width="95" align="right" />
        <el-table-column prop="weight" label="有效权重" min-width="95" align="right" />
        <el-table-column prop="points" label="得分" min-width="80" align="right" />
      </el-table>
      <p class="detail-note">倍数 = 个人值 ÷ 本轮同职业(分路)均值；有效权重来自该原型配置（轮内可用项归一化）。合计为四舍五入后的展示分。</p>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { MatchData } from '@/types/matchData'
import { computeScores, profColor, SCORE_METRICS } from './analysis'
import type { PlayerScore } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

const props = defineProps<{ items: MatchData[] }>()

const scores = computed(() => computeScores(props.items))

// 得分分解弹窗
const detailVisible = ref(false)
const detailRow = ref<PlayerScore | null>(null)
const detailTitle = computed(() =>
  detailRow.value ? `${detailRow.value.player.player_name} · ${detailRow.value.archetype} · 得分分解` : '',
)
const detailRows = computed(() => {
  const r = detailRow.value
  if (!r) return []
  interface DetailRow { name: string; mult: string; weight: string; points: string; isDeath: boolean; isTotal: boolean }
  const rows: DetailRow[] = r.breakdown.map((b) => ({
    name: b.metric,
    mult: b.mult.toFixed(2),
    weight: b.weight.toFixed(3),
    points: b.points.toFixed(1),
    isDeath: false,
    isTotal: false,
  }))
  rows.push({ name: '重伤惩罚', mult: `${r.deathMult.toFixed(2)} 倍`, weight: '15/倍', points: `-${r.deathPts.toFixed(1)}`, isDeath: true, isTotal: false })
  rows.push({ name: '合计', mult: '', weight: '', points: String(r.total), isDeath: false, isTotal: true })
  return rows
})

function showDetail(row: PlayerScore) {
  detailRow.value = row
  detailVisible.value = true
}

function detailRowClass({ row }: { row: { isDeath: boolean; isTotal: boolean } }) {
  return row.isTotal ? 'detail-total' : row.isDeath ? 'detail-death' : ''
}

const radarOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = p as { name: string; value: number[] }
      const lines = SCORE_METRICS.map((m, i) => `${m}: ${d.value[i]}`).join('<br/>')
      return `<b>${d.name}</b><br/>${lines}<br/><span style="color:#aaa">数值为相对同职业均值的百分比</span>`
    },
  },
  legend: { bottom: 0, ...CHART_THEME.legend },
  radar: {
    center: ['50%', '45%'],
    radius: '60%',
    axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 40 },
    indicator: SCORE_METRICS.map((m) => ({ name: m, max: 300 })),
  },
  series: [
    {
      type: 'radar',
      data: scores.value.slice(0, 10).map((s) => ({
        name: s.player.player_name,
        value: SCORE_METRICS.map((m) => Math.round(s.metrics[m] * 100)),
        areaStyle: { opacity: 0.1, color: profColor(s.player.profession) },
        lineStyle: { width: 2, color: profColor(s.player.profession) },
        itemStyle: { color: profColor(s.player.profession) },
        symbol: 'circle',
        symbolSize: 4,
      })),
    },
  ],
}))

const scatterOption = computed(() => ({
  backgroundColor: 'transparent',
  tooltip: {
    ...CHART_THEME.tooltip,
    formatter: (p: unknown) => {
      const d = (p as { data: (number | string)[] }).data
      return `<b>${d[3]}</b> (${d[4]})<br/>总分: ${d[0]}<br/>重伤倍数: ${Number(d[1]).toFixed(2)}`
    },
  },
  grid: { left: 12, right: 24, top: 20, bottom: 12, containLabel: true },
  xAxis: {
    name: '综合评分',
    nameLocation: 'middle',
    nameGap: 32,
    axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [8, 0, 0, 0] },
  },
  yAxis: {
    name: '重伤倍数',
    nameLocation: 'middle',
    nameGap: 45,
    axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
    splitLine: CHART_THEME.axis.splitLine,
    nameTextStyle: { ...CHART_THEME.axis.axisName },
  },
  series: [
    {
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(10, data[0] / 6),
      data: scores.value.map((s) => [s.total, Number(s.deathMult.toFixed(2)), s.player.player_name, s.player.profession || '未知']),
      itemStyle: {
        color: (p: unknown) => profColor(String((p as { data: (number | string)[] }).data[3])),
        opacity: 0.75,
        borderColor: 'rgba(255,255,255,0.3)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      markLine: {
        silent: true,
        lineStyle: { color: 'rgba(0,0,0,0.15)', type: 'dashed', width: 1 },
        data: [
          { yAxis: 1, label: { show: true, formatter: '平均重伤', fontSize: 10, color: '#aaa', position: 'end' } },
        ],
      },
      label: {
        show: true,
        position: 'top',
        formatter: (p: unknown) => ((p as { data: (number | string)[] }).data[0] as number) >= 115 ? String((p as { data: (number | string)[] }).data[2]) : '',
        fontSize: 11,
        color: '#555',
      },
    },
  ],
}))

function scoreClass(total: number): string {
  return total >= 115 ? 'is-high' : total >= 85 ? 'is-mid' : 'is-low'
}
</script>

<style scoped>
.score-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.score-row {
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

.player-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.rank-player {
  font-weight: 600;
  color: var(--ink-900);
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  font-size: 11px;
  font-weight: 700;
  color: var(--ink-400);
  background: var(--edge-faint);
}

.rank-badge--1 {
  background: linear-gradient(135deg, #f6c94d, #d4a017);
  color: #fff;
  box-shadow: 0 2px 6px rgba(212, 160, 23, 0.4);
}

.rank-badge--2 {
  background: linear-gradient(135deg, #c9c9c9, #9a9a9a);
  color: #fff;
}

.rank-badge--3 {
  background: linear-gradient(135deg, #e0a877, #b97f4b);
  color: #fff;
}

.score-num {
  font-weight: 800;
}

.archetype-tag {
  display: inline-block;
  padding: 1px 8px;
  border-radius: 999px;
  border: 1px solid var(--gold-line, #c9a13b);
  color: var(--gold-700, #8a6d1a);
  font-size: 12px;
  white-space: nowrap;
}

.archetype-same {
  color: var(--ink-400, #999);
}

.death-high {
  color: #c0392b;
  font-weight: 700;
}

.death-normal {
  color: var(--ink-700, #555);
}

.detail-note {
  margin: 10px 0 0;
  font-size: 12px;
  color: var(--ink-500, #888);
  line-height: 1.6;
}

:deep(.detail-total) {
  font-weight: 800;
  background: var(--ink-bg-paper, #fafafa);
}

:deep(.detail-death) {
  color: #c0392b;
}

.score-num.is-high {
  color: var(--jade);
}

.score-num.is-mid {
  color: var(--gold-700);
}

.score-num.is-low {
  color: var(--ink-400);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .score-row {
    grid-template-columns: 1fr;
  }
}
</style>
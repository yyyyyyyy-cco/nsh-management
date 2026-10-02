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

    <!-- 玩家综合能力雷达图 + 伤害分布饼图（并排） -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-card__head">
          <span class="chart-card__title">玩家综合能力雷达图（对比）</span>
          <div class="radar-selectors">
            <el-select
              aria-label="搜索左侧玩家"
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
              aria-label="搜索右侧玩家"
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
      <div class="chart-card">
        <div class="chart-card__title">伤害分布（玩家伤害 / 建筑伤害 / 治疗）</div>
        <EChart :option="damagePieOption" :height="380" />
      </div>
    </div>

    <!-- 职业×指标热力图 + 玩家四维构成（并排） -->
    <div class="chart-row">
      <div class="chart-card">
        <div class="chart-card__title">职业×指标热力图</div>
        <EChart :option="heatmapOption" :height="heatmapHeight" />
      </div>
      <div class="chart-card">
        <div class="chart-card__title">玩家四维数据（Top 10）</div>
        <EChart :option="playerBarsOption" :height="320" />
      </div>
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
import { aggregateCamps } from './analysis'
import EChart from './EChart.vue'
import {
  buildDamagePieOption,
  buildHeatmapOption,
  buildPlayerBarsOption,
  buildStackOption,
} from './playerAggregateCharts'
import { buildRadarOption } from './playerRadar'
import {
  buildDmgHealBubbleOption,
  buildHealTakenOption,
  buildKdaScatterOption,
  buildScatterOption,
} from './playerScatterCharts'

const props = defineProps<{ items: MatchData[] }>()

const camps = computed(() => aggregateCamps(props.items))
const allProfs = computed(() => [...new Set(props.items.map((r) => r.profession || '未知'))].sort())

const heatmapHeight = computed(() => Math.max(320, Math.min(480, allProfs.value.length * 28 + 80)))

const scatterOption = computed(() => buildScatterOption(props.items))
const heatmapOption = computed(() => buildHeatmapOption(props.items, allProfs.value))
const healTakenOption = computed(() => buildHealTakenOption(props.items))
const playerBarsOption = computed(() => buildPlayerBarsOption(props.items))

function stackOption(field: 'player_damage' | 'healing') {
  return buildStackOption(props.items, camps.value, allProfs.value, field)
}

// ==================== 玩家维度图表（设计文档 图表13/14/15） ====================

const kdaScatterOption = computed(() => buildKdaScatterOption(props.items))
const dmgHealBubbleOption = computed(() => buildDmgHealBubbleOption(props.items))

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

const radarOption = computed(() => buildRadarOption(props.items, radarLeft.value, radarRight.value))

const damagePieOption = computed(() => buildDamagePieOption(props.items))
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
  flex-wrap: wrap;
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
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .stack-row,
  .chart-row {
    grid-template-columns: 1fr;
  }
}
</style>

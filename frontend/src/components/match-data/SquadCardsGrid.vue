<template>
  <div class="chart-card">
    <div class="chart-card__head">
      <span class="chart-card__title">小队概览</span>
      <div class="card-toolbar">
        <span class="card-toolbar__count">共 {{ squads.length }} 个小队 · {{ totalPlayers }} 人</span>
        <el-tag v-if="adjustedCount" size="small" type="warning" effect="plain">已调整 {{ adjustedCount }} 人</el-tag>
        <el-button v-if="adjustedCount && isAdmin" link type="warning" size="small" @click="$emit('reset-adjustments')">重置调整</el-button>
        <el-checkbox v-model="compareModeProxy" label="对比模式" />
        <el-button
          v-if="compareModeProxy && compareSelectedCount >= 2"
          type="primary"
          size="small"
          @click="$emit('open-compare')"
        >对比所选小队（{{ compareSelectedCount }}）</el-button>
      </div>
    </div>

    <template v-for="group in squadGroups" :key="group.category">
      <div class="squad-group-label">{{ group.category }}</div>
      <div class="squad-row">
        <div
          v-for="s in group.items"
          :key="s.squad_name"
          class="squad-card"
          :class="{ 'squad-card--active': detailSquad === s.squad_name }"
          @click="$emit('open-detail', s.squad_name)"
        >
          <div class="squad-card__header">
            <el-checkbox
              v-if="compareModeProxy"
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
              <span class="metric-label">助攻</span>
              <span class="metric-value num">{{ s.totals.assists }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">重伤</span>
              <span class="metric-value num">{{ s.totals.deaths }}</span>
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
              <span class="metric-label">承伤</span>
              <span class="metric-value num">{{ fmtNum(s.totals.damage_taken) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">治疗</span>
              <span class="metric-value num">{{ fmtNum(s.totals.healing) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">秒伤</span>
              <span class="metric-value num">{{ fmtNum(s.indicators.dps) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">KDA</span>
              <span class="metric-value num">{{ s.indicators.kda.toFixed(2) }}</span>
            </div>
            <div class="metric-item">
              <span class="metric-label">清泉羽化</span>
              <span class="metric-value num">{{ s.totals.revives }}</span>
            </div>
          </div>
          <div class="squad-card__footer">
            <el-button
              v-if="s.squad_name === '未排表' && isAdmin"
              text
              type="warning"
              size="small"
              @click.stop="$emit('open-adjust')"
            >分配成员</el-button>
            <el-button text type="primary" size="small">查看详情 →</el-button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { SquadAnalysis } from '@/types/matchData'

import { fmtNum } from './analysis'

const props = defineProps<{
  squads: SquadAnalysis[]
  totalPlayers: number
  adjustedCount: number
  isAdmin: boolean
  detailSquad: string
  compareMode: boolean
  compareSelectedCount: number
}>()

// 勾选映射由子组件写入（`compareChecked[squad_name] = v`）：声明为 model（W2-8）
const compareChecked = defineModel<Record<string, boolean>>('compareChecked', { required: true })

const emit = defineEmits<{
  'open-detail': [name: string]
  'open-adjust': []
  'reset-adjustments': []
  'open-compare': []
  'update:compareMode': [value: boolean]
}>()

const compareModeProxy = computed({
  get: () => props.compareMode,
  set: (v: boolean) => emit('update:compareMode', v),
})

/** 按 category 分组，保持原始顺序 */
const squadGroups = computed(() => {
  const map = new Map<string, SquadAnalysis[]>()
  for (const s of props.squads) {
    const cat = s.category || '其他'
    if (!map.has(cat)) map.set(cat, [])
    map.get(cat)!.push(s)
  }
  return [...map.entries()].map(([category, items]) => ({ category, items }))
})
</script>

<style scoped>
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

/* ===== 卡片分组（每队一行） ===== */
.squad-group-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-700);
  margin: 10px 0 6px;
  border-left: 3px solid var(--gold-500);
  padding-left: 8px;
}

.squad-group-label:first-of-type {
  margin-top: 0;
}

.squad-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 4px;
}

.squad-card {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 10px 14px;
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
  flex-shrink: 0;
  min-width: 128px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.squad-card__name {
  font-weight: 700;
  font-size: 13px;
  color: var(--ink-800);
  white-space: nowrap;
}

.squad-card__count {
  font-size: 11px;
  color: var(--ink-400);
  white-space: nowrap;
}

.squad-card__metrics {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
  white-space: nowrap;
}

.metric-label {
  font-size: 11px;
  color: var(--ink-400);
}

.metric-value {
  font-size: 13px;
  font-weight: 800;
  color: var(--gold-700);
}

.squad-card__footer {
  flex-shrink: 0;
  text-align: right;
}

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  .chart-card {
    padding: 12px;
  }

  /* 小队卡片：窄屏纵向堆叠，指标自动换行 */
  .squad-card {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .squad-card__header {
    min-width: 0;
  }

  .squad-card__metrics {
    gap: 4px 10px;
  }
}
</style>

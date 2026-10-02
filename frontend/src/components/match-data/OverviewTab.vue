<!-- 行数豁免（连续逻辑）：单场比赛数据总览面板（统计卡/占比条/阵营卡/图表区同源）｜登记见 .agent/rules/file-length-rule.md 豁免清单 -->
<template>
  <div class="overview-tab">
    <!-- 统计卡 -->
    <div class="hero-grid">
      <div v-for="s in heroStats" :key="s.label" class="hero-card">
        <span class="hero-label">{{ s.label }}</span>
        <span class="hero-value num">
          {{ s.format ? s.format(s.value) : s.value.toLocaleString() }}
          <em v-if="s.suffix" class="hero-suffix">{{ s.suffix }}</em>
        </span>
      </div>
    </div>

    <!-- 阵营击杀占比条 -->
    <div v-if="camps.length >= 2" class="kill-bar">
      <div class="kill-bar__track">
        <div
          v-for="(c, i) in camps"
          :key="c.camp"
          class="kill-bar__fill"
          :style="{ width: killPct[i] + '%', background: campColor(i) }"
        />
      </div>
      <div class="kill-bar__labels">
        <span
          v-for="(c, i) in camps"
          :key="c.camp"
          class="kill-bar__label"
          :style="{ color: campColor(i) }"
        >
          {{ c.camp }} {{ killPct[i].toFixed(1) }}%
        </span>
      </div>
      <span class="kill-bar__title">击杀占比</span>
    </div>

    <!-- 阵营卡片：人数 + 职业分布 -->
    <div class="camp-grid">
      <div v-for="(c, i) in camps" :key="c.camp" class="camp-card" :class="`camp-card--${i % 2}`">
        <div class="camp-card__header">
          <i class="camp-card__dot" :style="{ background: campColor(i) }" />
          {{ c.camp }}
          <span class="camp-card__count num">{{ c.player_count }} 人</span>
        </div>
        <div class="camp-card__profs">
          <span v-for="p in campProfs[c.camp] || []" :key="p.prof" class="prof-chip">
            <i class="prof-dot" :style="{ background: profColor(p.prof) }" />
            {{ p.prof }} ×{{ p.count }}
          </span>
          <span v-if="!(campProfs[c.camp] || []).length" class="camp-card__empty">-</span>
        </div>
      </div>
    </div>

    <!-- 图表区块 -->
    <CampCompare :items="items" />
    <PlayerAnalysis :items="items" />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { CampStats, MatchData } from '@/types/matchData'
import { CAMP_COLORS, fmtNum, profColor } from './analysis'
import CampCompare from './CampCompare.vue'
import PlayerAnalysis from './PlayerAnalysis.vue'

const props = defineProps<{ items: MatchData[]; camps: CampStats[] }>()

const heroStats = computed(() => {
  const totalPlayers = props.items.length
  const totalKills = props.items.reduce((s, r) => s + r.kills, 0)
  const totalDamage = props.items.reduce((s, r) => s + r.player_damage, 0)
  const totalHealing = props.items.reduce((s, r) => s + r.healing, 0)
  return [
    { label: '总人数', value: totalPlayers, suffix: '人' },
    { label: '总击杀', value: totalKills, suffix: '' },
    { label: '总伤害', value: totalDamage, suffix: '', format: fmtNum },
    { label: '总治疗', value: totalHealing, suffix: '', format: fmtNum },
  ]
})

/** 阵营击杀占比。 */
const killPct = computed(() => {
  const total = props.camps.reduce((s, c) => s + c.total_kills, 0)
  if (!total || props.camps.length < 2) return props.camps.map(() => 0)
  return props.camps.map((c) => (c.total_kills / total) * 100)
})

/** 各阵营职业分布。 */
const campProfs = computed(() => {
  const map: Record<string, { prof: string; count: number }[]> = {}
  for (const r of props.items) {
    const prof = r.profession || '未知'
    const list = map[r.camp] ?? []
    const hit = list.find((p) => p.prof === prof)
    if (hit) hit.count += 1
    else list.push({ prof, count: 1 })
    map[r.camp] = list
  }
  return map
})

function campColor(i: number) {
  return CAMP_COLORS[i % CAMP_COLORS.length]
}
</script>

<style scoped>
.hero-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
  margin-bottom: 14px;
}

.hero-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px 18px;
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 60%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.hero-label {
  font-size: 12px;
  color: var(--ink-500);
  font-weight: 600;
  letter-spacing: 1px;
}

.hero-value {
  font-size: 28px;
  font-weight: 800;
  color: var(--gold-700);
}

.hero-suffix {
  font-style: normal;
  font-size: 14px;
  color: var(--ink-400);
  margin-left: 2px;
}

/* 击杀占比条 */
.kill-bar {
  margin-bottom: 14px;
  padding: 10px 14px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  background: var(--ink-bg-paper);
}

.kill-bar__track {
  display: flex;
  height: 10px;
  border-radius: var(--radius-xl);
  overflow: hidden;
  background: var(--ink-bg-wash);
}

.kill-bar__fill {
  height: 100%;
  transition: width 0.5s ease;
}

.kill-bar__labels {
  display: flex;
  gap: 16px;
  margin-top: 6px;
  font-size: 12px;
  font-weight: 700;
}

.kill-bar__title {
  float: right;
  font-size: 11px;
  color: var(--ink-400);
}

/* 阵营卡片 */
.camp-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
  margin-bottom: 14px;
}

.camp-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  background: var(--ink-bg-paper);
}

.camp-card--1 {
  border-color: #d5dfe8;
  background: #f7fafd;
}

.camp-card__header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 700;
  color: var(--ink-800);
  font-size: 14px;
}

.camp-card__dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  flex-shrink: 0;
}

.camp-card__count {
  margin-left: auto;
  font-size: 12px;
  color: var(--ink-500);
}

.camp-card__profs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 10px;
}

.camp-card__empty {
  color: var(--ink-300);
  font-size: 12px;
}

.prof-chip {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-700);
  background: var(--ink-bg-cream);
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-xl);
  padding: 1px 9px;
}

.prof-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
  margin-bottom: 14px;
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
  margin-bottom: 10px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .hero-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .hero-card {
    padding: 12px 14px;
  }

  .hero-value {
    font-size: 22px;
  }

  .camp-grid {
    grid-template-columns: 1fr;
  }
}
</style>

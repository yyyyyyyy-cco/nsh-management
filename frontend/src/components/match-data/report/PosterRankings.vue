<!-- 战报区块：高光榜单（击杀/对玩家伤害/治疗/建筑伤害/重伤/总分 TOP3，三列两行） -->
<template>
  <div class="rk">
    <div class="rk-head">高光榜单</div>
    <div class="rk-grid">
      <div v-for="col in columns" :key="col.title" class="rk-col">
        <div class="rk-col-title">{{ col.title }}</div>
        <div v-for="item in col.items" :key="item.player_name" class="rk-item">
          <span class="rk-badge" :class="`rk-badge--${item.rank}`">{{ item.rank }}</span>
          <span class="rk-name" :title="`${item.player_name}（第 ${item.round_no} 局）`">{{ item.player_name }}</span>
          <span v-if="item.profession" class="rk-prof" :style="profTagStyle(item.profession)">{{ item.profession }}</span>
          <span class="rk-value num">{{ fmtNum(item.value) }}</span>
        </div>
        <div v-if="col.items.length === 0" class="rk-empty">暂无数据</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { profTagStyle } from '@/utils/profession'
import { fmtNum } from '../analysis'
import type { ReportRankItem } from '../reportData'

const props = defineProps<{
  kills: ReportRankItem[]
  damage: ReportRankItem[]
  healing: ReportRankItem[]
  building: ReportRankItem[]
  deaths: ReportRankItem[]
  score: ReportRankItem[]
}>()

const columns = computed(() => [
  { title: '击杀榜', items: props.kills },
  { title: '对玩家伤害榜', items: props.damage },
  { title: '治疗榜', items: props.healing },
  { title: '对建筑伤害榜', items: props.building },
  { title: '重伤榜', items: props.deaths },
  { title: '总分榜', items: props.score },
])
</script>

<style scoped>
.rk {
  padding: 20px 40px 6px;
}

.rk-head {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

.rk-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}

.rk-col {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 12px 14px;
}

.rk-col-title {
  font-size: 12.5px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--gold-700);
  margin-bottom: 8px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--edge-faint);
}

.rk-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 0;
}

/* 名次徽章：金银铜，与 RankingTab/ScoreTab 全站统一 */
.rk-badge {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 700;
  color: var(--ink-400);
  background: var(--edge-faint);
}

.rk-badge--1 {
  background: linear-gradient(135deg, #f6c94d, #d4a017);
  color: #fff;
  box-shadow: 0 2px 6px rgba(212, 160, 23, 0.4);
}

.rk-badge--2 {
  background: linear-gradient(135deg, #c9c9c9, #9a9a9a);
  color: #fff;
}

.rk-badge--3 {
  background: linear-gradient(135deg, #e0a877, #b97f4b);
  color: #fff;
}

.rk-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-800);
}

.rk-prof {
  flex-shrink: 0;
  padding: 1px 7px;
  border-radius: var(--radius-xl);
  font-size: 10.5px;
  font-weight: 600;
  line-height: 1.6;
}

.rk-value {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 700;
  color: var(--gold-700);
}

.rk-empty {
  padding: 10px 0;
  text-align: center;
  font-size: 12px;
  color: var(--ink-400);
}

/* finesse · register=product · shell=match-report-poster: 六榜 TOP3（960px 固定宽，三列两行，导出用不响应式） */
</style>

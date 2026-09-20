<!-- 单场图文战报海报（960px 固定设计宽，html2canvas 导出用，内部不响应式） -->
<template>
  <div class="poster">
    <PosterHeader
      :schedule="schedule"
      :imported-rounds="data.importedRounds"
      :rounds="data.rounds"
      :player-count="data.playerCount"
      :record-count="data.recordCount"
    />
    <PosterOverview :stats="data.overview" />
    <PosterMvpKings :mvp="data.mvp" :kings="data.kings" />
    <PosterRankings
      :kills="data.killsTop"
      :damage="data.damageTop"
      :healing="data.healingTop"
      :building="data.buildingTop"
      :deaths="data.deathsTop"
      :score="data.scoreTop"
    />
    <PosterRounds :rounds-info="data.roundsInfo" />
    <PosterSquads :squads="data.squads" />
    <div class="poster-footer">轻衫都会用的帮会联赛管理系统 · 生成于 {{ genDate }}</div>
  </div>
</template>

<script setup lang="ts">
import dayjs from 'dayjs'

import type { ScheduleInfo } from '@/types/schedule'
import PosterHeader from './PosterHeader.vue'
import PosterMvpKings from './PosterMvpKings.vue'
import PosterOverview from './PosterOverview.vue'
import PosterRankings from './PosterRankings.vue'
import PosterRounds from './PosterRounds.vue'
import PosterSquads from './PosterSquads.vue'
import type { MatchReportData } from '../reportData'

defineProps<{
  data: MatchReportData
  schedule: ScheduleInfo | null
}>()

const genDate = dayjs().format('YYYY-MM-DD')
</script>

<style scoped>
.poster {
  width: 960px;
  /* 宣纸底：与全站页面背景令牌一致；html2canvas backgroundColor 同步为 #f7f3ea */
  background: var(--ink-bg-page);
  color: var(--ink-800);
}

.poster-footer {
  margin-top: 22px;
  padding: 12px 40px 18px;
  border-top: 1px solid var(--edge-faint);
  text-align: center;
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--ink-400);
}

/* finesse · register=product · shell=match-report-poster: 海报根容器 960px 固定宽（导出原尺寸，不做响应式） */
</style>

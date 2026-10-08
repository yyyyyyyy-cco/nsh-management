<!-- 战报区块：头部（帮会名 + 战报标题 + 对局信息 + 各局结果） -->
<template>
  <div class="ph">
    <div class="ph-topline" />
    <div class="ph-brand">
      <span class="ph-guild">{{ guildName }}</span>
      <span class="ph-title">联赛战报</span>
      <span class="ph-date">{{ dateText }}</span>
    </div>
    <div class="ph-match">
      <div class="ph-opponent">
        <span class="ph-vs">VS</span>
        <span class="ph-opponent-name" :title="schedule?.opponent || ''">{{ schedule?.opponent || '未知对手' }}</span>
      </div>
      <el-tag :type="resultType(schedule?.result || 'pending')" effect="light" size="large">
        {{ resultLabel(schedule?.result || 'pending') }}
      </el-tag>
    </div>
    <div class="ph-sub">
      <span>{{ timeText }}</span>
      <span v-if="rounds > 1" class="ph-sub-item">已导入 {{ importedRounds.length }}/{{ rounds }} 局</span>
      <span class="ph-sub-item">参战 {{ playerCount }} 人</span>
      <span class="ph-sub-item">累计 {{ recordCount }} 人次</span>
    </div>
    <div v-if="roundResults.length" class="ph-rounds">
      <el-tag
        v-for="(r, index) in roundResults"
        :key="index"
        :type="resultType(r)"
        effect="light"
        size="small"
        class="ph-round-tag"
      >
        第{{ index + 1 }}局 {{ resultLabel(r) }}
      </el-tag>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'

import { useAuthStore } from '@/stores/auth'
import type { ScheduleInfo } from '@/types/schedule'
import { resultLabel, resultType } from '@/utils/constants'

const props = defineProps<{
  schedule: ScheduleInfo | null
  importedRounds: number[]
  rounds: number
  playerCount: number
  recordCount: number
}>()

const auth = useAuthStore()

const guildName = computed(() => auth.user?.guild_name || '帮会')
const dateText = computed(() => (props.schedule ? dayjs(props.schedule.match_time).format('YYYY-MM-DD') : ''))
const timeText = computed(() => (props.schedule ? dayjs(props.schedule.match_time).format('YYYY-MM-DD HH:mm') : ''))
const roundResults = computed(() => (props.schedule?.round_results || []).filter((r) => r && r !== 'pending'))
</script>

<style scoped>
.ph {
  border-bottom: 1px solid var(--gold-200);
}

.ph-topline {
  height: 6px;
  background: var(--gold-gradient);
}

.ph-brand {
  display: flex;
  align-items: baseline;
  gap: 14px;
  padding: 22px 40px 0;
}

.ph-guild {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 1px;
  color: var(--ink-600);
}

.ph-title {
  font-family: var(--font-serif);
  font-size: 26px;
  font-weight: 700;
  letter-spacing: 6px;
  color: var(--ink-900);
}

.ph-date {
  margin-left: auto;
  font-size: 12.5px;
  color: var(--ink-400);
}

.ph-match {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 10px 40px 0;
}

.ph-opponent {
  display: flex;
  align-items: baseline;
  gap: 10px;
  min-width: 0;
}

.ph-vs {
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--gold-600);
}

.ph-opponent-name {
  font-size: 22px;
  font-weight: 700;
  color: var(--ink-900);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ph-sub {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 40px 0;
  font-size: 12.5px;
  color: var(--ink-500);
}

.ph-sub-item {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.ph-sub-item::before {
  content: '';
  width: 3px;
  height: 3px;
  border-radius: 50%;
  background: var(--gold-400);
}

.ph-rounds {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 40px 18px;
}

/* finesse · register=product · shell=match-report-poster: 战报头部（960px 固定宽，导出用不响应式） */
</style>

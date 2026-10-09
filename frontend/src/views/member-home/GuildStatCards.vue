<!-- 帮众首页·战绩统计卡：已赛场次 / 近10局战绩 / 局胜率 / 录屏完成 -->
<template>
  <div class="stat-grid">
    <div v-for="card in cards" :key="card.key" class="stat-card" :class="`stat-card--${card.theme}`" :title="card.hint">
      <div class="stat-card__header">
        <span class="stat-card__label">{{ card.label }}</span>
        <el-icon class="stat-card__icon"><component :is="card.icon" /></el-icon>
      </div>
      <div class="stat-card__value">
        <span class="stat-card__number" :class="{ num: card.numeric }">{{ card.display }}</span>
        <span v-if="card.suffix" class="stat-card__suffix">{{ card.suffix }}</span>
      </div>
      <div class="stat-card__track" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, TrendCharts, Trophy, VideoCamera } from '@element-plus/icons-vue'

import type { GuildStats } from './types'

const props = defineProps<{ stats: GuildStats }>()

const cards = computed(() => [
  {
    key: 'played',
    label: '已赛场次',
    icon: Calendar,
    theme: 'primary',
    numeric: true,
    display: props.stats.playedCount,
    suffix: '场',
    hint: '全部已结束的比赛',
  },
  {
    key: 'record',
    label: '近10局战绩',
    icon: Trophy,
    theme: 'gold',
    numeric: false,
    display: props.stats.recentRecord,
    suffix: '',
    hint: '最近 10 局已出结果的胜/平/负（跨场次，一场可含多局）',
  },
  {
    key: 'rate',
    label: '局胜率',
    icon: TrendCharts,
    theme: 'success',
    numeric: true,
    display: props.stats.roundWinRate != null ? props.stats.roundWinRate : '-',
    suffix: props.stats.roundWinRate != null ? '%' : '',
    hint: '近 5 场已出结果局的胜率',
  },
  {
    key: 'recording',
    label: '录屏完成',
    icon: VideoCamera,
    theme: 'warning',
    numeric: true,
    display: props.stats.recordingRate != null ? props.stats.recordingRate : '-',
    suffix: props.stats.recordingRate != null ? '%' : '',
    hint: '最近一场录屏已交占比（已通过 + 待审）',
  },
])
</script>

<style scoped>
/* finesse · register=product · shell=member-home: 战绩统计卡（与管理员首页统计卡同语言：浅金图标底 + 渐变数字 + 底部金条） */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 16px 18px 14px;
  box-shadow: var(--shadow-sm);
  transition:
    transform var(--dur-normal) var(--ease-out),
    box-shadow var(--dur-normal) var(--ease-out);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

.stat-card__track {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 3px;
  background: var(--gold-line);
  opacity: 0.85;
}

.stat-card__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.stat-card__label {
  font-size: 13px;
  color: var(--ink-400);
}

.stat-card__icon {
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: var(--gold-600);
  background: var(--gold-50);
}

.stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
  min-width: 0;
}

.stat-card__number {
  font-size: 28px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #d9b64a 0%, #c9a13b 55%, #b18c2c 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  overflow-wrap: anywhere;
}

.stat-card--success .stat-card__number {
  background: linear-gradient(135deg, #4da87b 0%, #2e8b57 60%, #3d9d6d 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.stat-card--warning .stat-card__number {
  background: linear-gradient(135deg, #e2a33d 0%, #d97706 60%, #c26a05 100%);
  -webkit-background-clip: text;
  background-clip: text;
}

.stat-card__suffix {
  font-size: 13px;
  color: var(--ink-400);
}

@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
  }
}

@media (max-width: 480px) {
  .stat-grid {
    gap: 10px;
  }

  .stat-card {
    padding: 14px 14px 12px;
  }

  .stat-card__number {
    font-size: 23px;
  }
}
</style>

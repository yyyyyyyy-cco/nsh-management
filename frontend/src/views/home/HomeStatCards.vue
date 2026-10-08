<template>
  <div class="stat-grid">
    <div
      v-for="(card, i) in statCards"
      :key="card.key"
      class="stat-card"
      :class="`stat-card--${card.theme}`"
      :style="{ animationDelay: `${i * 60}ms` }"
    >
      <div class="stat-card__header">
        <span class="stat-card__label">{{ card.label }}</span>
        <el-icon class="stat-card__icon"><component :is="card.icon" /></el-icon>
      </div>
      <div class="stat-card__value">
        <span v-if="loading" class="sk sk-kpi" />
        <span v-else-if="card.numeric" class="stat-card__number num">{{ card.display }}</span>
        <span v-else class="stat-card__number num">{{ card.value }}</span>
        <span class="stat-card__suffix">{{ card.suffix }}</span>
      </div>
      <div class="stat-card__track" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Calendar, TrendCharts, Trophy, UserFilled } from '@element-plus/icons-vue'

import { useCountUp } from '@/composables/useCountUp'

const props = defineProps<{
  loading: boolean
  memberCount: number
  scheduleCount: number
  topName: string
  topRate: number | null | undefined
}>()

/** 数字滚动 */
const animatedMemberCount = useCountUp(computed(() => props.memberCount))
const animatedScheduleCount = useCountUp(computed(() => props.scheduleCount))
const animatedTopRate = useCountUp(
  computed(() => props.topRate),
  { decimals: 0 },
)

const statCards = computed(() => {
  const rate = props.topRate
  return [
    {
      key: 'members',
      label: '帮众总数',
      value: props.memberCount,
      suffix: '人',
      icon: UserFilled,
      theme: 'primary',
      numeric: true,
      display: animatedMemberCount.value,
    },
    {
      key: 'matches',
      label: '历史比赛',
      value: props.scheduleCount,
      suffix: '场',
      icon: Calendar,
      theme: 'gold',
      numeric: true,
      display: animatedScheduleCount.value,
    },
    {
      key: 'top',
      label: '出勤之星',
      value: props.topName,
      suffix: '',
      icon: Trophy,
      theme: 'success',
      numeric: false,
      display: '',
    },
    {
      key: 'rate',
      label: '最高出勤',
      value: rate != null ? Math.round(rate * 100) : '-',
      suffix: rate != null ? '%' : '',
      icon: TrendCharts,
      theme: 'warning',
      numeric: rate != null,
      display: rate != null ? Math.round(animatedTopRate.value * 100) : '-',
    },
  ]
})
</script>

<style scoped>
/* ===== 统计卡片 ===== */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  position: relative;
  overflow: hidden;
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 18px 20px 16px;
  box-shadow: var(--shadow-sm);
  animation: stat-pop 0.4s var(--ease-out) both;
  transition:
    transform var(--dur-normal) var(--ease-out),
    box-shadow var(--dur-normal) var(--ease-out);
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
}

/* 卡片底部渐变条 */
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
  margin-bottom: 12px;
}

.stat-card__label {
  font-size: 13px;
  color: var(--ink-400);
}

.stat-card__icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 17px;
  background: var(--gold-50);
}

.stat-card__value {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.stat-card__number {
  font-size: 30px;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, #d9b64a 0%, #c9a13b 55%, #b18c2c 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stat-card__suffix {
  font-size: 13px;
  color: var(--ink-400);
  font-weight: 400;
}

.stat-card--success .stat-card__number {
  background: linear-gradient(135deg, #4da87b 0%, #2e8b57 60%, #3d9d6d 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.stat-card--warning .stat-card__number {
  background: linear-gradient(135deg, #e2a33d 0%, #d97706 60%, #c26a05 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

/* ===== 响应式 ===== */
@media (max-width: 900px) {
  .stat-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .stat-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 10px;
  }

  .stat-card {
    padding: 14px 14px 12px;
  }

  .stat-card__number {
    font-size: 24px;
  }
}
</style>

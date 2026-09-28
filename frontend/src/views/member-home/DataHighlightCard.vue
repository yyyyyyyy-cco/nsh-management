<!-- 帮众首页·数据亮点：最近一场 MVP 与数据之王（与「生成战报」同源数据） -->
<template>
  <div class="card">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><Trophy /></el-icon>
        <span class="card__title">数据亮点</span>
      </div>
      <span v-if="data" class="card__subtitle">vs {{ data.opponent }} · {{ data.dateText }}</span>
    </div>
    <div class="card__body">
      <!-- 加载中：骨架 -->
      <div v-if="!ready" class="hl-skeleton">
        <div class="sk sk-block" style="height:84px;border-radius:var(--radius-md)" />
        <div class="sk sk-block" style="height:150px;border-radius:var(--radius-md)" />
      </div>

      <!-- 无数据 -->
      <EmptyState v-else-if="!data" variant="chart" description="最近暂无比赛数据" :image-size="64" />

      <template v-else>
        <!-- MVP 金卡 -->
        <div v-if="data.mvp" class="mvp-block">
          <span class="mvp-block__badge">MVP</span>
          <div class="mvp-block__main">
            <span class="mvp-block__name">{{ data.mvp.player_name }}</span>
            <span class="mvp-block__sub">
              第{{ data.mvp.round_no }}局 · 综合 {{ data.mvp.score }} 分 · KDA {{ data.mvp.kda }}
            </span>
          </div>
        </div>

        <!-- 数据之王六格 -->
        <div class="kings-grid">
          <div v-for="k in data.kings" :key="k.label" class="king-cell">
            <span class="king-cell__label">{{ k.label }}</span>
            <span class="king-cell__name">{{ k.player_name }}</span>
            <span class="king-cell__value num">{{ fmtNum(k.value) }}</span>
          </div>
        </div>

        <div class="hl-foot">
          <el-button link type="primary" @click="goAnalysis(data.scheduleId)">
            查看完整分析 <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { ArrowRight, Trophy } from '@element-plus/icons-vue'

import { fmtNum } from '@/components/match-data/analysis'
import EmptyState from '@/components/common/EmptyState.vue'
import type { HighlightData } from './types'

defineProps<{ data: HighlightData | null; ready: boolean }>()

const router = useRouter()

function goAnalysis(scheduleId: number) {
  router.push({ name: 'schedule-detail', params: { id: scheduleId }, query: { tab: 'analysis', from: 'home' } })
}
</script>

<style scoped src="./card-shared.css"></style>

<style scoped>
/* finesse · register=product · shell=member-home: 数据亮点（MVP 金卡 + 数据之王六格，导出/长名不溢出） */
.hl-skeleton {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* ===== MVP 金卡 ===== */
.mvp-block {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius-md);
  background: linear-gradient(135deg, var(--gold-100) 0%, var(--gold-50) 100%);
  border: 1px solid var(--gold-200);
}

.mvp-block__badge {
  flex-shrink: 0;
  padding: 3px 10px;
  border-radius: var(--radius-xl);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 1px;
  color: #fff;
  background: var(--gold-gradient);
}

.mvp-block__main {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mvp-block__name {
  font-size: 16px;
  font-weight: 700;
  color: var(--ink-900);
  overflow-wrap: anywhere;
}

.mvp-block__sub {
  font-size: 12px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

/* ===== 数据之王六格 ===== */
.kings-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin-top: 10px;
}

.king-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 8px 10px;
  border-radius: var(--radius-md);
  background: var(--ink-bg-wash);
  border: 1px solid var(--edge-faint);
}

.king-cell__label {
  font-size: 11px;
  color: var(--ink-400);
}

.king-cell__name {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-900);
  overflow-wrap: anywhere;
}

.king-cell__value {
  font-size: 12px;
  font-weight: 700;
  color: var(--gold-700);
}

.hl-foot {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>

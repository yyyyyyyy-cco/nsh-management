<!-- 战报区块：全场 MVP（金卡）+ 数据之王（六格） -->
<template>
  <div class="mk">
    <div class="mk-head">MVP 与数据之王</div>

    <!-- MVP 金卡：评分最高者（标注所属局） -->
    <div v-if="mvp" class="mk-mvp">
      <span class="mk-mvp__badge">MVP</span>
      <span class="mk-mvp__name">{{ mvp.player_name }}</span>
      <span v-if="mvp.profession" class="mk-mvp__prof" :style="profTagStyle(mvp.profession)">{{ mvp.profession }}</span>
      <span class="mk-mvp__round">第 {{ mvp.round_no }} 局</span>
      <span class="mk-mvp__stats">
        <span class="mk-stat"><b class="num">{{ mvp.score }}</b><i>评分</i></span>
        <span class="mk-stat"><b class="num">{{ mvp.kda.toFixed(1) }}</b><i>KDA</i></span>
        <span class="mk-stat"><b class="num">{{ mvp.kills }}</b><i>击杀</i></span>
        <span class="mk-stat"><b class="num">{{ fmtNum(mvp.playerDamage) }}</b><i>伤害</i></span>
      </span>
    </div>

    <!-- 数据之王：六项全场最佳单局 -->
    <div class="mk-kings">
      <div v-for="k in kings" :key="k.label" class="king">
        <div class="king__label">{{ k.label }}</div>
        <div class="king__name">
          <i v-if="k.profession" class="king__dot" :style="{ background: profColor(k.profession) }" />
          <span :title="`${k.player_name}（第 ${k.round_no} 局）`">{{ k.player_name }}</span>
        </div>
        <div class="king__value num">{{ fmtNum(k.value) }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { profColor, profTagStyle } from '@/utils/profession'
import { fmtNum } from '../analysis'
import type { ReportKingItem, ReportMvp } from '../reportData'

defineProps<{
  mvp: ReportMvp | null
  kings: ReportKingItem[]
}>()
</script>

<style scoped>
.mk {
  padding: 20px 40px 6px;
}

.mk-head {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

/* ===== MVP 金卡 ===== */
.mk-mvp {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 18px;
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 70%);
  margin-bottom: 12px;
}

.mk-mvp__badge {
  flex-shrink: 0;
  padding: 3px 12px;
  border-radius: var(--radius-xl);
  background: var(--gold-gradient);
  color: #fff;
  font-size: 12.5px;
  font-weight: 800;
  letter-spacing: 2px;
}

.mk-mvp__name {
  font-size: 18px;
  font-weight: 700;
  color: var(--ink-900);
}

.mk-mvp__prof {
  flex-shrink: 0;
  padding: 1px 8px;
  border-radius: var(--radius-xl);
  font-size: 11px;
  font-weight: 600;
  line-height: 1.7;
}

.mk-mvp__round {
  font-size: 12px;
  color: var(--ink-400);
}

.mk-mvp__stats {
  margin-left: auto;
  display: inline-flex;
  gap: 24px;
}

.mk-stat {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.mk-stat b {
  font-size: 17px;
  font-weight: 800;
  color: var(--gold-700);
}

.mk-stat i {
  font-style: normal;
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--ink-500);
}

/* ===== 数据之王六格 ===== */
.mk-kings {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
}

.king {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 10px 8px;
  text-align: center;
}

.king__label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--gold-700);
}

.king__name {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-top: 6px;
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-800);
}

.king__name span {
  max-width: 108px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.king__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.king__value {
  margin-top: 4px;
  font-size: 14px;
  font-weight: 800;
  color: var(--ink-900);
}

/* finesse · register=product · shell=match-report-poster: MVP 金卡 + 数据之王六格（960px 固定宽，导出用不响应式） */
</style>

<!-- 战报区块：逐局战况（每局结果 + 我方击杀/伤害/治疗 + 该局 MVP/击杀王/重伤第一） -->
<template>
  <div class="rd">
    <div class="rd-head">逐局战况</div>
    <div v-for="info in roundsInfo" :key="info.roundNo" class="rd-round">
      <div class="rd-main">
        <span class="rd-no">第 {{ info.roundNo }} 局</span>
        <el-tag v-if="info.result" :type="resultType(info.result)" effect="light" size="small">
          {{ resultLabel(info.result) }}
        </el-tag>
        <span v-else class="rd-unknown">结果待定</span>
        <span v-if="info.hasData && info.team" class="rd-stats">
          击杀 <b class="num">{{ info.team.kills }}</b>
          <i>·</i>
          伤害 <b class="num">{{ fmtNum(info.team.playerDamage) }}</b>
          <i>·</i>
          治疗 <b class="num">{{ fmtNum(info.team.healing) }}</b>
        </span>
        <span v-else class="rd-empty">该局数据未导入</span>
      </div>
      <div v-if="info.hasData" class="rd-sub">
        <span v-if="info.mvp" class="rd-item">MVP <b>{{ info.mvp.player_name }}</b> <i>{{ info.mvp.score }} 分</i></span>
        <span v-if="info.killKing" class="rd-item">击杀王 <b>{{ info.killKing.player_name }}</b> <i>{{ info.killKing.kills }} 杀</i></span>
        <span v-if="info.deathKing" class="rd-item">重伤第一 <b>{{ info.deathKing.player_name }}</b> <i>{{ info.deathKing.deaths }} 次</i></span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { resultLabel, resultType } from '@/utils/constants'
import { fmtNum } from '../analysis'
import type { ReportRoundInfo } from '../reportData'

defineProps<{ roundsInfo: ReportRoundInfo[] }>()
</script>

<style scoped>
.rd {
  padding: 20px 40px 6px;
}

.rd-head {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

.rd-round {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 10px 16px;
}

.rd-round + .rd-round {
  margin-top: 8px;
}

.rd-main {
  display: flex;
  align-items: center;
  gap: 10px;
}

.rd-no {
  font-size: 13.5px;
  font-weight: 700;
  letter-spacing: 1px;
  color: var(--ink-800);
}

.rd-unknown,
.rd-empty {
  font-size: 12px;
  color: var(--ink-400);
}

.rd-stats {
  margin-left: auto;
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  font-size: 12.5px;
  color: var(--ink-500);
}

.rd-stats b {
  font-size: 14px;
  font-weight: 800;
  color: var(--ink-900);
}

.rd-stats i {
  font-style: normal;
  color: var(--gold-500);
}

.rd-sub {
  display: flex;
  flex-wrap: wrap; /* 三项高光（MVP/击杀王/重伤第一）遇长名自动换行，避免溢出导出宽度 */
  gap: 6px 20px;
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px dashed var(--edge-soft);
  font-size: 12px;
  color: var(--ink-500);
}

.rd-item b {
  font-weight: 700;
  color: var(--gold-700);
}

.rd-item i {
  font-style: normal;
  margin-left: 2px;
  color: var(--ink-400);
}

/* finesse · register=product · shell=match-report-poster: 逐局战况卡（960px 固定宽，导出用不响应式） */
</style>

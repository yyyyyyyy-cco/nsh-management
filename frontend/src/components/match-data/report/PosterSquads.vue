<!-- 战报区块：小队战况（按排表归属聚合我方各队击杀/对玩家伤害/治疗；无排表时不出区块） -->
<template>
  <div v-if="squads.length" class="sq">
    <div class="sq-head">小队战况</div>
    <div class="sq-list">
      <div class="sq-row sq-row--colhead">
        <span>小队</span>
        <span>击杀</span>
        <span>助攻</span>
        <span>对玩家伤害</span>
        <span>对建筑伤害</span>
        <span>治疗</span>
        <span>承伤</span>
        <span>焚骨</span>
      </div>
      <div v-for="s in squads" :key="s.name" class="sq-row">
        <span class="sq-name" :class="{ 'sq-name--free': s.name === '未排表' }" :title="s.name">{{ s.name }}</span>
        <span class="sq-kill num">{{ s.kills }}</span>
        <span class="sq-num num">{{ s.assists }}</span>
        <span class="sq-num num">{{ fmtNum(s.playerDamage) }}</span>
        <span class="sq-num num">{{ fmtNum(s.buildingDamage) }}</span>
        <span class="sq-num num">{{ fmtNum(s.healing) }}</span>
        <span class="sq-num num">{{ fmtNum(s.damageTaken) }}</span>
        <span class="sq-num num">{{ fmtNum(s.fenGu) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { fmtNum } from '../analysis'
import type { ReportSquadItem } from '../reportData'

defineProps<{ squads: ReportSquadItem[] }>()
</script>

<style scoped>
.sq {
  padding: 20px 40px 6px;
}

.sq-head {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  letter-spacing: 2px;
  color: var(--ink-700);
  margin-bottom: 12px;
}

.sq-list {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 4px 16px 8px;
}

.sq-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 52px 52px 88px 88px 80px 80px 80px;
  align-items: center;
  gap: 8px;
  padding: 6px 0;
  border-bottom: 1px dashed var(--edge-faint);
}

.sq-row:last-child {
  border-bottom: none;
}

.sq-row--colhead {
  padding: 10px 0 6px;
  border-bottom: 1px solid var(--edge-soft);
  font-size: 11px;
  letter-spacing: 1px;
  color: var(--ink-400);
}

/* 数据列统一右对齐（首列队名左对齐；表头行同规则，保证表头与数据逐列对齐） */
.sq-row > span:not(:first-child) {
  text-align: right;
}

.sq-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-800);
}

.sq-name--free {
  font-weight: 400;
  color: var(--ink-500);
}

.sq-kill {
  font-size: 13.5px;
  font-weight: 800;
  color: var(--gold-700);
}

.sq-num {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-700);
}

/* finesse · register=product · shell=match-report-poster: 小队战况列表（960px 固定宽，导出用不响应式） */
</style>

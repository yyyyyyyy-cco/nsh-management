<template>
  <div class="og-group" :class="`og-group--${group.type}`">
    <div class="og-group__header">
      <span class="og-group__dot" />
      <span class="og-group__label">{{ group.label }}</span>
      <span v-if="groupsRemark[group.category]" class="og-group__remark" :title="groupsRemark[group.category]">{{ groupsRemark[group.category] }}</span>
      <span class="og-group__meta">{{ group.teams.length }}队</span>
    </div>
    <div class="og-teams">
      <div v-for="team in group.teams" :key="team.category + team.team_index" class="og-team">
        <div class="og-team__header">{{ team.category }} {{ team.team_index + 1 }} 队</div>
        <div v-for="(slot, si) in team.slots" :key="si" class="og-slot">
          <template v-if="slot.member_name">
            <span class="og-slot__dot" :style="{ background: profColor(slot.profession) }" />
            <span class="og-slot__name">{{ slot.member_name }}</span>
            <span v-if="slot.remark" class="og-slot__remark" :title="slot.remark">{{ slot.remark }}</span>
          </template>
          <span v-else class="og-slot__empty">—</span>
        </div>
        <div class="og-team__footer" :class="footerClass(team)">{{ filledCount(team) }}/6</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LineupTeam } from '@/types/lineup'
import { profColor } from '@/utils/profession'

defineProps<{
  group: { category: string; label: string; type: string; teams: LineupTeam[] }
  groupsRemark: Record<string, string>
}>()

function filledCount(team: LineupTeam): number {
  return team.slots.filter((s) => s.member_name).length
}

function footerClass(team: LineupTeam): string {
  const n = filledCount(team)
  return n === 6 ? 'is-full' : n > 0 ? 'is-partial' : 'is-empty'
}
</script>

<style scoped>
/* ===== 分组卡片 ===== */
.og-group {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--ink-bg-paper);
}

.og-group--attack {
  border-color: var(--gold-200);
}

.og-group--defense {
  border-color: #d5dfe8;
}

.og-group__header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: var(--gold-50);
  border-bottom: 1px solid var(--gold-100);
}

.og-group--defense .og-group__header {
  background: #eef3f8;
  border-bottom-color: #dde6ee;
}

.og-group__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--gold-gradient);
}

.og-group--defense .og-group__dot {
  background: linear-gradient(135deg, #7b9cc0, var(--indigo));
}

.og-group__label {
  font-weight: 700;
  font-size: 13px;
  color: var(--gold-700);
  letter-spacing: 1px;
  white-space: nowrap;
  flex-shrink: 0;
}

.og-group--defense .og-group__label {
  color: var(--indigo);
}

.og-group__meta {
  margin-left: auto;
  font-size: 11px;
  color: var(--ink-400);
  white-space: nowrap;
  flex-shrink: 0;
}

.og-group__remark {
  font-size: 10px;
  font-weight: 500;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 0 6px;
  max-width: 320px;
  min-width: 0;
  flex-shrink: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.8;
}

.og-teams {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 12px 14px;
}

.og-team {
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--ink-bg-cream);
}

.og-team__header {
  text-align: center;
  font-size: 11.5px;
  font-weight: 700;
  color: var(--ink-600);
  padding: 5px 0;
  background: var(--ink-bg-wash);
  border-bottom: 1px solid var(--edge-faint);
}

.og-slot {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 26px;
  padding: 3px 8px;
  border-bottom: 1px solid var(--edge-faint);
  font-size: 12px;
}

.og-slot:last-of-type {
  border-bottom: none;
}

.og-slot__dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.og-slot__name {
  font-weight: 600;
  color: var(--ink-800);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
  flex-shrink: 1;
}

.og-slot__remark {
  margin-left: auto;
  flex-shrink: 10; /* 空间不足时优先折叠备注（10:1 收缩），保证姓名完整 */
  min-width: 0;
  font-size: 10.5px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 0 6px;
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.og-slot__empty {
  width: 100%;
  text-align: center;
  color: var(--ink-300);
}

.og-team__footer {
  text-align: center;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 0;
}

.og-team__footer.is-full {
  color: var(--jade);
  background: var(--el-color-success-light-9);
}

.og-team__footer.is-partial {
  color: var(--ochre);
  background: var(--el-color-warning-light-9);
}

.og-team__footer.is-empty {
  color: var(--ink-300);
  background: var(--ink-bg-wash);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .og-teams {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 10px 12px;
  }

  .og-group__remark {
    max-width: 140px; /* 窄屏限制备注宽度，避免挤压标题与队数标签 */
  }

  .og-slot__remark {
    max-width: 88px; /* 窄屏提前触发备注折叠，让位给姓名 */
  }
}

@media (max-width: 480px) {
  .og-teams {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

<template>
  <div class="stats-bar">
    <div class="stat">
      <span class="label">总人数</span>
      <span class="value num">{{ stats.total }}</span>
    </div>
    <div class="stat-sep" />
    <div class="stat">
      <span class="label">正常</span>
      <span class="value normal num">{{ stats.normal_count }}</span>
    </div>
    <div class="stat-sep" />
    <div class="stat">
      <span class="label">请假</span>
      <span class="value leave num">{{ stats.leave_count }}</span>
    </div>
    <div class="stat-sep" />
    <div class="stat">
      <span class="label">缺口（60 人上限）</span>
      <span class="value num" :class="{ warn: stats.gap > 0 }">{{ stats.gap }}</span>
    </div>
  </div>

  <!-- 职业缺口分析（配置目标 vs 当前出勤）；目标默认沿用系统配置，管理员可单场覆盖 -->
  <div v-if="isAdmin || hasGapTarget" class="gap-bar">
    <template v-if="hasGapTarget">
      <span class="gap-bar__label">职业缺口</span>
      <span
        v-for="g in professionGap"
        :key="g.profession"
        class="gap-chip"
        :class="{ need: g.gap > 0, full: g.gap === 0, surplus: g.gap < 0 }"
      >
        {{ g.profession }}
        <template v-if="g.gap > 0">缺{{ g.gap }}</template>
        <template v-else-if="g.gap < 0">多{{ -g.gap }}</template>
        <template v-else>已满</template>
      </span>
    </template>
    <div v-if="isAdmin" class="gap-bar__actions">
      <el-tag v-if="customConfig" size="small" type="warning" effect="plain">已自定义</el-tag>
      <button class="gap-chip need gap-chip--action" @click="$emit('open-config')">修改职业配置</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { AttendanceStats } from '@/types/attendance'

defineProps<{
  stats: AttendanceStats
  hasGapTarget: boolean
  professionGap: { profession: string; target: number; current: number; gap: number }[]
  customConfig: Record<string, number> | null
  isAdmin: boolean
}>()

defineEmits<{ 'open-config': [] }>()
</script>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 14px 20px;
  background: linear-gradient(135deg, var(--gold-50) 0%, var(--ink-bg-paper) 60%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-lg);
  margin-bottom: 14px;
  box-shadow: var(--shadow-sm);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.stat-sep {
  width: 1px;
  height: 30px;
  background: linear-gradient(180deg, transparent, var(--gold-300), transparent);
}

.label {
  font-size: 12px;
  color: var(--ink-500);
}

.value {
  font-size: 22px;
  font-weight: 800;
  color: var(--gold-700);
}

.value.normal {
  color: var(--jade);
}

.value.leave {
  color: var(--ochre);
}

.value.warn {
  color: var(--cinnabar);
}

/* ===== 职业缺口条 ===== */
.gap-bar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  padding: 10px 14px;
  margin-bottom: 12px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  background: var(--ink-bg-wash);
}

.gap-bar__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
  margin-right: 4px;
}

.gap-bar__actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.gap-chip {
  font-size: 12px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-xl);
  padding: 1px 9px;
  color: var(--ink-400);
}

.gap-chip.need {
  font-weight: 700;
  color: var(--gold-700);
  border-color: var(--gold-300);
  background: var(--gold-50);
}

.gap-chip.full {
  color: var(--ink-300);
}

.gap-chip.surplus {
  font-weight: 700;
  color: var(--jade);
  border-color: var(--jade);
}

/* 与缺口标签同款的药丸按钮（置于 chip 样式后以便 hover 覆盖） */
.gap-chip--action {
  font-family: inherit;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.gap-chip--action:hover {
  background: var(--gold-100);
  border-color: var(--gold-400);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .stats-bar {
    flex-wrap: wrap;
    gap: 10px 16px;
    padding: 12px 14px;
  }

  .stat {
    flex: 1 1 calc(50% - 16px);
    min-width: 0;
  }

  .stat-sep {
    display: none;
  }
}

@media (max-width: 480px) {
  .value {
    font-size: 19px;
  }

  .gap-bar__label {
    flex-basis: 100%;
  }

  .stats-bar .label {
    font-size: 11px;
  }

  .stats-bar {
    padding: 10px 12px;
    gap: 8px 12px;
  }

  /* 职业缺口操作区域在极窄屏撑满换行 */
  .gap-bar__actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>

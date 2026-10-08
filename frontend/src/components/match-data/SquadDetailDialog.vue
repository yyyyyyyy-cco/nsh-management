<template>
  <el-dialog
    v-model="visible"
    :title="name + ' · 成员明细'"
    width="88%"
    top="3vh"
    destroy-on-close
    class="detail-dialog"
  >
    <div v-if="squad" class="detail-body">
      <!-- 小队汇总徽标栏 -->
      <div class="squad-summary-bar">
        <div class="summary-item">
          <span class="s-label">人数</span><b class="s-value">{{ squad.totals.player_count }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">总击杀</span><b class="s-value num">{{ squad.totals.kills }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">总伤害</span><b class="s-value num">{{ fmtNum(squad.totals.player_damage) }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">总塔伤</span><b class="s-value num">{{ fmtNum(squad.totals.building_damage) }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">总治疗</span><b class="s-value num">{{ fmtNum(squad.totals.healing) }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">均KDA</span><b class="s-value num">{{ squad.indicators.kda.toFixed(2) }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">均秒伤</span><b class="s-value num">{{ fmtNum(squad.indicators.dps) }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">清泉羽化</span><b class="s-value num">{{ squad.totals.revives }}</b>
        </div>
        <div class="summary-item">
          <span class="s-label">焚骨</span><b class="s-value num">{{ squad.totals.fen_gu }}</b>
        </div>
      </div>

      <!-- 图表列表：点击图表名弹出查看（避免 6 图网格在矮视口下被压扁） -->
      <div class="chart-list">
        <div v-for="item in chartItems" :key="item.title" class="chart-list-item" @click="openChart(item)">
          <span class="chart-list-item__name">{{ item.title }}</span>
          <span class="chart-list-item__arrow">›</span>
        </div>
      </div>

      <!-- 成员表：3 个子标签（间距收紧，表格上提） -->
      <SquadMembersTabs
        :members="members"
        :adjustments="adjustments"
        :is-admin="isAdmin"
        :squad-key="squadKey"
        @remove-adjustment="$emit('removeAdjustment', $event)"
      />
    </div>
  </el-dialog>

  <!-- 图表查看弹窗：详情弹窗内点击图表名打开 -->
  <el-dialog
    v-model="chartViewerVisible"
    :title="activeChartTitle"
    width="72%"
    top="8vh"
    append-to-body
    destroy-on-close
    class="chart-viewer-dialog"
  >
    <EChart v-if="activeChartOption" :option="activeChartOption" height="100%" />
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

import type { SquadAnalysis } from '@/types/matchData'

import { fmtNum } from './analysis'
import EChart from './EChart.vue'
import SquadMembersTabs from './SquadMembersTabs.vue'
import {
  memberContribOption,
  memberEfficiencyOption,
  memberKdaScatterOption,
  memberKillsStackOption,
  memberRadarOption,
  memberRatioBarOption,
} from './squadCharts'

const props = defineProps<{
  name: string
  squad?: SquadAnalysis
  /** 分析调整副本：成员名 → "category:team_index" */
  adjustments?: Record<string, string>
  isAdmin?: boolean
  /** 当前小队的键（"category:team_index"） */
  squadKey?: string
}>()

defineEmits<{
  removeAdjustment: [playerName: string]
}>()

const visible = defineModel<boolean>({ required: true })

const members = computed(() => props.squad?.members ?? [])

/** 详情弹窗图表列表：点击名称弹出查看 */
const chartItems = computed(() => [
  { title: '成员四维对比', option: memberContribOption(members.value) },
  { title: '成员能力雷达图', option: memberRadarOption(members.value) },
  { title: '击杀/助攻/重伤', option: memberKillsStackOption(members.value) },
  { title: '效率指标对比', option: memberEfficiencyOption(members.value) },
  { title: '成员占比构成', option: memberRatioBarOption(members.value) },
  { title: '成员 KDA 散点', option: memberKdaScatterOption(members.value) },
])

const chartViewerVisible = ref(false)
const activeChartTitle = ref('')
const activeChartOption = ref<Record<string, unknown> | null>(null)

function openChart(item: { title: string; option: Record<string, unknown> }) {
  activeChartTitle.value = item.title
  activeChartOption.value = item.option
  chartViewerVisible.value = true
}
</script>

<style scoped>
/* ===== 详情弹窗：固定高度 + 图表区独立滚动（修复超出视口） =====
   弹窗级布局规则已迁移至 src/styles/element-plus.css 全局定义：
   detail-dialog 与 el-dialog 是同一根元素，scoped :deep(.el-dialog) 后代选择器无法命中 */

.detail-body {
  display: flex;
  flex-direction: column;
  gap: 0;
  height: 100%;
}

/* 小队汇总徽标栏（紧凑单行：给成员表留出完整 6 行空间） */
.squad-summary-bar {
  flex-shrink: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 6px;
}

.summary-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-md);
  padding: 3px 8px;
  background: var(--ink-bg-paper);
  white-space: nowrap;
}

.s-label {
  font-size: 10px;
  color: var(--ink-400);
}

.s-value {
  font-size: 13px;
  font-weight: 800;
  color: var(--gold-700);
}

/* 图表列表：占满剩余空间，至少保证 3 行完整可见，超高时内部滚动 */
.chart-list {
  flex: 1 1 auto;
  min-height: 130px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 4px;
  align-content: start;
}

.chart-list-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  background: var(--ink-bg-paper);
  cursor: pointer;
  transition:
    border-color var(--dur-fast),
    box-shadow var(--dur-fast),
    transform var(--dur-fast);
}

.chart-list-item:hover {
  border-color: var(--gold-500);
  box-shadow: var(--shadow-sm);
  transform: translateY(-1px);
}

.chart-list-item__name {
  font-size: 14px;
  font-weight: 600;
  color: var(--ink-900);
}

.chart-list-item__arrow {
  font-size: 18px;
  line-height: 1;
  color: var(--ink-400);
  transition:
    transform var(--dur-fast),
    color var(--dur-fast);
}

.chart-list-item:hover .chart-list-item__arrow {
  transform: translateX(3px);
  color: var(--gold-600);
}

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  .chart-list {
    grid-template-columns: 1fr;
  }

  /* 弹窗宽度覆盖已迁移至 element-plus.css 全局 media query */
}
</style>

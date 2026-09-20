<template>
  <div class="squad-analysis-tab">
    <EmptyState v-if="!loading && squads.length === 0" variant="chart" description="暂无数据或未关联排表（需先导入 CSV 与排表）" />
    <template v-else>
      <el-tabs v-model="mainTab" class="squad-main-tabs">
        <!-- 子 tab 1：总览图表 -->
        <el-tab-pane label="总览图表" name="overview">
          <SquadOverviewPanel :squads="effectiveSquads" />
        </el-tab-pane>

        <!-- 子 tab 2：小队明细 -->
        <el-tab-pane label="小队明细" name="detail">
          <SquadCardsGrid
            :squads="effectiveSquads"
            :total-players="totalPlayers"
            :adjusted-count="adjustedCount"
            :is-admin="auth.isAdmin"
            :detail-squad="detailSquad"
            v-model:compareMode="compareMode"
            :compare-checked="compareChecked"
            :compare-selected-count="compareSelectedNames.length"
            @open-detail="openDetail"
            @open-adjust="openAdjustDialog"
            @reset-adjustments="resetAdjustments"
            @open-compare="openCompare"
          />

          <SquadDetailDialog v-model="detailVisible" :name="detailSquad" :squad="detailSquadData" />
          <SquadCompareDialog v-model="compareVisible" :squads="compareSelectedSquads" :names="compareSelectedNames" />
          <SquadAssignDialog
            v-model="adjustVisible"
            :members="unassignedMembers"
            :teams="assignableTeams"
            :saving="adjustSaving"
            @confirm="onAssignConfirm"
          />
        </el-tab-pane>
      </el-tabs>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

import { getSquadAnalysis } from '@/api/matchData'
import { getSquadAdjustments, saveSquadAdjustments } from '@/api/squadAdjustments'
import { useAuthStore } from '@/stores/auth'
import type { SquadAnalysis, SquadIndicators, SquadMember, SquadTotals } from '@/types/matchData'

import SquadAssignDialog from './SquadAssignDialog.vue'
import SquadCardsGrid from './SquadCardsGrid.vue'
import SquadCompareDialog from './SquadCompareDialog.vue'
import SquadDetailDialog from './SquadDetailDialog.vue'
import SquadOverviewPanel from './SquadOverviewPanel.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const loading = ref(false)
const squads = ref<SquadAnalysis[]>([])
const mainTab = ref((route.query.squadTab as string) || 'overview')

// 分析调整副本：未排表成员 → 目标队伍（仅影响小队分析视图，不修改正式排表）
const adjustments = ref<Record<string, string>>({})
const adjustVisible = ref(false)
const adjustSaving = ref(false)

// 详情弹窗
const detailVisible = ref(false)
const detailSquad = ref('')

watch(mainTab, (v) => { router.replace({ query: { ...route.query, squadTab: v } }) })

// 对比模式
const compareMode = ref(false)
const compareChecked = reactive<Record<string, boolean>>({})
const compareVisible = ref(false)

const totalPlayers = computed(() => effectiveSquads.value.reduce((s, sq) => s + sq.totals.player_count, 0))

/**
 * 应用分析调整副本后的有效小队列表：成员按调整映射重分组，汇总/均值指标重算。
 * 调整仅作用于本视图，不修改正式排表。
 */
const effectiveSquads = computed(() => {
  const raw = squads.value
  const adj = adjustments.value
  if (!raw.length) return []
  const byKey = new Map<string, SquadMember[]>()
  for (const s of raw) byKey.set(`${s.category}:${s.team_index}`, [])
  for (const s of raw) {
    for (const m of s.members) {
      const target = adj[m.player_name]
      const key = target && byKey.has(target) ? target : `${s.category}:${s.team_index}`
      byKey.get(key)!.push(m)
    }
  }
  return raw.map((s) => {
    const members = byKey.get(`${s.category}:${s.team_index}`) ?? []
    return rebuildSquadTotals(s, members)
  })
})

/** 按成员列表重算小队汇总与均值指标（指标保留两位小数）。 */
function rebuildSquadTotals(meta: SquadAnalysis, members: SquadMember[]): SquadAnalysis {
  const n = members.length
  const totalKeys = ['kills', 'assists', 'player_damage', 'building_damage', 'healing', 'damage_taken', 'deaths', 'revives', 'fen_gu'] as const
  const totals: SquadTotals = { player_count: n } as SquadTotals
  for (const k of totalKeys) {
    totals[k] = members.reduce((sum, m) => sum + (m[k] as number), 0)
  }
  const indKeys = ['kda', 'dps', 'kpa_damage', 'damage_per_death', 'taken_per_death', 'healing_per_death', 'heal_conversion', 'revive_rate', 'fen_gu_rate'] as const
  const indicators: SquadIndicators = {} as SquadIndicators
  for (const k of indKeys) {
    indicators[k] = n ? Math.round((members.reduce((sum, m) => sum + (m[k] as number), 0) / n) * 100) / 100 : 0
  }
  return { ...meta, members, totals, indicators }
}

/** 已调整成员数（工具栏展示） */
const adjustedCount = computed(() => Object.keys(adjustments.value).length)

/** 可选目标队伍：原始数据中的排表队伍（排除未排表） */
const assignableTeams = computed(() =>
  squads.value.filter((s) => s.team_index >= 0 && s.category !== '-'),
)

/** 当前仍未分配的未排表成员（取有效数据中的未排表队伍成员） */
const unassignedMembers = computed(() => {
  const un = effectiveSquads.value.find((s) => s.team_index < 0)
  return un?.members ?? []
})

const detailSquadData = computed(() => effectiveSquads.value.find((s) => s.squad_name === detailSquad.value))

function openDetail(name: string) {
  detailSquad.value = name
  detailVisible.value = true
}

function openAdjustDialog() {
  adjustVisible.value = true
}

/** 分配确认（来自 SquadAssignDialog）：写入分析副本并保存，不影响正式排表 */
async function onAssignConfirm(names: string[], target: string) {
  adjustSaving.value = true
  try {
    const next = { ...adjustments.value }
    for (const name of names) next[name] = target
    await saveSquadAdjustments(props.scheduleId, next)
    adjustments.value = next
    adjustVisible.value = false
    ElMessage.success('已保存到分析副本（不影响正式排表）')
  } catch {
    /* 错误已由 http 拦截器提示 */
  } finally {
    adjustSaving.value = false
  }
}

async function resetAdjustments() {
  try {
    await ElMessageBox.confirm('将清空所有手动分配，恢复原始分组？此操作会覆盖已保存的分析副本。', '重置调整', { type: 'warning' })
  } catch {
    return
  }
  try {
    await saveSquadAdjustments(props.scheduleId, {})
    adjustments.value = {}
    ElMessage.success('已重置为原始分组')
  } catch {
    /* 已提示 */
  }
}

// 请求序号：快速切局时丢弃过期响应，避免旧局数据覆盖新局
let loadSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  try {
    const [data, adjResp] = await Promise.all([
      getSquadAnalysis(props.scheduleId, props.roundNo),
      getSquadAdjustments(props.scheduleId).catch(() => ({ data: {} as Record<string, string> })),
    ])
    if (seq !== loadSeq) return
    squads.value = data.squads
    adjustments.value = adjResp.data ?? {}
    // 初始化 checkbox 状态
    for (const s of squads.value) {
      if (!(s.squad_name in compareChecked)) compareChecked[s.squad_name] = false
    }
    // 关闭已不存在的面板
    if (detailSquad.value && !squads.value.some((s) => s.squad_name === detailSquad.value)) {
      detailSquad.value = ''
    }
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

watch(() => props.roundNo, load, { immediate: true })

// ==================== 对比面板 ====================

const compareSelectedNames = computed(() =>
  squads.value.filter((s) => compareChecked[s.squad_name]).map((s) => s.squad_name),
)

const compareSelectedSquads = computed(() =>
  effectiveSquads.value.filter((s) => compareChecked[s.squad_name]),
)

function openCompare() {
  compareVisible.value = true
}
</script>

<style scoped>
.squad-analysis-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.squad-main-tabs :deep(.el-tabs__header) {
  margin-bottom: 12px;
}

.squad-main-tabs :deep(.el-tabs__item) {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.squad-main-tabs :deep(.el-tabs__content) {
  padding: 0;
}
</style>

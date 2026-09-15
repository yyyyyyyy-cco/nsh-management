<template>
  <div class="squad-analysis-tab">
    <el-empty v-if="!loading && squads.length === 0" description="暂无数据或未关联排表（需先导入 CSV 与排表）" />
    <template v-else>
      <el-tabs v-model="mainTab" class="squad-main-tabs">
        <!-- 子 tab 1：总览图表 -->
        <el-tab-pane label="总览图表" name="overview">
          <!-- 图表行 1：击杀 + 伤害 -->
          <div class="chart-row">
            <div class="chart-card">
              <div class="chart-card__title">小队击杀对比</div>
              <EChart :option="killsBarOption" :height="340" />
            </div>
            <div class="chart-card">
              <div class="chart-card__title">小队伤害对比（万）</div>
              <EChart :option="damageBarOption" :height="340" />
            </div>
          </div>

          <!-- 图表行 2：塔伤 + 重伤对比 -->
          <div class="chart-row">
            <div class="chart-card">
              <div class="chart-card__title">小队塔伤贡献（万）</div>
              <EChart :option="towerBarOption" :height="340" />
            </div>
            <div class="chart-card">
              <div class="chart-card__title">小队重伤对比</div>
              <EChart :option="deathsBarOption" :height="340" />
            </div>
          </div>
        </el-tab-pane>

        <!-- 子 tab 2：小队明细 -->
        <el-tab-pane label="小队明细" name="detail">

      <!-- 小队卡片网格（按 category 分组，每组一行） -->
      <div class="chart-card">
        <div class="chart-card__head">
          <span class="chart-card__title">小队概览</span>
          <div class="card-toolbar">
            <span class="card-toolbar__count">共 {{ squads.length }} 个小队 · {{ totalPlayers }} 人</span>
            <el-tag v-if="adjustedCount" size="small" type="warning" effect="plain">已调整 {{ adjustedCount }} 人</el-tag>
            <el-button v-if="adjustedCount" link type="warning" size="small" @click="resetAdjustments">重置调整</el-button>
            <el-checkbox v-model="compareMode" label="对比模式" />
            <el-button
              v-if="compareMode && compareSelectedNames.length >= 2"
              type="primary"
              size="small"
              @click="openCompare"
            >对比所选小队（{{ compareSelectedNames.length }}）</el-button>
          </div>
        </div>

        <template v-for="group in squadGroups" :key="group.category">
          <div class="squad-group-label">{{ group.category }}</div>
          <div class="squad-row">
            <div
              v-for="s in group.items"
              :key="s.squad_name"
              class="squad-card"
              :class="{ 'squad-card--active': detailSquad === s.squad_name }"
              @click="openDetail(s.squad_name)"
            >
              <div class="squad-card__header">
                <el-checkbox
                  v-if="compareMode"
                  v-model="compareChecked[s.squad_name]"
                  @click.stop
                />
                <span class="squad-card__name">{{ s.squad_name }}</span>
                <span class="squad-card__count">{{ s.totals.player_count }}人</span>
              </div>
              <div class="squad-card__metrics">
                <div class="metric-item">
                  <span class="metric-label">击杀</span>
                  <span class="metric-value num">{{ s.totals.kills }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">助攻</span>
                  <span class="metric-value num">{{ s.totals.assists }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">重伤</span>
                  <span class="metric-value num">{{ s.totals.deaths }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">伤害</span>
                  <span class="metric-value num">{{ fmtNum(s.totals.player_damage) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">塔伤</span>
                  <span class="metric-value num">{{ fmtNum(s.totals.building_damage) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">承伤</span>
                  <span class="metric-value num">{{ fmtNum(s.totals.damage_taken) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">治疗</span>
                  <span class="metric-value num">{{ fmtNum(s.totals.healing) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">秒伤</span>
                  <span class="metric-value num">{{ fmtNum(s.indicators.dps) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">KDA</span>
                  <span class="metric-value num">{{ s.indicators.kda.toFixed(2) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">清泉羽化</span>
                  <span class="metric-value num">{{ s.totals.revives }}</span>
                </div>
              </div>
              <div class="squad-card__footer">
                <el-button
                  v-if="s.squad_name === '未排表' && auth.isAdmin"
                  text
                  type="warning"
                  size="small"
                  @click.stop="openAdjustDialog"
                >分配成员</el-button>
                <el-button text type="primary" size="small">查看详情 →</el-button>
              </div>
            </div>
          </div>
        </template>
      </div>

      <!-- 小队详情弹窗 -->
      <el-dialog
        v-model="detailVisible"
        :title="detailSquad + ' · 成员明细'"
        width="88%"
        top="3vh"
        destroy-on-close
        class="detail-dialog"
      >
        <div v-if="detailSquadData" class="detail-body">
          <!-- 小队汇总徽标栏 -->
          <div class="squad-summary-bar">
            <div class="summary-item"><span class="s-label">人数</span><b class="s-value">{{ detailSquadData.totals.player_count }}</b></div>
            <div class="summary-item"><span class="s-label">总击杀</span><b class="s-value num">{{ detailSquadData.totals.kills }}</b></div>
            <div class="summary-item"><span class="s-label">总伤害</span><b class="s-value num">{{ fmtNum(detailSquadData.totals.player_damage) }}</b></div>
            <div class="summary-item"><span class="s-label">总塔伤</span><b class="s-value num">{{ fmtNum(detailSquadData.totals.building_damage) }}</b></div>
            <div class="summary-item"><span class="s-label">总治疗</span><b class="s-value num">{{ fmtNum(detailSquadData.totals.healing) }}</b></div>
            <div class="summary-item"><span class="s-label">均KDA</span><b class="s-value num">{{ detailSquadData.indicators.kda.toFixed(2) }}</b></div>
            <div class="summary-item"><span class="s-label">均秒伤</span><b class="s-value num">{{ fmtNum(detailSquadData.indicators.dps) }}</b></div>
            <div class="summary-item"><span class="s-label">清泉羽化</span><b class="s-value num">{{ detailSquadData.totals.revives }}</b></div>
            <div class="summary-item"><span class="s-label">焚骨</span><b class="s-value num">{{ detailSquadData.totals.fen_gu }}</b></div>
          </div>

          <!-- 图表列表：点击图表名弹出查看（避免 6 图网格在矮视口下被压扁） -->
          <div class="chart-list">
            <div
              v-for="item in detailChartItems"
              :key="item.title"
              class="chart-list-item"
              @click="openChart(item)"
            >
              <span class="chart-list-item__name">{{ item.title }}</span>
              <span class="chart-list-item__arrow">›</span>
            </div>
          </div>

        <!-- 成员表：3 个子标签（间距收紧，表格上提） -->
        <el-tabs v-model="detailSubTab" class="detail-sub-tabs detail-tabs-wrap" style="margin-top: 6px">
          <el-tab-pane label="基础数据" name="basic">
            <el-table :data="detailMembers" size="small" border max-height="300">
              <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
              <el-table-column prop="profession" label="职业" min-width="70" />
              <el-table-column prop="kills" label="击杀" min-width="55" align="right" sortable />
              <el-table-column prop="assists" label="助攻" min-width="55" align="right" sortable />
              <el-table-column prop="deaths" label="重伤" min-width="55" align="right" sortable />
              <el-table-column prop="kda" label="KDA" min-width="65" align="right" sortable>
                <template #default="{ row }">{{ row.kda.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column prop="player_damage" label="玩家伤害" min-width="90" align="right" sortable>
                <template #default="{ row }">{{ fmtNum(row.player_damage) }}</template>
              </el-table-column>
              <el-table-column prop="building_damage" label="建筑伤害" min-width="90" align="right" sortable>
                <template #default="{ row }">{{ fmtNum(row.building_damage) }}</template>
              </el-table-column>
              <el-table-column prop="healing" label="治疗" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ fmtNum(row.healing) }}</template>
              </el-table-column>
              <el-table-column prop="damage_taken" label="承伤" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ fmtNum(row.damage_taken) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="效率指标" name="efficiency">
            <el-table :data="detailMembers" size="small" border max-height="300">
              <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
              <el-table-column prop="profession" label="职业" min-width="70" />
              <el-table-column prop="dps" label="秒伤" min-width="70" align="right" sortable />
              <el-table-column prop="kpa_damage" label="参与击杀均伤" min-width="100" align="right" sortable />
              <el-table-column prop="damage_per_death" label="每死输出值" min-width="100" align="right" sortable />
              <el-table-column prop="taken_per_death" label="每死承伤" min-width="90" align="right" sortable />
              <el-table-column prop="healing_per_death" label="每死治疗量" min-width="100" align="right" sortable />
              <el-table-column prop="heal_conversion" label="治疗转化率" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.heal_conversion.toFixed(2) }}</template>
              </el-table-column>
              <el-table-column prop="revive_rate" label="清泉羽化率" min-width="100" align="right" sortable>
                <template #default="{ row }">{{ row.revive_rate.toFixed(2) }}<em class="unit">次/分</em></template>
              </el-table-column>
              <el-table-column prop="fen_gu_rate" label="焚骨率" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ row.fen_gu_rate.toFixed(2) }}<em class="unit">次/分</em></template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <el-tab-pane label="占比指标" name="ratio">
            <el-table :data="detailMembers" size="small" border max-height="300">
              <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
              <el-table-column prop="profession" label="职业" min-width="70" />
              <el-table-column prop="kill_ratio" label="击杀占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.kill_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="assist_ratio" label="助攻占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.assist_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="player_damage_ratio" label="人伤占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.player_damage_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="building_ratio" label="拆塔占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.building_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="taken_ratio" label="承伤占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.taken_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="death_ratio" label="死亡占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.death_ratio) }}</template>
              </el-table-column>
              <el-table-column prop="heal_ratio" label="治疗占比" min-width="80" align="right" sortable>
                <template #default="{ row }">{{ pct(row.heal_ratio) }}</template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
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

      <!-- 多小队对比弹窗 -->
      <el-dialog
        v-model="compareVisible"
        :title="'小队对比（' + compareSelectedNames.join(' vs ') + '）'"
        width="80%"
        top="4vh"
        destroy-on-close
        class="compare-dialog"
      >
        <div class="chart-row">
          <div>
            <div class="chart-card__title">汇总对比</div>
            <EChart :option="compareSummaryBar" :height="300" />
          </div>
          <div>
            <div class="chart-card__title">均值指标雷达图</div>
            <EChart :option="compareRadar" :height="300" />
          </div>
        </div>

        <!-- 差值表（恰好选 2 队时） -->
        <div v-if="compareSelectedNames.length === 2" class="diff-table-wrap">
          <div class="chart-card__title">差值 / 波动值</div>
          <el-table :data="compareDiffRows" size="small" border max-height="260">
            <el-table-column prop="label" label="指标" min-width="110" />
            <el-table-column :label="compareSelectedNames[0]" min-width="90" align="right">
              <template #default="{ row }">{{ row.v1 }}</template>
            </el-table-column>
            <el-table-column :label="compareSelectedNames[1]" min-width="90" align="right">
              <template #default="{ row }">{{ row.v2 }}</template>
            </el-table-column>
            <el-table-column label="差值" min-width="90" align="right">
              <template #default="{ row }">
                <span :class="row.diff >= 0 ? 'diff-pos' : 'diff-neg'">{{ row.diff >= 0 ? '+' : '' }}{{ row.diffStr }}</span>
              </template>
            </el-table-column>
            <el-table-column label="波动值" min-width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.min(Math.abs(row.wave), 100)"
                  :stroke-width="12"
                  :format="() => `${row.wave.toFixed(2)}%`"
                  :status="row.wave > 20 ? 'exception' : row.wave > 5 ? 'warning' : 'success'"
                />
              </template>
            </el-table-column>
          </el-table>
        </div>
      </el-dialog>

      <!-- 分配未排表成员（保存到分析副本，不影响正式排表） -->
      <el-dialog v-model="adjustVisible" title="分配未排表成员" width="560px" append-to-body>
        <div class="adjust-tip">
          将未排表成员手动分配到目标队伍。调整保存在<b>分析副本</b>中，不会修改正式排表。
        </div>
        <el-select v-model="adjustTarget" placeholder="选择目标队伍" size="small" style="width: 100%">
          <el-option
            v-for="t in assignableTeams"
            :key="`${t.category}:${t.team_index}`"
            :label="t.squad_name"
            :value="`${t.category}:${t.team_index}`"
          />
        </el-select>
        <div class="adjust-members">
          <template v-if="unassignedMembers.length">
            <el-checkbox-group v-model="adjustSelected">
              <el-checkbox v-for="m in unassignedMembers" :key="m.player_name" :value="m.player_name">
                <span class="adjust-member__name">{{ m.player_name }}</span>
                <span class="adjust-member__prof" :style="{ color: profColor(m.profession ?? '') }">{{ m.profession || '未知' }}</span>
              </el-checkbox>
            </el-checkbox-group>
          </template>
          <el-empty v-else description="未排表成员已全部调整" :image-size="60" />
        </div>
        <template #footer>
          <el-button size="small" @click="adjustVisible = false">取消</el-button>
          <el-button
            size="small"
            type="primary"
            :disabled="!adjustTarget || !adjustSelected.length"
            :loading="adjustSaving"
            @click="confirmAdjust"
          >确定分配</el-button>
        </template>
      </el-dialog>
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
import { fmtNum, profColor } from './analysis'
import EChart from './EChart.vue'
import { CHART_THEME } from './chartTheme'

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
const adjustTarget = ref('')
const adjustSelected = ref<string[]>([])
const adjustSaving = ref(false)

// 详情弹窗
const detailVisible = ref(false)
const detailSquad = ref('')
const detailSubTab = ref('basic')

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

function openAdjustDialog() {
  adjustSelected.value = []
  adjustTarget.value = ''
  adjustVisible.value = true
}

async function confirmAdjust() {
  if (!adjustTarget.value || !adjustSelected.value.length) return
  adjustSaving.value = true
  try {
    const next = { ...adjustments.value }
    for (const name of adjustSelected.value) next[name] = adjustTarget.value
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

/** 按 category 分组，保持原始顺序 */
const squadGroups = computed(() => {
  const map = new Map<string, SquadAnalysis[]>()
  for (const s of effectiveSquads.value) {
    const cat = s.category || '其他'
    if (!map.has(cat)) map.set(cat, [])
    map.get(cat)!.push(s)
  }
  return [...map.entries()].map(([category, items]) => ({ category, items }))
})

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

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

// ==================== 顶部图表 ====================

function barBase(data: number[]) {
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    grid: { left: 16, right: 20, top: 30, bottom: 56, containLabel: true },
    xAxis: {
      type: 'category',
      data: squads.value.map((s) => s.squad_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 30, fontSize: 10, width: 60, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [{
      name: '数值', type: 'bar', barWidth: 16,
      itemStyle: { color: '#c9a13b', borderRadius: [3, 3, 0, 0] },
      data,
    }],
  }
}

const killsBarOption = computed(() => barBase(effectiveSquads.value.map((s) => s.totals.kills)))
const damageBarOption = computed(() => barBase(effectiveSquads.value.map((s) => +(s.totals.player_damage / 10000).toFixed(0))))
const towerBarOption = computed(() => barBase(effectiveSquads.value.map((s) => +(s.totals.building_damage / 10000).toFixed(0))))
const deathsBarOption = computed(() => barBase(effectiveSquads.value.map((s) => s.totals.deaths)))

// ==================== 详情面板 ====================

function openDetail(name: string) {
  detailSquad.value = name
  detailSubTab.value = 'basic'
  detailVisible.value = true
}

const detailSquadData = computed(() => effectiveSquads.value.find((s) => s.squad_name === detailSquad.value))
const detailMembers = computed(() => detailSquadData.value?.members ?? [])

const CONTRIB_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b']

/** 成员四维对比：玩家伤害/建筑伤害/治疗/承伤 分组柱状图 */
const detailContribOption = computed(() => {
  const members = detailMembers.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: ['玩家伤害', '建筑伤害', '治疗', '承伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '玩家伤害', type: 'bar', barWidth: 7, barGap: '15%', itemStyle: { color: CONTRIB_COLORS[0], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.player_damage) },
      { name: '建筑伤害', type: 'bar', barWidth: 7, itemStyle: { color: CONTRIB_COLORS[1], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.building_damage) },
      { name: '治疗', type: 'bar', barWidth: 7, itemStyle: { color: CONTRIB_COLORS[2], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.healing) },
      { name: '承伤', type: 'bar', barWidth: 7, itemStyle: { color: CONTRIB_COLORS[3], borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.damage_taken) },
    ],
  }
})

/** 成员能力雷达图（全员叠加） */
const detailRadarOption = computed(() => {
  const members = detailMembers.value
  if (!members.length) return {}
  const maxOf = (fn: (m: SquadAnalysis['members'][number]) => number) => Math.max(...members.map(fn), 1) * 1.15
  const dims = [
    { name: '击杀', max: maxOf((m) => m.kills) },
    { name: '助攻', max: maxOf((m) => m.assists) },
    { name: '伤害', max: maxOf((m) => m.player_damage) },
    { name: '治疗', max: maxOf((m) => m.healing) },
    { name: '承伤', max: maxOf((m) => m.damage_taken) },
    { name: 'KDA', max: maxOf((m) => m.kda) },
  ]
  const RADAR_MEMBER_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b', '#8B5CF6', '#f6ff00']
  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: members.map((m) => m.player_name), ...CHART_THEME.legend, type: 'scroll' },
    radar: {
      center: ['50%', '44%'],
      radius: '58%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 40 },
      indicator: dims.map((d) => ({ name: d.name, max: Math.round(d.max) })),
    },
    series: [{
      type: 'radar',
      data: members.map((m, i) => ({
        name: m.player_name,
        value: [m.kills, m.assists, m.player_damage, m.healing, m.damage_taken, m.kda],
        areaStyle: { opacity: 0.06 },
        lineStyle: { width: 2, color: RADAR_MEMBER_COLORS[i % RADAR_MEMBER_COLORS.length] },
        itemStyle: { color: RADAR_MEMBER_COLORS[i % RADAR_MEMBER_COLORS.length] },
        symbol: 'circle',
        symbolSize: 4,
      })),
    }],
  }
})

/** 成员占比构成：击杀/助攻/人伤/拆塔/承伤/治疗 占比 堆叠条形图 */
const detailRatioBarOption = computed(() => {
  const members = detailMembers.value
  const ratios = [
    { key: 'kill_ratio', label: '击杀占比' },
    { key: 'assist_ratio', label: '助攻占比' },
    { key: 'player_damage_ratio', label: '人伤占比' },
    { key: 'building_ratio', label: '拆塔占比' },
    { key: 'taken_ratio', label: '承伤占比' },
    { key: 'heal_ratio', label: '治疗占比' },
  ]
  const COLORS = ['#c9a13b', '#e8d48b', '#5b7a9d', '#2e8b57', '#c0392b', '#FF9CF2']
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => (v * 100).toFixed(1) + '%' },
    legend: { bottom: 0, data: ratios.map((r) => r.label), ...CHART_THEME.legend, type: 'scroll' },
    grid: { left: 12, right: 16, top: 20, bottom: 40, containLabel: true },
    xAxis: {
      type: 'value',
      max: 1,
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => (v * 100) + '%' },
    },
    yAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 50, overflow: 'truncate' },
    },
    series: ratios.map((r, i) => ({
      name: r.label,
      type: 'bar',
      stack: 'total',
      barWidth: 14,
      itemStyle: { color: COLORS[i] },
      data: members.map((m) => (m[r.key as keyof SquadMember] as number) ?? 0),
    })),
  }
})

/** 成员 KDA 散点：击杀 vs 重伤，气泡大小=伤害 */
const detailKdaScatter = computed(() => {
  const members = detailMembers.value
  return {
    backgroundColor: 'transparent',
    tooltip: {
      ...CHART_THEME.tooltip,
      formatter: (p: unknown) => {
        const d = (p as { data: (number | string)[] }).data
        return `<b>${d[3]}</b> (${d[4]})<br/>击杀: ${d[0]}<br/>重伤: ${d[1]}<br/>KDA: ${Number(d[5]).toFixed(2)}<br/>伤害: ${fmtNum(Number(d[2]))}`
      },
    },
    grid: { left: 16, right: 20, top: 20, bottom: 16, containLabel: true },
    xAxis: {
      name: '击杀', nameLocation: 'middle', nameGap: 28,
      axisLabel: { ...CHART_THEME.axis.axisLabel, margin: 10 },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName, padding: [6, 0, 0, 0] },
    },
    yAxis: {
      name: '重伤', nameLocation: 'middle', nameGap: 40,
      axisLabel: { ...CHART_THEME.axis.axisLabel, width: 40, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
      nameTextStyle: { ...CHART_THEME.axis.axisName },
    },
    series: [{
      type: 'scatter',
      symbolSize: (data: number[]) => Math.max(8, Math.min(22, Math.sqrt(data[2]) / 400)),
      data: members.map((m) => [m.kills, m.deaths, m.player_damage, m.player_name, m.profession || '未知', m.kda]),
      itemStyle: {
        color: (p: { data: (number | string)[] }) => profColor(String(p.data[4])),
        opacity: 0.8,
        borderColor: 'rgba(0,0,0,0.1)',
        borderWidth: 1,
      },
      emphasis: { itemStyle: { opacity: 1, borderColor: '#fff', borderWidth: 2, shadowBlur: 8, shadowColor: 'rgba(0,0,0,0.3)' } },
      label: {
        show: true,
        formatter: (p: unknown) => (p as { data: (string | number)[] }).data[3],
        fontSize: 10,
        color: '#555',
        position: 'top',
      },
    }],
  }
})

/** 成员击杀/助攻/重伤 分组柱状图（新增） */
const detailKillsStackOption = computed(() => {
  const members = detailMembers.value
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: ['击杀', '助攻', '重伤'], ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
    },
    yAxis: { type: 'value', axisLabel: CHART_THEME.axis.axisLabel, splitLine: CHART_THEME.axis.splitLine },
    series: [
      { name: '击杀', type: 'bar', barWidth: 8, itemStyle: { color: '#c9a13b', borderRadius: [2, 2, 0, 0] }, data: members.map((m) => m.kills) },
      { name: '助攻', type: 'bar', barWidth: 8, itemStyle: { color: '#e8d48b' }, data: members.map((m) => m.assists) },
      { name: '重伤', type: 'bar', barWidth: 8, itemStyle: { color: '#c0392b' }, data: members.map((m) => m.deaths) },
    ],
  }
})

/** 成员效率指标：秒伤 / 每死输出 / 每死治疗 分组柱状图（新增） */
const detailEfficiencyOption = computed(() => {
  const members = detailMembers.value
  const series = [
    { key: 'dps', label: '秒伤', color: '#5b7a9d' },
    { key: 'damage_per_death', label: '每死输出', color: '#c9a13b' },
    { key: 'healing_per_death', label: '每死治疗', color: '#2e8b57' },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { bottom: 0, data: series.map((s) => s.label), ...CHART_THEME.legend },
    grid: { left: 12, right: 16, top: 20, bottom: 36, containLabel: true },
    xAxis: {
      type: 'category',
      data: members.map((m) => m.player_name),
      axisLabel: { ...CHART_THEME.axis.axisLabel, rotate: 25, fontSize: 10, width: 50, overflow: 'truncate' },
    },
    yAxis: {
      type: 'value',
      axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 50, overflow: 'truncate' },
      splitLine: CHART_THEME.axis.splitLine,
    },
    series: series.map((s) => ({
      name: s.label,
      type: 'bar',
      barWidth: 8,
      itemStyle: { color: s.color, borderRadius: [2, 2, 0, 0] },
      data: members.map((m) => (m[s.key as keyof SquadMember] as number) ?? 0),
    })),
  }
})

/** 详情弹窗图表列表：点击名称弹出查看（避免网格图在矮视口下被压扁） */
const detailChartItems = [
  { title: '成员四维对比', option: detailContribOption },
  { title: '成员能力雷达图', option: detailRadarOption },
  { title: '击杀/助攻/重伤', option: detailKillsStackOption },
  { title: '效率指标对比', option: detailEfficiencyOption },
  { title: '成员占比构成', option: detailRatioBarOption },
  { title: '成员 KDA 散点', option: detailKdaScatter },
]

const chartViewerVisible = ref(false)
const activeChartTitle = ref('')
const activeChartOption = ref<Record<string, unknown> | null>(null)

function openChart(item: (typeof detailChartItems)[number]) {
  activeChartTitle.value = item.title
  activeChartOption.value = item.option.value
  chartViewerVisible.value = true
}

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

const COMPARE_COLORS = ['#c9a13b', '#5b7a9d', '#2e8b57', '#c0392b']

const compareSummaryBar = computed(() => {
  const sel = compareSelectedSquads.value
  const metrics = [
    { key: 'kills', label: '击杀' },
    { key: 'assists', label: '助攻' },
    { key: 'deaths', label: '重伤' },
    { key: 'player_damage', label: '玩家伤害' },
    { key: 'building_damage', label: '建筑伤害' },
    { key: 'healing', label: '治疗' },
    { key: 'damage_taken', label: '承伤' },
  ]
  return {
    backgroundColor: 'transparent',
    tooltip: { trigger: 'axis', ...CHART_THEME.tooltip, valueFormatter: (v: number) => fmtNum(v) },
    legend: { top: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    grid: { left: 16, right: 20, top: 40, bottom: 8, containLabel: true },
    xAxis: { type: 'category', data: metrics.map((m) => m.label), axisLabel: { ...CHART_THEME.axis.axisLabel, interval: 0 } },
    yAxis: { type: 'value', axisLabel: { ...CHART_THEME.axis.axisLabel, formatter: (v: number) => fmtNum(v), width: 50, overflow: 'truncate' }, splitLine: CHART_THEME.axis.splitLine },
    series: sel.map((s, i) => ({
      name: s.squad_name,
      type: 'bar',
      barWidth: 14,
      barGap: '30%',
      itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length], borderRadius: [3, 3, 0, 0] },
      data: metrics.map((m) => s.totals[m.key as keyof typeof s.totals]),
      // 柱顶数值：击杀/助攻/重伤小数字原样展示，大额伤害压缩
      label: {
        show: true,
        position: 'top',
        fontSize: 10,
        color: '#6b5b45',
        formatter: (p: { value: number }) => (p.value > 9999 ? fmtNum(p.value) : String(p.value)),
      },
    })),
  }
})

const compareRadar = computed(() => {
  const sel = compareSelectedSquads.value
  const dims = [
    { name: 'KDA', max: 0 },
    { name: '秒伤', max: 0 },
    { name: '每死输出', max: 0 },
    { name: '每死承伤', max: 0 },
    { name: '治疗转化', max: 0 },
  ]
  const keys: (keyof SquadAnalysis['indicators'])[] = ['kda', 'dps', 'damage_per_death', 'taken_per_death', 'heal_conversion']
  // 动态 max
  for (const d of dims) d.max = 1
  for (const s of sel) {
    keys.forEach((k, i) => {
      const v = s.indicators[k] as number
      if (v > dims[i].max) dims[i].max = v
    })
  }
  // 留余量
  for (const d of dims) d.max = Math.ceil(d.max * 1.15)

  return {
    backgroundColor: 'transparent',
    tooltip: { ...CHART_THEME.tooltip },
    legend: { bottom: 0, data: sel.map((s) => s.squad_name), ...CHART_THEME.legend },
    radar: {
      center: ['50%', '46%'],
      radius: '60%',
      axisName: { ...CHART_THEME.axis.axisName, overflow: 'truncate', width: 50 },
      indicator: dims,
    },
    series: [{
      type: 'radar',
      data: sel.map((s, i) => ({
        name: s.squad_name,
        value: keys.map((k) => s.indicators[k] as number),
        areaStyle: { opacity: 0.1 },
        lineStyle: { width: 2.5, color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
        itemStyle: { color: COMPARE_COLORS[i % COMPARE_COLORS.length] },
        symbol: 'circle',
        symbolSize: 5,
      })),
    }],
  }
})

const COMPARE_METRIC_LABELS: Record<string, string> = {
  kills: '总击杀', assists: '总助攻', player_damage: '玩家伤害',
  building_damage: '建筑伤害', healing: '治疗', damage_taken: '承伤',
  deaths: '总死亡', kda: '均 KDA', dps: '均秒伤',
  damage_per_death: '均每死输出', taken_per_death: '均每死承伤',
  heal_conversion: '均治疗转化',
}

const compareDiffRows = computed(() => {
  const sel = compareSelectedSquads.value
  if (sel.length !== 2) return []
  const [a, b] = sel
  const rows: { label: string; v1: string; v2: string; diff: number; diffStr: string; wave: number }[] = []

  // 汇总指标
  const totalKeys: (keyof SquadAnalysis['totals'])[] = ['kills', 'assists', 'player_damage', 'building_damage', 'healing', 'damage_taken', 'deaths']
  for (const k of totalKeys) {
    const v1 = a.totals[k] as number
    const v2 = b.totals[k] as number
    const diff = v1 - v2
    const base = Math.min(v1, v2)
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: fmtNum(v1), v2: fmtNum(v2),
      diff, diffStr: fmtNum(Math.abs(diff)),
      wave: base > 0 ? Math.abs(diff) / base * 100 : 0,
    })
  }

  // 均值指标
  const indKeys: (keyof SquadAnalysis['indicators'])[] = ['kda', 'dps', 'damage_per_death', 'taken_per_death', 'heal_conversion']
  for (const k of indKeys) {
    const v1 = a.indicators[k] as number
    const v2 = b.indicators[k] as number
    const diff = +(v1 - v2).toFixed(2)
    const base = Math.min(v1, v2)
    const isDecimal = k === 'kda' || k === 'heal_conversion'
    rows.push({
      label: COMPARE_METRIC_LABELS[k] ?? k,
      v1: isDecimal ? v1.toFixed(2) : fmtNum(Math.round(v1)),
      v2: isDecimal ? v2.toFixed(2) : fmtNum(Math.round(v2)),
      diff, diffStr: isDecimal ? Math.abs(diff).toFixed(2) : fmtNum(Math.round(Math.abs(diff))),
      wave: base > 0 ? Math.abs(diff) / base * 100 : 0,
    })
  }

  return rows
})
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

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
}

.chart-card__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
}

.card-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-toolbar__count {
  font-size: 12px;
  color: var(--ink-400);
}

/* ===== 卡片分组（每队一行） ===== */
.squad-group-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--ink-700);
  margin: 10px 0 6px;
  border-left: 3px solid var(--gold-500);
  padding-left: 8px;
}

.squad-group-label:first-of-type {
  margin-top: 0;
}

.squad-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 4px;
}

.squad-card {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--ink-bg-paper);
}

.squad-card:hover {
  border-color: var(--gold-400);
  box-shadow: var(--shadow-sm);
}

.squad-card--active {
  border-color: var(--gold-500);
  box-shadow: 0 0 0 1px var(--gold-200);
}

.squad-card__header {
  flex-shrink: 0;
  min-width: 128px;
  display: flex;
  align-items: center;
  gap: 6px;
}

.squad-card__name {
  font-weight: 700;
  font-size: 13px;
  color: var(--ink-800);
  white-space: nowrap;
}

.squad-card__count {
  font-size: 11px;
  color: var(--ink-400);
  white-space: nowrap;
}

.squad-card__metrics {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
}

.metric-item {
  display: flex;
  align-items: baseline;
  gap: 4px;
  white-space: nowrap;
}

.metric-label {
  font-size: 11px;
  color: var(--ink-400);
}

.metric-value {
  font-size: 13px;
  font-weight: 800;
  color: var(--gold-700);
}

.squad-card__footer {
  flex-shrink: 0;
  text-align: right;
}

/* ===== 分配未排表成员 ===== */
.adjust-tip {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 10px;
  line-height: 1.6;
}

.adjust-tip b {
  color: var(--gold-700);
}

.adjust-members {
  margin-top: 12px;
  max-height: 260px;
  overflow-y: auto;
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-md);
  padding: 8px 12px;
  background: var(--ink-bg-cream);
}

.adjust-member__name {
  font-size: 13px;
}

.adjust-member__prof {
  font-size: 12px;
  margin-left: 6px;
}

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
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast), transform var(--dur-fast);
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
  transition: transform var(--dur-fast), color var(--dur-fast);
}

.chart-list-item:hover .chart-list-item__arrow {
  transform: translateX(3px);
  color: var(--gold-600);
}

/* 成员表区：固定高度（表格内部滚动） */
.detail-tabs-wrap {
  flex-shrink: 0;
}

/* ===== 对比弹窗：同样固定高度（规则已迁移至 element-plus.css 全局定义） ===== */

.detail-sub-tabs :deep(.el-tabs__header) {
  margin-bottom: 10px;
}

.detail-sub-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 600;
}

.detail-sub-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.unit {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 2px;
}

/* ===== 对比差值 ===== */
.diff-table-wrap {
  margin-top: 12px;
}

.diff-table-wrap .chart-card__title {
  margin-bottom: 8px;
}

.diff-pos {
  color: var(--gold-700);
  font-weight: 700;
}

.diff-neg {
  color: #c0392b;
  font-weight: 700;
}

/* ===== 移动端 ===== */
@media (max-width: 768px) {
  /* 图表卡内边距收紧，为窄屏图表释放宽度 */
  .chart-card {
    padding: 12px;
  }

  .chart-row {
    grid-template-columns: 1fr;
  }

  .chart-list {
    grid-template-columns: 1fr;
  }

  /* 小队卡片：窄屏纵向堆叠，指标自动换行 */
  .squad-card {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }

  .squad-card__header {
    min-width: 0;
  }

  .squad-card__metrics {
    gap: 4px 10px;
  }

  /* 弹窗宽度覆盖已迁移至 element-plus.css 全局 media query */
}
</style>

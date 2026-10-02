<template>
  <div class="indicators-tab">
    <!-- 工具栏：阵营筛选 + 职业筛选 + ID 搜索 -->
    <div class="toolbar">
      <el-select aria-label="阵营筛选" v-model="campFilter" placeholder="阵营筛选" clearable style="width: 150px">
        <el-option v-for="c in camps" :key="c.camp" :label="c.camp" :value="c.camp" />
      </el-select>
      <el-select aria-label="职业筛选" v-model="profFilter" placeholder="职业筛选" clearable style="width: 150px">
        <el-option v-for="p in professions" :key="p" :label="p" :value="p" />
      </el-select>
      <el-input aria-label="按ID搜索" v-model="nameFilter" placeholder="按ID搜索" clearable style="width: 180px" :prefix-icon="Search" />
      <span class="toolbar__count">{{ filteredItems.length }} 人</span>
    </div>

    <div class="chart-card">
      <el-tabs v-model="subTab" class="indicator-sub-tabs">
        <!-- 基础战斗数据 -->
        <el-tab-pane label="基础数据" name="basic">
          <el-table :data="filteredItems" v-loading="loading" max-height="560" fit border size="small" class="ind-table">
            <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
            <el-table-column prop="profession" label="职业" min-width="70" />
            <el-table-column prop="camp" label="阵营" min-width="70" />
            <el-table-column prop="kills" label="击杀" align="right" min-width="65" sortable />
            <el-table-column prop="assists" label="助攻" align="right" min-width="65" sortable />
            <el-table-column prop="deaths" label="重伤" align="right" min-width="65" sortable />
            <el-table-column prop="kda" label="KDA" align="right" min-width="70" sortable>
              <template #default="{ row }">{{ row.kda.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="dps" label="秒伤" align="right" min-width="75" sortable />
            <el-table-column prop="player_damage" label="玩家伤害" align="right" min-width="100" sortable>
              <template #default="{ row }">{{ fmtNum(row.player_damage) }}</template>
            </el-table-column>
            <el-table-column prop="building_damage" label="建筑伤害" align="right" min-width="100" sortable>
              <template #default="{ row }">{{ fmtNum(row.building_damage) }}</template>
            </el-table-column>
            <el-table-column prop="healing" label="治疗" align="right" min-width="90" sortable>
              <template #default="{ row }">{{ fmtNum(row.healing) }}</template>
            </el-table-column>
            <el-table-column prop="damage_taken" label="承伤" align="right" min-width="90" sortable>
              <template #default="{ row }">{{ fmtNum(row.damage_taken) }}</template>
            </el-table-column>
            <el-table-column prop="revives" label="复活/清泉" align="right" min-width="80" sortable />
            <el-table-column prop="fen_gu" label="焚骨" align="right" min-width="70" sortable />
          </el-table>
        </el-tab-pane>

        <!-- 效率指标 -->
        <el-tab-pane label="效率指标" name="efficiency">
          <el-table :data="filteredItems" v-loading="loading" max-height="560" fit border size="small" class="ind-table">
            <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
            <el-table-column prop="profession" label="职业" min-width="70" />
            <el-table-column prop="camp" label="阵营" min-width="70" />
            <el-table-column prop="kda" label="KDA" align="right" min-width="70" sortable>
              <template #default="{ row }">{{ row.kda.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="dps" label="秒伤" align="right" min-width="75" sortable />
            <el-table-column prop="kpa_damage" label="参与击杀均伤" align="right" min-width="100" sortable />
            <el-table-column prop="damage_per_death" label="每死输出值" align="right" min-width="100" sortable />
            <el-table-column prop="taken_per_death" label="每死承伤" align="right" min-width="90" sortable />
            <el-table-column prop="healing_per_death" label="每死治疗量" align="right" min-width="100" sortable />
            <el-table-column prop="heal_conversion" label="治疗转化率" align="right" min-width="100" sortable>
              <template #default="{ row }">{{ row.heal_conversion.toFixed(2) }}</template>
            </el-table-column>
            <el-table-column prop="revive_rate" label="清泉羽化率" align="right" min-width="100" sortable>
              <template #default="{ row }">{{ row.revive_rate.toFixed(2) }}<em class="unit">次/分</em></template>
            </el-table-column>
            <el-table-column prop="fen_gu_rate" label="焚骨率" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ row.fen_gu_rate.toFixed(2) }}<em class="unit">次/分</em></template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 占比指标 -->
        <el-tab-pane label="占比指标" name="ratio">
          <el-table :data="filteredItems" v-loading="loading" max-height="560" fit border size="small" class="ind-table">
            <el-table-column prop="player_name" label="ID" min-width="110" fixed="left" />
            <el-table-column prop="profession" label="职业" min-width="70" />
            <el-table-column prop="camp" label="阵营" min-width="70" />
            <el-table-column prop="kill_ratio" label="击杀占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.kill_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="assist_ratio" label="助攻占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.assist_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="player_damage_ratio" label="人伤占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.player_damage_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="building_ratio" label="拆塔占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.building_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="taken_ratio" label="承伤占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.taken_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="death_ratio" label="死亡占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.death_ratio) }}</template>
            </el-table-column>
            <el-table-column prop="heal_ratio" label="治疗占比" align="right" min-width="80" sortable>
              <template #default="{ row }">{{ pct(row.heal_ratio) }}</template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'

import { getIndicators } from '@/api/matchData'
import type { CampTotals, MatchDataIndicators } from '@/types/matchData'

const props = defineProps<{ scheduleId: number; roundNo: number }>()

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const items = ref<MatchDataIndicators[]>([])
const camps = ref<CampTotals[]>([])
const campFilter = ref('')
const profFilter = ref('')
const nameFilter = ref('')
/** 防抖后的搜索词：避免每敲一个字符触发全量过滤与表格重排 */
const appliedNameFilter = ref('')
let nameFilterTimer: ReturnType<typeof setTimeout> | null = null
watch(nameFilter, (v) => {
  if (nameFilterTimer) clearTimeout(nameFilterTimer)
  nameFilterTimer = setTimeout(() => {
    appliedNameFilter.value = v
  }, 250)
})
onBeforeUnmount(() => {
  if (nameFilterTimer) clearTimeout(nameFilterTimer)
})
const subTab = ref((route.query.sub as string) || 'basic')

watch(subTab, (v) => { router.replace({ query: { ...route.query, sub: v } }) })

const professions = computed(() => [...new Set(items.value.map((r) => r.profession || '未知'))].sort())

const filteredItems = computed(() => {
  let list = items.value
  if (campFilter.value) list = list.filter((r) => r.camp === campFilter.value)
  if (profFilter.value) list = list.filter((r) => (r.profession || '未知') === profFilter.value)
  const kw = appliedNameFilter.value.trim()
  if (kw) list = list.filter((r) => r.player_name.includes(kw))
  return list
})

// 请求序号：快速切局时丢弃过期响应，避免旧局数据覆盖新局
let loadSeq = 0

async function load() {
  const seq = ++loadSeq
  loading.value = true
  try {
    const data = await getIndicators(props.scheduleId, props.roundNo)
    if (seq !== loadSeq) return
    items.value = data.items
    camps.value = data.camps
  } finally {
    if (seq === loadSeq) loading.value = false
  }
}

watch(() => props.roundNo, load, { immediate: true })

function pct(v: number): string {
  return ((v || 0) * 100).toFixed(2) + '%'
}

function fmtNum(v: number): string {
  if (v >= 10000) return (v / 10000).toFixed(1) + '万'
  return (v || 0).toLocaleString()
}
</script>

<style scoped>
.indicators-tab {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.toolbar__count {
  font-size: 13px;
  color: var(--ink-500);
}

.chart-card {
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-lg);
  padding: 14px 16px;
  background: var(--ink-bg-paper);
  box-shadow: var(--shadow-sm);
}

.chart-card__title {
  font-size: 14px;
  font-weight: 700;
  font-family: var(--font-serif);
  letter-spacing: 1px;
  color: var(--ink-800);
  margin-bottom: 10px;
}

/* 子标签页样式：去掉多余间距，与表格融合 */
.indicator-sub-tabs :deep(.el-tabs__header) {
  margin-bottom: 10px;
}

.indicator-sub-tabs :deep(.el-tabs__item) {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.indicator-sub-tabs :deep(.el-tabs__content) {
  padding: 0;
}

.unit {
  font-style: normal;
  font-size: 11px;
  color: var(--ink-400);
  margin-left: 2px;
}
</style>

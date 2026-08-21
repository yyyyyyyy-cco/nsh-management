<template>
  <div class="lineup-tab">
    <!-- 管理员：拖拽编排（保存后刷新总览） -->
    <LineupEditor ref="editorRef" v-if="isAdmin" :schedule-id="scheduleId" @saved="loadOverview" />

    <!-- 排表总览（管理员与帮众均可见） -->
    <div ref="overviewRef" class="overview-wrap">
      <el-card v-loading="loading" shadow="never" class="overview">
        <template #header>
          <div class="overview-header">
            <span class="overview-title">排表总览</span>
            <span class="overview-sub">按ID查找位置</span>
            <el-button class="overview-export" size="small" :loading="exporting" :icon="Picture" @click="onExportOverview">
              导出 PNG
            </el-button>
          </div>
        </template>
      <div v-if="titleRemark" class="title-remark-bar">{{ titleRemark }}</div>
      <el-empty v-if="!loading && !totalPlaced" description="排表中暂无成员" />
      <template v-else>
        <!-- 四组卡片 -->
        <div class="overview-grid">
          <div v-for="g in groupViews" :key="g.category" class="og-group" :class="`og-group--${g.type}`">
            <div class="og-group__header">
              <span class="og-group__dot" />
              <span class="og-group__label">{{ g.label }}</span>
              <span v-if="groupsRemark[g.category]" class="og-group__remark" :title="groupsRemark[g.category]">{{ groupsRemark[g.category] }}</span>
              <span class="og-group__meta">{{ g.teams.length }}队</span>
            </div>
            <div class="og-teams">
              <div v-for="team in g.teams" :key="team.category + team.team_index" class="og-team">
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
        </div>

        <!-- 职业分布 -->
        <div class="prof-stats">
          <span class="prof-stats__label">职业分布</span>
          <span
            v-for="p in PROF_ORDER"
            :key="p"
            class="prof-stats__item"
            :class="{ active: (profCount[p] || 0) > 0 }"
            :style="(profCount[p] || 0) > 0 ? { color: profColor(p), borderColor: profColor(p) + '55', background: profColor(p) + '1a' } : {}"
          >
            {{ p }} <strong>{{ profCount[p] || 0 }}</strong>
          </span>
          <span class="prof-stats__total">合计 {{ totalPlaced }} 人</span>
        </div>
      </template>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'
import html2canvas from 'html2canvas'

import { getLineup } from '@/api/lineups'
import { useAuthStore } from '@/stores/auth'
import type { LineupTeam } from '@/types/lineup'
import { PROF_ORDER } from '@/composables/lineupBoard'
import LineupEditor from './LineupEditor.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()
const isAdmin = computed(() => auth.isAdmin)
const loading = ref(false)
const teams = ref<LineupTeam[]>([])
const editorRef = ref<InstanceType<typeof LineupEditor>>()
const exporting = ref(false)
const overviewRef = ref<HTMLElement | null>(null)
const titleRemark = ref('')
const groupsRemark = ref<Record<string, string>>({})

/** 四大分组（进攻/防守配色与编辑器一致）。 */
const GROUPS = [
  { category: '进攻1', label: '进攻一', type: 'attack' },
  { category: '进攻2', label: '进攻二', type: 'attack' },
  { category: '防守1', label: '防守一', type: 'defense' },
  { category: '防守2', label: '防守二', type: 'defense' },
]

/** 职业色映射（依据 ui-style-guide）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profColor(prof: string | null | undefined) {
  return (prof && PROF_COLORS[prof]) || '#c9a13b'
}

const groupViews = computed(() =>
  GROUPS.map((g) => ({
    ...g,
    teams: teams.value
      .filter((t) => t.category === g.category)
      .sort((a, b) => a.team_index - b.team_index),
  })),
)

const totalPlaced = computed(() =>
  teams.value.reduce((n, t) => n + t.slots.filter((s) => s.member_name).length, 0),
)

/** 已排成员职业计数。 */
const profCount = computed(() => {
  const map: Record<string, number> = {}
  for (const t of teams.value) {
    for (const s of t.slots) {
      if (s.member_name && s.profession) map[s.profession] = (map[s.profession] || 0) + 1
    }
  }
  return map
})

function filledCount(team: LineupTeam): number {
  return team.slots.filter((s) => s.member_name).length
}

function footerClass(team: LineupTeam): string {
  const n = filledCount(team)
  return n === 6 ? 'is-full' : n > 0 ? 'is-partial' : 'is-empty'
}

/** 导出排表总览为 PNG。 */
async function onExportOverview() {
  const el = overviewRef.value
  if (!el) return
  exporting.value = true
  try {
    const canvas = await html2canvas(el, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      // 固定 PC 视口尺寸渲染，导出的图片大小与布局不受当前浏览器窗口影响
      windowWidth: 1440,
      windowHeight: Math.max(window.innerHeight, 3000),
    })
    const link = document.createElement('a')
    link.download = `排表总览_${props.scheduleId}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    ElMessage.success('排表总览图片已导出')
  } catch (e) {
    ElMessage.error(`导出失败：${e instanceof Error ? e.message : '未知错误'}`)
  } finally {
    exporting.value = false
  }
}

async function loadOverview() {
  loading.value = true
  try {
    const lineup = await getLineup(props.scheduleId)
    teams.value = lineup.data
    titleRemark.value = lineup.title_remark || ''
    groupsRemark.value = lineup.groups_remark || {}
  } finally {
    loading.value = false
  }
}

/** Tab 重新激活时刷新（出勤库变动后补人/成员可同步到候选池与总览）。 */
function reload() {
  loadOverview()
  editorRef.value?.reload()
}

defineExpose({ reload })

onMounted(loadOverview)
</script>

<style scoped>
.overview {
  border-radius: var(--radius-lg);
}

.overview-header {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overview-export {
  margin-left: auto;
  flex-shrink: 0;
}

.overview-title {
  font-family: var(--font-serif);
  font-weight: 700;
  letter-spacing: 1px;
}

.overview-sub {
  font-size: 12px;
  color: var(--ink-400);
  font-weight: normal;
}

/* ===== 总备注横幅 ===== */
.title-remark-bar {
  text-align: center;
  font-size: 13px;
  font-weight: 600;
  color: var(--gold-800);
  background: linear-gradient(135deg, var(--gold-100) 0%, var(--gold-50) 100%);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-md);
  padding: 8px 16px;
  margin-bottom: 14px;
}

/* ===== 分组卡片 ===== */
.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

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

/* ===== 职业分布 ===== */
.prof-stats {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 14px;
  padding: 12px 14px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-lg);
  background: var(--ink-bg-wash);
}

.prof-stats__label {
  font-size: 12px;
  font-weight: 700;
  color: var(--ink-600);
  margin-right: 4px;
}

.prof-stats__item {
  font-size: 12px;
  font-weight: 400;
  color: var(--ink-300);
  border: 1px solid var(--edge-soft);
  border-radius: var(--radius-xl);
  padding: 1px 8px;
}

.prof-stats__item strong {
  font-weight: 700;
}

.prof-stats__item.active {
  font-weight: 600;
}

.prof-stats__total {
  margin-left: auto;
  font-size: 12px;
  font-weight: 700;
  color: var(--gold-700);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .overview-header {
    flex-wrap: wrap;
    gap: 6px 12px;
  }

  .overview-sub {
    display: none; /* 窄屏隐藏副标题，避免溢出 */
  }

  .overview-export {
    margin-left: auto;
  }

  .overview-grid {
    grid-template-columns: 1fr;
  }

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

  .prof-stats {
    gap: 6px;
    padding: 10px 12px;
  }
}

@media (max-width: 480px) {
  .og-teams {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

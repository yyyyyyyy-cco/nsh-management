<template>
  <div ref="overviewRef" class="overview-wrap">
    <el-card shadow="never" class="overview">
      <template #header>
        <div class="overview-header">
          <span class="overview-title">排表总览</span>
          <span class="overview-sub">按ID查找位置</span>
          <div class="overview-actions">
            <!-- 显示方案：圆点 = 职业色圆点标识（默认）；全底色 = 职业色铺满整格。导出 PNG 截取实时 DOM，自动同步当前方案 -->
            <el-radio-group v-model="displayMode" size="small">
              <el-radio-button value="dot">圆点</el-radio-button>
              <el-radio-button value="fill">全底色</el-radio-button>
            </el-radio-group>
            <el-button
              class="overview-export"
              size="small"
              :loading="exporting"
              :icon="Picture"
              @click="onExportOverview"
            >
              导出 PNG
            </el-button>
          </div>
        </div>
      </template>
      <div v-if="titleRemark" class="title-remark-bar">{{ titleRemark }}</div>
      <SkeletonTable v-if="showSkeleton && !totalPlaced" variant="table" :rows="4" />
      <EmptyState v-else-if="!loading && !totalPlaced" description="排表中暂无成员" />
      <template v-else>
        <!-- 四组卡片 -->
        <div class="overview-grid">
          <LineupOverviewGroup
            v-for="g in groupViews"
            :key="g.category"
            :group="g"
            :groups-remark="groupsRemark"
            :fill-bg="displayMode === 'fill'"
          />
        </div>

        <!-- 职业分布 -->
        <div class="prof-stats">
          <span class="prof-stats__label">职业分布</span>
          <span
            v-for="p in professionStore.activeNames"
            :key="p"
            class="prof-stats__item"
            :class="{ active: (profCount[p] || 0) > 0 }"
            :style="
              (profCount[p] || 0) > 0
                ? { color: profColor(p), borderColor: profColor(p) + '55', background: profColor(p) + '1a' }
                : {}
            "
          >
            {{ p }} <strong>{{ profCount[p] || 0 }}</strong>
          </span>
          <span class="prof-stats__total">合计 {{ totalPlaced }} 人</span>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Picture } from '@element-plus/icons-vue'

import { getLineup } from '@/api/lineups'
import type { LineupTeam } from '@/types/lineup'
import { useProfessionStore } from '@/stores/profession'
import { profColor } from '@/utils/profession'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import LineupOverviewGroup from './LineupOverviewGroup.vue'

const props = defineProps<{ scheduleId: number }>()
const professionStore = useProfessionStore()

const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const teams = ref<LineupTeam[]>([])
const exporting = ref(false)
/** 总览显示方案：dot = 职业色圆点（默认、现有方案），fill = 职业色铺满整格。 */
const displayMode = ref<'dot' | 'fill'>('dot')
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

const groupViews = computed(() =>
  GROUPS.map((g) => ({
    ...g,
    teams: teams.value.filter((t) => t.category === g.category).sort((a, b) => a.team_index - b.team_index),
  })),
)

const totalPlaced = computed(() => teams.value.reduce((n, t) => n + t.slots.filter((s) => s.member_name).length, 0))

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

/** 导出排表总览为 PNG：不含顶部标题/操作行与底部职业分布统计；截取实时 DOM（圆点 / 全底色自动同步）。 */
async function onExportOverview() {
  const el = overviewRef.value
  if (!el) return
  exporting.value = true
  try {
    // html2canvas 体积较大（~470KB）：点击导出时才动态加载，不进首屏 chunk
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(el, {
      backgroundColor: '#ffffff',
      scale: 2,
      useCORS: true,
      // 导出图不含顶部标题/操作行与底部职业分布统计（仅克隆文档中移除，实时界面不受影响）
      onclone: (_doc: Document, clonedEl: HTMLElement) =>
        clonedEl.querySelectorAll('.el-card__header,.prof-stats').forEach((n) => n.remove()),
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

/** Tab 重新激活 / 编辑器保存后刷新总览。 */
function reload() {
  loadOverview()
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

.overview-actions {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
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

/* 显示方案切换：雅金分段控件（与赛程列表「本月/全部」同款配色） */
.overview-actions :deep(.el-radio-button__inner) {
  border-color: var(--gold-200);
  color: var(--gold-700);
  background: var(--ink-bg-paper);
}

.overview-actions :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gold-gradient);
  border-color: transparent;
  color: #fff;
  box-shadow: -1px 0 0 0 var(--gold-400);
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

.overview-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
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

  .overview-grid {
    grid-template-columns: 1fr;
  }

  .prof-stats {
    gap: 6px;
    padding: 10px 12px;
  }
}
</style>

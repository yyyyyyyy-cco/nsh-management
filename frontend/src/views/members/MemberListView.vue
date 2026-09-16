<template>
  <div class="member-list">
    <el-tabs v-model="activeTab" class="member-tabs" @tab-change="onTabChange">
      <el-tab-pane label="成员列表" name="list">
        <el-card shadow="never" class="page-card">
          <MemberStatsBar :show-skeleton="showSkeleton" :stats="stats" :total="total" />
          <ProfessionShortage :refresh-key="shortageRefreshKey" />
          <MemberToolbar
            :query="query"
            :exporting="exporting"
            :selected-count="selectedIds.length"
            @search="handleSearch"
            @create="openForm()"
            @import="importVisible = true"
            @export="onExport"
            @batch-delete="onBatchDelete"
          />
          <MemberTablePanel
            :is-mobile="isMobile"
            :loading="loading"
            :show-skeleton="showSkeleton"
            :items="items"
            :total="total"
            :selected-ids="selectedIds"
            :query="query"
            @selection-change="onSelectionChange"
            @toggle-select="toggleSelect"
            @sort-change="onSortChange"
            @edit="openForm"
            @delete="onDelete"
            @reload="load"
          />
        </el-card>
      </el-tab-pane>
      <el-tab-pane label="出勤率统计" name="rate">
        <AttendanceRatePanel />
      </el-tab-pane>
    </el-tabs>

    <MemberFormDialog v-model="formVisible" :member="editingMember" @success="load" />
    <MemberImportDialog v-model="importVisible" @success="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useMemberList } from '@/composables/useMemberList'
import type { MemberInfo } from '@/types/member'
import AttendanceRatePanel from '@/components/members/AttendanceRatePanel.vue'
import MemberFormDialog from '@/components/members/MemberFormDialog.vue'
import MemberImportDialog from '@/components/members/MemberImportDialog.vue'
import MemberStatsBar from '@/components/members/MemberStatsBar.vue'
import MemberTablePanel from '@/components/members/MemberTablePanel.vue'
import MemberToolbar from '@/components/members/MemberToolbar.vue'
import ProfessionShortage from '@/components/members/ProfessionShortage.vue'

const route = useRoute()
const router = useRouter()

const activeTab = ref('list')

// 支持从首页「出勤排行」跳转直达出勤率统计 Tab；刷新时从 URL 恢复当前 Tab
if (route.query.tab === 'rate') {
  activeTab.value = 'rate'
}

/** Tab 切换同步到 URL，刷新后保持当前 Tab。 */
function onTabChange(name: string | number) {
  router.replace({ query: { ...route.query, tab: String(name) } })
}

// 数据与操作逻辑（见 composables/useMemberList）
const {
  loading,
  showSkeleton,
  items,
  total,
  stats,
  selectedIds,
  shortageRefreshKey,
  exporting,
  query,
  load,
  handleSearch,
  onSortChange,
  onExport,
  onSelectionChange,
  toggleSelect,
  onDelete,
  onBatchDelete,
} = useMemberList()

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
  selectedIds.value = [] // 形态切换时清空勾选，避免残留「看不见的已勾选」
}

const formVisible = ref(false)
const importVisible = ref(false)
const editingMember = ref<MemberInfo | null>(null)

function openForm(member: MemberInfo | null = null) {
  editingMember.value = member
  formVisible.value = true
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped>
/* ===== 排序箭头强化：激活态放大并高亮，便于区分升/降序 ===== */
.member-list :deep(.caret-wrapper) {
  width: 20px;
  height: 34px;
}

.member-list :deep(.caret-wrapper .sort-caret) {
  border-width: 6px;
  left: 6px;
}

.member-list :deep(.caret-wrapper .sort-caret.ascending) {
  border-bottom-color: var(--gold-300);
  top: 4px;
}

.member-list :deep(.caret-wrapper .sort-caret.descending) {
  border-top-color: var(--gold-300);
  bottom: 6px;
}

.member-list :deep(.el-table__header th.ascending .sort-caret.ascending) {
  border-bottom-color: var(--gold-600);
}

.member-list :deep(.el-table__header th.descending .sort-caret.descending) {
  border-top-color: var(--gold-600);
}

.member-list :deep(.el-table__header th.is-sortable .cell) {
  color: var(--ink-800);
  font-weight: 600;
}

.member-list :deep(.el-table__header th.ascending .cell),
.member-list :deep(.el-table__header th.descending .cell) {
  color: var(--gold-700);
}

/* finesse · register=product · shell=member-list: row-list(≤768px) + toolbar grid(≤768px) 主操作满宽 + 2×2 + 44px 触控 */

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 卡片内边距收紧（对齐赛程详情/联赛总览），为行列表释放横向空间 */
  .page-card :deep(.el-card__body) {
    padding: 14px;
  }
}
</style>

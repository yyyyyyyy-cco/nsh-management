<template>
  <div class="member-list">
    <el-tabs v-model="activeTab" class="member-tabs" @tab-change="onTabChange">
      <el-tab-pane label="成员列表" name="list">
        <el-card shadow="never" class="page-card">
      <div class="stats-bar">
        <template v-if="showSkeleton">
          <span class="stats-item">正式 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
          <span class="stats-sep" />
          <span class="stats-item">替补 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
          <span class="stats-sep" />
          <span class="stats-item">当前筛选共 <span class="sk sk-line sk-kpi-sm" style="vertical-align:middle" /></span>
        </template>
        <template v-else>
          <span class="stats-item">正式 <b class="num">{{ stats.formal_count }}</b> 人</span>
          <span class="stats-sep" />
          <span class="stats-item">替补 <b class="num">{{ stats.substitute_count }}</b> 人</span>
          <span class="stats-sep" />
          <span class="stats-item">当前筛选共 <b class="num">{{ total }}</b> 人</span>
        </template>
      </div>
      <ProfessionShortage :refresh-key="shortageRefreshKey" />
      <div class="toolbar">
        <div class="toolbar-filters">
          <el-input
            v-model="query.keyword"
            placeholder="搜索ID"
            clearable
            class="keyword"
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            @clear="handleSearch"
          />
          <el-select v-model="query.profession" placeholder="职业筛选" clearable class="filter" @change="handleSearch">
            <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
          </el-select>
          <el-select v-model="query.status" placeholder="状态筛选" clearable class="filter" @change="handleSearch">
            <el-option v-for="s in MEMBER_STATUSES" :key="s.value" :label="s.label" :value="s.value" />
          </el-select>
        </div>
        <div class="toolbar-actions">
          <el-button type="primary" :icon="Plus" @click="openForm()">添加成员</el-button>
          <el-button :icon="Upload" @click="importVisible = true">Excel 导入</el-button>
          <el-button :icon="Download" :loading="exporting" @click="onExport('xlsx')">导出 Excel</el-button>
          <el-button :icon="Download" :loading="exporting" @click="onExport('png')">导出图片</el-button>
          <el-button
            type="danger"
            plain
            :icon="Delete"
            :disabled="selectedIds.length === 0"
            @click="onBatchDelete"
          >
            批量删除
            <span v-if="selectedIds.length" class="batch-count num">{{ selectedIds.length }}</span>
          </el-button>
        </div>
      </div>

      <!-- 移动端（≤768px）：成员行列表，职业标签 + 紧凑编辑/删除 -->
      <div v-if="isMobile" class="member-rows">
        <SkeletonTable v-if="showSkeleton && !items.length" variant="rows" :rows="5" />
        <el-empty v-else-if="!loading && !items.length" description="暂无成员数据" :image-size="72" />
        <div v-for="row in items" :key="row.id" class="member-row">
          <div class="mr-main">
            <el-checkbox
              class="mr-check"
              :model-value="selectedIds.includes(row.id)"
              @change="toggleSelect(row.id)"
            />
            <span class="mr-name">{{ row.name }}</span>
            <el-tag class="mr-status" :type="row.status === 'formal' ? 'primary' : 'info'" effect="light" size="small">
              {{ row.status === 'formal' ? '正式' : '替补' }}
            </el-tag>
          </div>
          <div v-if="row.remark" class="mr-remark">备注：{{ row.remark }}</div>
          <div class="mr-actions">
            <span class="mr-profs">
              <span class="prof-tag" :style="profStyle(row.main_profession)">{{ row.main_profession }}</span>
              <span v-if="row.sub_profession" class="prof-tag prof-tag--sub" :style="profStyle(row.sub_profession)">
                {{ row.sub_profession }}
              </span>
            </span>
            <el-button class="mr-act mr-act--edit" @click="openForm(row)">编辑</el-button>
            <el-button class="mr-act" type="danger" plain @click="onDelete(row)">删除</el-button>
          </div>
        </div>
      </div>

      <!-- 桌面端：表格形态保持不变 -->
      <SkeletonTable v-else-if="showSkeleton && !items.length" variant="table" :rows="5" />
      <el-table v-else
        :data="items"
        :default-sort="{ prop: 'name', order: 'ascending' }"
        @selection-change="onSelectionChange"
        @sort-change="onSortChange"
      >
        <el-table-column type="selection" width="48" />
        <el-table-column prop="name" label="ID" min-width="120" sortable="custom">
          <template #default="{ row }">
            <span class="member-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="main_profession" label="主职业" min-width="100" sortable="custom">
          <template #default="{ row }">
            <span class="prof-tag" :style="profStyle(row.main_profession)">{{ row.main_profession }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="sub_profession" label="副职业" min-width="90">
          <template #default="{ row }">
            <span v-if="row.sub_profession" class="prof-tag prof-tag--sub" :style="profStyle(row.sub_profession)">
              {{ row.sub_profession }}
            </span>
            <span v-else class="dim">-</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" min-width="80">
          <template #default="{ row }">
            <el-tag :type="row.status === 'formal' ? 'primary' : 'info'" effect="light">
              {{ row.status === 'formal' ? '正式' : '替补' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="160" show-overflow-tooltip />
        <el-table-column label="操作" min-width="130">
          <template #default="{ row }">
            <el-button link type="primary" @click="openForm(row)">编辑</el-button>
            <el-button link type="danger" @click="onDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="query.page"
        v-model:page-size="query.page_size"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        class="pagination"
        @change="load"
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
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Plus, Search, Upload, Download, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { batchDeleteMembers, deleteMember, exportMembers, exportMembersImage, listMembers, type MemberStats, type MemberQuery } from '@/api/members'
import type { MemberInfo } from '@/types/member'
import { MEMBER_STATUSES, PROFESSIONS } from '@/utils/constants'
import { PROF_COLORS } from '@/utils/profession'
import AttendanceRatePanel from '@/components/members/AttendanceRatePanel.vue'
import ProfessionShortage from '@/components/members/ProfessionShortage.vue'
import MemberFormDialog from '@/components/members/MemberFormDialog.vue'
import MemberImportDialog from '@/components/members/MemberImportDialog.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const activeTab = ref('list')
const shortageRefreshKey = ref(0) // 成员数据变更（添加/导入/删除）后递增，驱动缺少职业组件刷新
const route = useRoute()
const router = useRouter()

// 支持从首页「出勤排行」跳转直达出勤率统计 Tab；刷新时从 URL 恢复当前 Tab
if (route.query.tab === 'rate') {
  activeTab.value = 'rate'
}

/** Tab 切换同步到 URL，刷新后保持当前 Tab。 */
function onTabChange(name: string | number) {
  router.replace({ query: { ...route.query, tab: String(name) } })
}

const items = ref<MemberInfo[]>([])
const total = ref(0)
const stats = ref<MemberStats>({ formal_count: 0, substitute_count: 0 })
const selectedIds = ref<number[]>([])

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

/** 初始默认按 ID 正序（与后端白名单字段 name 对应）。 */
const query = reactive<MemberQuery>({ page: 1, page_size: 20, sort_by: 'name', sort_order: 'asc' })

function profStyle(prof: string) {
  const bg = PROF_COLORS[prof] || '#e5e7eb'
  const dark = ['#3E6BF4', '#F04545', '#8B5CF6', '#4F95FF', '#605EF0', '#C6834D']
  const color = dark.includes(bg) ? '#fff' : '#333'
  return { background: bg, color }
}

/** 服务端排序变化：携带排序参数重新请求全量数据（无视分页）。 */
function onSortChange({ prop, order }: { prop: string; order: 'ascending' | 'descending' | null }) {
  if (order) {
    query.sort_by = prop
    query.sort_order = order === 'ascending' ? 'asc' : 'desc'
  } else {
    delete query.sort_by
    delete query.sort_order
  }
  query.page = 1
  load()
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))

async function load() {
  loading.value = true
  // 刷新后清空勾选：桌面表格随数据更新失去选中，移动端勾选同步清空保持一致
  selectedIds.value = []
  try {
    const page = await listMembers(query)
    items.value = page.items
    total.value = page.total
    stats.value = page.stats
  } finally {
    loading.value = false
    shortageRefreshKey.value += 1
  }
}

function handleSearch() {
  query.page = 1
  load()
}

/** 一键导出：沿用当前筛选与排序（不含分页），浏览器直接下载 xlsx / png。 */
const exporting = ref(false)
async function onExport(format: 'xlsx' | 'png') {
  exporting.value = true
  try {
    const params = {
      keyword: query.keyword,
      profession: query.profession,
      status: query.status,
      sort_by: query.sort_by,
      sort_order: query.sort_order,
    }
    const blob = format === 'xlsx' ? await exportMembers(params) : await exportMembersImage(params)
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    const tag = new Date().toISOString().slice(0, 10).replace(/-/g, '')
    link.href = url
    link.download = `常驻库_${tag}.${format}`
    link.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('导出失败，请稍后重试')
  } finally {
    exporting.value = false
  }
}

function onSelectionChange(rows: MemberInfo[]) {
  selectedIds.value = rows.map((row) => row.id)
}

/** 移动端行内勾选：与桌面表格共用 selectedIds，支撑批量删除。 */
function toggleSelect(id: number) {
  const idx = selectedIds.value.indexOf(id)
  if (idx >= 0) selectedIds.value.splice(idx, 1)
  else selectedIds.value.push(id)
}

function openForm(member: MemberInfo | null = null) {
  editingMember.value = member
  formVisible.value = true
}

async function onDelete(row: MemberInfo) {
  await ElMessageBox.confirm(`确定删除成员「${row.name}」吗？`, '提示', { type: 'warning' })
  await deleteMember(row.id)
  ElMessage.success('删除成功')
  load()
}

async function onBatchDelete() {
  await ElMessageBox.confirm(`确定删除选中的 ${selectedIds.value.length} 名成员吗？`, '提示', { type: 'warning' })
  const result = await batchDeleteMembers(selectedIds.value)
  ElMessage.success(result.message)
  load()
}
</script>

<style scoped>
.stats-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  font-size: 13px;
  color: var(--ink-500);
}

.stats-item b {
  font-size: 17px;
  color: var(--gold-700);
}

.stats-sep {
  width: 1px;
  height: 14px;
  background: var(--gold-300);
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.toolbar-filters {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* 筛选区与操作区以淡分割线区分 */
.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-left: auto;
  padding-left: 16px;
  border-left: 1px solid var(--edge-faint);
}

/* 批量删除选中数量徽标 */
.batch-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  margin-left: 4px;
  border-radius: 9px;
  background: var(--cinnabar);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  line-height: 1;
}

.member-name {
  font-weight: 600;
  color: var(--ink-900);
}

.keyword {
  width: 220px;
}

.filter {
  width: 140px;
}

/* 职业色标签 */
.prof-tag {
  display: inline-block;
  padding: 2px 10px;
  border-radius: var(--radius-xl);
  font-size: 12px;
  font-weight: 600;
  line-height: 1.7;
}

.prof-tag--sub {
  opacity: 0.75;
}

.dim {
  color: var(--ink-300);
}

.pagination {
  margin-top: 16px;
  justify-content: flex-end;
}

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

/* ===== 移动端行列表（isMobile 时渲染，替换表格） ===== */
.member-rows {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态/加载遮罩的占位高度 */
  touch-action: manipulation;
}

.member-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.member-row:last-child {
  border-bottom: none;
}

.mr-main {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.mr-check {
  flex-shrink: 0;
  padding: 10px 6px 10px 0;
}

.mr-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--ink-900);
}

.mr-status {
  flex-shrink: 0;
  margin-left: auto;
}

.mr-remark {
  margin-top: 6px;
  margin-left: 28px; /* 与职业标签组同左缩进（约 2 个字符宽） */
  font-size: 12px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

/* 职业标签组：动作行最左，右移约 2 个字符宽，与编辑/删除同行 */
.mr-profs {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-left: 28px;
  margin-right: auto;
  flex-shrink: 0;
}

.mr-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 8px;
}

/* 紧凑动作按钮：32px 高、内容宽度，右对齐 */
.mr-actions .el-button.mr-act {
  height: 32px;
  margin-left: 0;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
}

/* 编辑：鎏金描边（与录屏行内动作同一形态，规避 primary+plain 浑浊） */
.mr-actions .el-button.mr-act--edit {
  background: var(--gold-50);
  border: 1px solid var(--gold-300);
  color: var(--gold-700);
}

.mr-actions .el-button.mr-act--edit:active {
  background: var(--gold-100);
  border-color: var(--gold-400);
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  /* 卡片内边距收紧（对齐赛程详情/联赛总览），为行列表释放横向空间 */
  .page-card :deep(.el-card__body) {
    padding: 14px;
  }

  .toolbar-filters {
    flex: 1 1 100%;
  }

  /* 操作区：主操作（添加成员）满宽一行，其余按钮两列均分 */
  .toolbar-actions {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    flex: 1 1 100%;
    border-left: none;
    padding-left: 0;
  }

  /* 44px 触控高度；收窄左右内边距保证 320px 下「导出 Excel」单行不溢出 */
  .toolbar-actions .el-button {
    width: 100%;
    height: 44px;
    margin-left: 0 !important;
    padding: 0 10px;
  }

  .toolbar-actions .el-button:first-child {
    grid-column: 1 / -1;
  }

  /* 选中数量徽标窄屏收紧，避免撑破网格单元 */
  .batch-count {
    min-width: 16px;
    height: 16px;
    padding: 0 4px;
    margin-left: 3px;
    font-size: 10px;
  }

  .keyword,
  .filter {
    flex: 1 1 100%;
    width: 100%;
  }

  .pagination {
    justify-content: center;
  }
}
</style>

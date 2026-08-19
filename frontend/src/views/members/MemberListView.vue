<template>
  <div class="member-list page-enter">
    <el-card shadow="never" class="page-card">
      <div class="toolbar">
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
        <div class="spacer" />
        <el-button type="primary" :icon="Plus" @click="openForm()">添加成员</el-button>
        <el-button :icon="Upload" @click="importVisible = true">Excel 导入</el-button>
        <el-button type="danger" plain :disabled="selectedIds.length === 0" @click="onBatchDelete">
          批量删除{{ selectedIds.length ? `（${selectedIds.length}）` : '' }}
        </el-button>
      </div>

      <el-table v-loading="loading" :data="items" @selection-change="onSelectionChange">
        <el-table-column type="selection" width="48" />
        <el-table-column prop="name" label="ID" min-width="120">
          <template #default="{ row }">
            <span class="member-name">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="main_profession" label="主职业" min-width="100">
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

    <AttendanceRatePanel />
    <MemberFormDialog v-model="formVisible" :member="editingMember" @success="load" />
    <MemberImportDialog v-model="importVisible" @success="load" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { Plus, Search, Upload } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { batchDeleteMembers, deleteMember, listMembers, type MemberQuery } from '@/api/members'
import type { MemberInfo } from '@/types/member'
import { MEMBER_STATUSES, PROFESSIONS } from '@/utils/constants'
import AttendanceRatePanel from '@/components/members/AttendanceRatePanel.vue'
import MemberFormDialog from '@/components/members/MemberFormDialog.vue'
import MemberImportDialog from '@/components/members/MemberImportDialog.vue'

const loading = ref(false)
const items = ref<MemberInfo[]>([])
const total = ref(0)
const selectedIds = ref<number[]>([])
const formVisible = ref(false)
const importVisible = ref(false)
const editingMember = ref<MemberInfo | null>(null)

const query = reactive<MemberQuery>({ page: 1, page_size: 20 })

/** 职业颜色（依据 ui-style-guide §9 职业色映射）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profStyle(prof: string) {
  const bg = PROF_COLORS[prof] || '#e5e7eb'
  const dark = ['#3E6BF4', '#F04545', '#8B5CF6', '#4F95FF', '#605EF0', '#C6834D']
  const color = dark.includes(bg) ? '#fff' : '#333'
  return { background: bg, color }
}

onMounted(load)

async function load() {
  loading.value = true
  try {
    const page = await listMembers(query)
    items.value = page.items
    total.value = page.total
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  query.page = 1
  load()
}

function onSelectionChange(rows: MemberInfo[]) {
  selectedIds.value = rows.map((row) => row.id)
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
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.keyword {
  width: 220px;
}

.filter {
  width: 140px;
}

.spacer {
  flex: 1;
}

.member-name {
  font-weight: 600;
  color: var(--ink-900);
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

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .keyword,
  .filter {
    flex: 1 1 100%;
    width: 100%;
  }

  .toolbar .el-button {
    flex: 1;
    margin-left: 0 !important;
  }

  .pagination {
    justify-content: center;
  }
}
</style>

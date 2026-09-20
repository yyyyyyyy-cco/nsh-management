<template>
  <!-- 移动端（≤768px）：成员行列表，职业标签 + 紧凑编辑/删除 -->
  <div v-if="isMobile" class="member-rows">
    <SkeletonTable v-if="showSkeleton && !items.length" variant="rows" :rows="5" />
    <EmptyState v-else-if="!loading && !items.length" description="暂无成员数据" :image-size="72" />
    <div v-for="row in items" :key="row.id" class="member-row">
      <div class="mr-main">
        <el-checkbox
          class="mr-check"
          :model-value="selectedIds.includes(row.id)"
          @change="$emit('toggle-select', row.id)"
        />
        <span class="mr-name mr-name--link" title="查看成员详情" @click="$emit('detail', row)">
          {{ row.name }}<el-icon class="mr-link-icon"><ArrowRight /></el-icon>
        </span>
        <el-tag class="mr-status" :type="row.status === 'formal' ? 'primary' : 'info'" effect="light" size="small">
          {{ row.status === 'formal' ? '正式' : '替补' }}
        </el-tag>
      </div>
      <div v-if="row.remark" class="mr-remark">备注：{{ row.remark }}</div>
      <div class="mr-actions">
        <span class="mr-profs">
          <span class="prof-tag" :style="profTagStyle(row.main_profession)">{{ row.main_profession }}</span>
          <span v-if="row.sub_profession" class="prof-tag prof-tag--sub" :style="profTagStyle(row.sub_profession)">
            {{ row.sub_profession }}
          </span>
        </span>
        <el-button class="mr-act mr-act--edit" @click="$emit('edit', row)">编辑</el-button>
        <el-button class="mr-act" type="danger" plain @click="$emit('delete', row)">删除</el-button>
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
        <span class="member-name member-name--link" title="查看成员详情" @click="$emit('detail', row)">{{ row.name }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="main_profession" label="主职业" min-width="100" sortable="custom">
      <template #default="{ row }">
        <span class="prof-tag" :style="profTagStyle(row.main_profession)">{{ row.main_profession }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="sub_profession" label="副职业" min-width="90">
      <template #default="{ row }">
        <span v-if="row.sub_profession" class="prof-tag prof-tag--sub" :style="profTagStyle(row.sub_profession)">
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
        <el-button link type="primary" @click="$emit('edit', row)">编辑</el-button>
        <el-button link type="danger" @click="$emit('delete', row)">删除</el-button>
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
    @change="$emit('reload')"
  />
</template>

<script setup lang="ts">
import { ArrowRight } from '@element-plus/icons-vue'

import type { MemberQuery } from '@/api/members'
import type { MemberInfo } from '@/types/member'
import { profTagStyle } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{
  isMobile: boolean
  loading: boolean
  showSkeleton: boolean
  items: MemberInfo[]
  total: number
  selectedIds: number[]
  query: MemberQuery
}>()

const emit = defineEmits<{
  'selection-change': [rows: MemberInfo[]]
  'toggle-select': [id: number]
  'sort-change': [payload: { prop: string; order: 'ascending' | 'descending' | null }]
  edit: [row: MemberInfo]
  delete: [row: MemberInfo]
  detail: [row: MemberInfo]
  reload: []
}>()

function onSelectionChange(rows: MemberInfo[]) {
  emit('selection-change', rows)
}

function onSortChange(payload: { prop: string; order: 'ascending' | 'descending' | null }) {
  emit('sort-change', payload)
}
</script>

<style scoped>
.member-name {
  font-weight: 600;
  color: var(--ink-900);
}

/* 点击进入成员详情：金色 hover 反馈 */
.member-name--link,
.mr-name--link {
  cursor: pointer;
  transition: color var(--dur-fast);
}

.member-name--link:hover,
.mr-name--link:hover {
  color: var(--gold-700);
}

.mr-link-icon {
  margin-left: 2px;
  font-size: 12px;
  vertical-align: -1px;
  color: var(--ink-300);
  transition: color var(--dur-fast);
}

.mr-name--link:hover .mr-link-icon {
  color: var(--gold-600);
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
  .pagination {
    justify-content: center;
  }
}
</style>

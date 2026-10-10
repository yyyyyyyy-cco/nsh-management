<template>
  <div class="toolbar">
    <div class="toolbar-filters">
      <el-input
        aria-label="搜索ID"
        v-model="query.keyword"
        placeholder="搜索ID"
        clearable
        class="keyword"
        :prefix-icon="Search"
        @keyup.enter="$emit('search')"
        @clear="$emit('search')"
      />
      <el-select
        aria-label="职业筛选"
        v-model="query.profession"
        placeholder="职业筛选"
        clearable
        class="filter"
        @change="$emit('search')"
      >
        <el-option v-for="p in professionStore.activeNames" :key="p" :label="p" :value="p" />
      </el-select>
      <el-select
        aria-label="状态筛选"
        v-model="query.status"
        placeholder="状态筛选"
        clearable
        class="filter"
        @change="$emit('search')"
      >
        <el-option v-for="s in MEMBER_STATUSES" :key="s.value" :label="s.label" :value="s.value" />
      </el-select>
    </div>
    <div class="toolbar-actions">
      <el-button type="primary" :icon="Plus" @click="$emit('create')">添加成员</el-button>
      <el-button :icon="Upload" @click="$emit('import')">Excel 导入</el-button>
      <el-button :icon="Download" :loading="exporting" @click="$emit('export', 'xlsx')">导出 Excel</el-button>
      <el-button :icon="Download" :loading="exporting" @click="$emit('export', 'png')">导出图片</el-button>
      <el-button type="danger" plain :icon="Delete" :disabled="selectedCount === 0" @click="$emit('batch-delete')">
        批量删除
        <span v-if="selectedCount" class="batch-count num">{{ selectedCount }}</span>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Delete, Download, Plus, Search, Upload } from '@element-plus/icons-vue'

import type { MemberQuery } from '@/api/members'
import { useProfessionStore } from '@/stores/profession'
import { MEMBER_STATUSES } from '@/utils/constants'

// `query` 由子组件双向使用（筛选输入与下拉），故声明为 model 而非 prop：
// defineModel 返回 ref，模板中就地更新的是**父组件共享的同一对象**，行为与改前一致（2026-10-03 W2-8）。
const query = defineModel<MemberQuery>('query', { required: true })

const professionStore = useProfessionStore()

defineProps<{ exporting: boolean; selectedCount: number }>()

defineEmits<{
  search: []
  create: []
  import: []
  export: [format: 'xlsx' | 'png']
  'batch-delete': []
}>()
</script>

<style scoped>
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

.keyword {
  width: 220px;
}

.filter {
  width: 140px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
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
}
</style>

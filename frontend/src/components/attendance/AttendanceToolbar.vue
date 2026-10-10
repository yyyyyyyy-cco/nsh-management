<template>
  <div v-if="isAdmin" class="toolbar">
    <el-button type="primary" :loading="loading" @click="$emit('import-formal')">一键导入正式成员</el-button>
    <el-button @click="$emit('import-substitute')">导入替补</el-button>
    <el-button @click="$emit('import-member')">导入成员</el-button>
    <el-button @click="$emit('add-filler')">添加补人</el-button>
    <el-button type="warning" plain :disabled="selectedCount === 0" @click="$emit('batch-leave')">
      批量请假（{{ selectedCount }}）
    </el-button>
    <el-button type="success" plain :disabled="selectedCount === 0" @click="$emit('batch-normal')">
      批量正常
    </el-button>
    <el-button type="warning" plain @click="$emit('import-leave')">导入请假</el-button>
    <el-button type="danger" plain @click="$emit('open-remove')">一键移除</el-button>
    <div class="spacer" />
  </div>

  <!-- ID 搜索 + 职业筛选 -->
  <div class="filter-row">
    <el-input
      aria-label="搜索 ID 过滤"
      v-model="keyword"
      placeholder="搜索 ID 过滤"
      clearable
      :prefix-icon="Search"
      class="keyword-input"
    />
    <el-select aria-label="职业筛选" v-model="professionFilter" placeholder="职业筛选" clearable class="prof-filter">
      <el-option v-for="p in professionStore.activeNames" :key="p" :label="p" :value="p" />
    </el-select>
    <el-select aria-label="类型筛选" v-model="typeFilter" placeholder="类型筛选" clearable class="small-filter">
      <el-option v-for="t in TYPE_OPTIONS" :key="t.value" :label="t.label" :value="t.value" />
    </el-select>
    <el-select aria-label="状态筛选" v-model="statusFilter" placeholder="状态筛选" clearable class="small-filter">
      <el-option v-for="s in STATUS_OPTIONS" :key="s.value" :label="s.label" :value="s.value" />
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { Search } from '@element-plus/icons-vue'

import { useProfessionStore } from '@/stores/profession'

const professionStore = useProfessionStore()

defineProps<{ isAdmin: boolean; loading: boolean; selectedCount: number }>()

defineEmits<{
  'import-formal': []
  'import-substitute': []
  'import-member': []
  'add-filler': []
  'batch-leave': []
  'batch-normal': []
  'import-leave': []
  'open-remove': []
}>()

const keyword = defineModel<string>('keyword', { required: true })
const professionFilter = defineModel<string>('professionFilter', { required: true })
const typeFilter = defineModel<string>('typeFilter', { required: true })
const statusFilter = defineModel<string>('statusFilter', { required: true })

/** 类型筛选选项：正式 / 替补 / 补人。 */
const TYPE_OPTIONS = [
  { value: 'formal', label: '正式' },
  { value: 'substitute', label: '替补' },
  { value: 'filler', label: '补人' },
]

/** 状态筛选选项：正常 / 请假。 */
const STATUS_OPTIONS = [
  { value: 'normal', label: '正常' },
  { value: 'leave', label: '请假' },
]
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.spacer {
  flex: 1;
}

/* ===== ID 搜索框 ===== */
.filter-row {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.filter-row .keyword-input {
  flex: 1;
  max-width: 280px;
  margin-bottom: 0;
}

.filter-row .prof-filter {
  width: 140px;
}

.filter-row .small-filter {
  width: 110px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .toolbar .el-button {
    flex: 1 1 calc(50% - 6px);
    margin-left: 0 !important;
    margin-right: 0;
  }

  .filter-row {
    flex-wrap: wrap;
    gap: 8px;
  }

  .filter-row .keyword-input {
    flex: 1 1 100%;
    max-width: none;
  }

  .filter-row .prof-filter {
    flex: 1 1 100%;
    width: 100%;
  }

  .filter-row .small-filter {
    flex: 1 1 calc(50% - 4px);
    width: 100%;
  }

  .toolbar {
    gap: 6px;
  }

  .spacer {
    display: none;
  }
}

@media (max-width: 480px) {
  .toolbar .el-button {
    font-size: 12px;
    padding-left: 8px;
    padding-right: 8px;
  }
}
</style>

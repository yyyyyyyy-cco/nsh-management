<template>
  <SkeletonTable v-if="showSkeleton && !items.length" variant="table" :rows="5" />
  <el-table v-else :data="items" @selection-change="(rows: AttendanceRecord[]) => $emit('selection-change', rows)">
    <el-table-column v-if="isAdmin" type="selection" width="44" />
    <el-table-column prop="member_name" label="ID" min-width="110" />
    <el-table-column prop="profession" label="职业" min-width="110">
      <template #default="{ row }">
        <el-select
          v-if="isAdmin && (row.professions?.length || 0) > 1"
          :model-value="row.profession"
          style="width: 100px"
          @change="(value: string) => $emit('profession-change', row, value)"
        >
          <el-option v-for="p in row.professions" :key="p" :label="p" :value="p" />
        </el-select>
        <span v-else class="prof-name" :style="{ color: profColor(row.profession) }">{{ row.profession }}</span>
      </template>
    </el-table-column>
    <el-table-column label="类型" min-width="70">
      <template #default="{ row }">
        <el-tag v-if="row.is_filler" type="warning" effect="light" size="small">补人</el-tag>
        <el-tag v-else-if="row.member_status === 'substitute'" type="info" effect="plain" size="small">替补</el-tag>
        <el-tag v-else type="primary" effect="plain" size="small">正式</el-tag>
      </template>
    </el-table-column>
    <el-table-column label="状态" min-width="110">
      <template #default="{ row }">
        <el-switch
          :model-value="row.status === 'normal'"
          inline-prompt
          active-text="正常"
          inactive-text="请假"
          @change="(value: boolean) => $emit('toggle', row, value)"
        />
      </template>
    </el-table-column>
    <el-table-column v-if="isAdmin" label="备注" min-width="140">
      <template #default="{ row }">
        <span class="remark-cell">
          <span class="remark-text" :class="{ 'remark-text--empty': !row.remark }">{{ row.remark || '-' }}</span>
          <el-icon class="remark-edit" title="编辑备注" @click="$emit('edit-remark', row)"><EditPen /></el-icon>
        </span>
      </template>
    </el-table-column>
    <el-table-column v-if="isAdmin" label="操作" min-width="80">
      <template #default="{ row }">
        <el-button link type="danger" @click="$emit('delete', row)">移除</el-button>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import { EditPen } from '@element-plus/icons-vue'

import type { AttendanceRecord } from '@/types/attendance'
import { profColor } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

defineProps<{
  isAdmin: boolean
  showSkeleton: boolean
  items: AttendanceRecord[]
}>()

defineEmits<{
  'selection-change': [rows: AttendanceRecord[]]
  toggle: [row: AttendanceRecord, value: boolean]
  'profession-change': [row: AttendanceRecord, value: string]
  'edit-remark': [row: AttendanceRecord]
  delete: [row: AttendanceRecord]
}>()
</script>

<style scoped>
/* ===== 备注列（桌面表格）：文本 + 编辑入口 ===== */
.remark-cell {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
}

.remark-cell .remark-text {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.remark-text--empty {
  color: var(--ink-300);
}

.remark-edit {
  flex-shrink: 0;
  font-size: 14px;
  color: var(--ink-300);
  cursor: pointer;
}

.remark-edit:hover {
  color: var(--gold-600);
}
</style>

<template>
  <SkeletonTable v-if="showSkeleton && !logs.length" variant="table" :rows="5" />
  <el-table v-else :data="logs" border @row-click="(row: OperationLog) => $emit('select', row)">
    <el-table-column label="时间" min-width="150">
      <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
    </el-table-column>
    <el-table-column label="级别" width="80">
      <template #default="{ row }">
        <el-tag :type="levelTagType(row.level)" effect="light" size="small">
          {{ levelLabel(row.level) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="操作人" min-width="110">
      <template #default="{ row }">
        <span v-if="row.username">{{ row.username }}</span>
        <span v-else class="muted">匿名</span>
        <el-tag v-if="row.role" :type="roleTagType(row.role)" size="small" effect="plain" class="role-tag">
          {{ roleLabel(row.role) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="模块" width="90">
      <template #default="{ row }">{{ moduleLabels[row.module] ?? row.module }}</template>
    </el-table-column>
    <el-table-column label="动作" width="90">
      <template #default="{ row }">
        <el-tag :type="actionTagType(row.action)" size="small" effect="plain">
          {{ actionLabels[row.action] ?? row.action }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="请求" min-width="220" show-overflow-tooltip>
      <template #default="{ row }">
        <span class="method">{{ row.method }}</span>
        <span class="path">{{ row.path }}</span>
      </template>
    </el-table-column>
    <el-table-column label="状态码" width="90">
      <template #default="{ row }">
        <span :class="statusClass(row.status_code)">{{ row.status_code ?? '-' }}</span>
      </template>
    </el-table-column>
    <el-table-column prop="ip" label="IP" min-width="110" show-overflow-tooltip>
      <template #default="{ row }">{{ row.ip || '-' }}</template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import type { OperationLog } from '@/types/log'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

import {
  actionLabels,
  actionTagType,
  formatTime,
  levelLabel,
  levelTagType,
  moduleLabels,
  roleLabel,
  roleTagType,
  statusClass,
} from './logLabels'

defineProps<{ showSkeleton: boolean; logs: OperationLog[] }>()

defineEmits<{ select: [row: OperationLog] }>()
</script>

<style scoped>
.muted {
  color: var(--ink-500, #8a8378);
}

.role-tag {
  margin-left: 4px;
}

.method {
  font-weight: 600;
  margin-right: 6px;
  color: var(--gold-700, #a67c1a);
}

.path {
  font-family: monospace;
  font-size: 12px;
}

.status-ok {
  color: var(--green-600, #4f9d5d);
}

.status-warning {
  color: var(--gold-700, #a67c1a);
}

.status-error {
  color: #c9302c;
  font-weight: 600;
}
</style>

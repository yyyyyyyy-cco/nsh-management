<template>
  <el-dialog v-model="visible" title="日志详情" width="640px">
    <el-descriptions v-if="row" :column="2" border size="small">
      <el-descriptions-item label="时间">{{ formatTime(row.created_at) }}</el-descriptions-item>
      <el-descriptions-item label="级别">{{ levelLabel(row.level) }}</el-descriptions-item>
      <el-descriptions-item label="账号">{{ row.username ?? '匿名' }}</el-descriptions-item>
      <el-descriptions-item label="角色">{{ row.role ? roleLabel(row.role) : '-' }}</el-descriptions-item>
      <el-descriptions-item label="帮会 ID">{{ row.guild_id ?? '-' }}</el-descriptions-item>
      <el-descriptions-item label="IP">{{ row.ip || '-' }}</el-descriptions-item>
      <el-descriptions-item label="模块">{{ moduleLabels[row.module] ?? row.module }}</el-descriptions-item>
      <el-descriptions-item label="动作">{{ actionLabels[row.action] ?? row.action }}</el-descriptions-item>
      <el-descriptions-item label="请求" :span="2">
        {{ row.method }} {{ row.path }}
      </el-descriptions-item>
      <el-descriptions-item label="状态码">{{ row.status_code ?? '-' }}</el-descriptions-item>
    </el-descriptions>
    <div v-if="row?.detail" class="detail-block">
      <div class="detail-title">详细信息</div>
      <pre class="detail-pre">{{ formatDetail(row.detail) }}</pre>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import type { OperationLog } from '@/types/log'

import { actionLabels, formatDetail, formatTime, levelLabel, moduleLabels, roleLabel } from './logLabels'

defineProps<{ row: OperationLog | null }>()

const visible = defineModel<boolean>({ required: true })
</script>

<style scoped>
/* ===== 详情 ===== */
.detail-block {
  margin-top: 12px;
}

.detail-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.detail-pre {
  margin: 0;
  padding: 10px;
  max-height: 240px;
  overflow: auto;
  background: var(--paper-100, #faf6ec);
  border: 1px solid var(--line-300, #e6dfce);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>

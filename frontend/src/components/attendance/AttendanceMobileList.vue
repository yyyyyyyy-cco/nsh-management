<template>
  <div class="att-rows">
    <SkeletonTable v-if="showSkeleton && !items.length" variant="rows" :rows="5" />
    <EmptyState v-else-if="!loading && !items.length" description="暂无出勤记录" :image-size="72" />
    <div v-for="row in items" :key="row.id" class="att-row">
      <div class="ar-main">
        <el-checkbox
          v-if="isAdmin"
          class="ar-check"
          :model-value="selectedIds.includes(row.id)"
          @change="$emit('toggle-select', row.id)"
        />
        <span class="ar-name">{{ row.member_name }}</span>
        <el-tag v-if="row.is_filler" type="warning" effect="light" size="small">补人</el-tag>
        <el-tag v-else-if="row.member_status === 'substitute'" type="info" effect="plain" size="small">替补</el-tag>
        <el-tag v-else type="primary" effect="plain" size="small">正式</el-tag>
        <el-switch
          class="ar-switch"
          :model-value="row.status === 'normal'"
          inline-prompt
          active-text="正常"
          inactive-text="请假"
          @change="(value: boolean) => $emit('toggle', row, value)"
        />
      </div>
      <div class="ar-meta" :class="{ 'ar-meta--indent': isAdmin }">
        <el-select
          aria-label="职业"
          v-if="isAdmin && (row.professions?.length || 0) > 1"
          :model-value="row.profession"
          class="ar-prof-select"
          @change="(value: string) => $emit('profession-change', row, value)"
        >
          <el-option v-for="p in row.professions" :key="p" :label="p" :value="p" />
        </el-select>
        <span v-else class="prof-name" :style="{ color: profColor(row.profession) }">{{ row.profession }}</span>
        <el-icon v-if="isAdmin" class="ar-remark-edit" title="编辑备注" @click="$emit('edit-remark', row)"
          ><EditPen
        /></el-icon>
        <el-button v-if="isAdmin" class="ar-act" type="danger" plain @click="$emit('delete', row)">移除</el-button>
      </div>
      <div v-if="isAdmin && row.remark" class="ar-remark">备注：{{ row.remark }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { EditPen } from '@element-plus/icons-vue'

import type { AttendanceRecord } from '@/types/attendance'
import { profColor } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'

defineProps<{
  isAdmin: boolean
  loading: boolean
  showSkeleton: boolean
  items: AttendanceRecord[]
  selectedIds: number[]
}>()

defineEmits<{
  'toggle-select': [id: number]
  toggle: [row: AttendanceRecord, value: boolean]
  'profession-change': [row: AttendanceRecord, value: string]
  'edit-remark': [row: AttendanceRecord]
  delete: [row: AttendanceRecord]
}>()
</script>

<style scoped>
/* ===== 移动端行列表（isMobile 时渲染，替换表格） ===== */
.att-rows {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态/加载遮罩的占位高度 */
  touch-action: manipulation;
}

.att-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.att-row:last-child {
  border-bottom: none;
}

.ar-main {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

.ar-check {
  flex-shrink: 0;
  padding: 10px 6px 10px 0;
}

.ar-name {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--ink-900);
}

.ar-main .el-tag {
  flex-shrink: 0;
}

.ar-switch {
  margin-left: auto;
  flex-shrink: 0;
}

.ar-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

/* 管理员行（勾选区存在）职业与上方 ID 对齐（约 2 个字符宽） */
.ar-meta--indent {
  padding-left: 28px;
}

.ar-prof-select {
  width: 110px;
  flex-shrink: 0;
}

/* 备注编辑入口（动作行内，管理员）：占据剩余空间把移除按钮推向右侧 */
.ar-remark-edit {
  margin-left: auto;
  flex-shrink: 0;
  padding: 6px 4px;
  font-size: 20px;
  color: var(--ink-400);
  cursor: pointer;
}

.ar-remark-edit:active {
  color: var(--gold-600);
}

/* 出勤备注行（仅管理员可见，与职业/ID 左对齐） */
.ar-remark {
  margin-top: 6px;
  padding-left: 28px;
  font-size: 12px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

/* 紧凑移除按钮：32px、右对齐（与常驻库/日程行列表同款） */
.ar-meta .el-button.ar-act {
  height: 32px;
  margin-left: 0;
  padding: 0 14px;
  border-radius: var(--radius-md);
  font-size: 13px;
  font-weight: 600;
}
</style>

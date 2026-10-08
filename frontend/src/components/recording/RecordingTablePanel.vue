<template>
  <SkeletonTable v-if="showSkeleton && items.length === 0" variant="table" :rows="5" />
  <el-table
    v-else
    :data="items"
    :row-key="rowKey"
    :default-sort="{ prop: 'member_name', order: 'ascending' }"
    @selection-change="(rows: Recording[]) => $emit('selection-change', rows)"
  >
    <el-table-column v-if="isAdmin" type="selection" width="44" reserve-selection />
    <el-table-column prop="member_name" label="ID" min-width="100" sortable />
    <el-table-column prop="profession" label="职业" min-width="80" sortable>
      <template #default="{ row }">
        <span class="prof-cell">
          <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
          {{ row.profession || '-' }}
        </span>
      </template>
    </el-table-column>
    <el-table-column label="局数" min-width="60" align="center">
      <template #default="{ row }">第{{ row.round_number }}局</template>
    </el-table-column>
    <el-table-column label="录屏链接" min-width="280">
      <template #default="{ row }">
        <div v-if="editingId === row.id" class="url-edit">
          <el-input aria-label="请输入录屏链接" v-model="editingUrl" placeholder="请输入录屏链接" size="small" />
          <el-button type="primary" size="small" @click="$emit('submit', row)">保存</el-button>
          <el-button size="small" @click="$emit('cancel-edit')">取消</el-button>
        </div>
        <div v-else-if="row.url" class="url-display">
          <a v-if="isAdmin" :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link">{{
            row.url
          }}</a>
          <span v-else class="submitted-hint">已提交</span>
          <el-button
            v-if="isAdmin"
            link
            type="primary"
            size="small"
            :icon="CopyDocument"
            title="复制链接"
            @click="$emit('copy-url', row.url)"
          />
          <el-button v-if="!isAdmin" link type="primary" size="small" @click="$emit('start-edit', row)">修改</el-button>
        </div>
        <div v-else>
          <el-button v-if="!isAdmin" type="primary" link size="small" @click="$emit('start-edit', row)">
            提交链接
          </el-button>
          <span v-else class="empty-url">未提交</span>
        </div>
      </template>
    </el-table-column>
    <el-table-column label="备注" min-width="150">
      <template #default="{ row }">
        <!-- 管理员：可见备注内容 -->
        <template v-if="isAdmin">
          <span v-if="row.note">{{ row.note }}</span>
          <span v-else class="empty-remark">-</span>
        </template>
        <!-- 帮众：仅可见状态与编辑入口，不回显内容 -->
        <template v-else>
          <div v-if="editingNoteId === row.id" class="note-edit">
            <el-input
              aria-label="备注"
              v-model="editingNote"
              type="textarea"
              :autosize="{ minRows: 2, maxRows: 5 }"
              placeholder="备注（仅管理员可见）"
              size="small"
            />
            <div class="note-edit__btns">
              <el-button type="primary" size="small" @click="$emit('submit-note', row)">保存</el-button>
              <el-button size="small" @click="$emit('cancel-note-edit')">取消</el-button>
            </div>
          </div>
          <div v-else-if="row.note" class="note-display">
            <span class="submitted-hint">已备注</span>
            <el-button link type="primary" size="small" @click="$emit('start-note-edit', row)">修改</el-button>
          </div>
          <div v-else>
            <el-button type="primary" link size="small" @click="$emit('start-note-edit', row)">添加备注</el-button>
          </div>
        </template>
      </template>
    </el-table-column>
    <el-table-column label="状态" min-width="90" align="center">
      <template #default="{ row }">
        <el-tag :type="statusType(row.status)" effect="light" size="small">
          {{ statusLabel(row.status) }}
        </el-tag>
      </template>
    </el-table-column>
    <el-table-column label="审核备注" min-width="150">
      <template #default="{ row }">
        <span v-if="row.review_remark">{{ row.review_remark }}</span>
        <span v-else class="empty-remark">-</span>
      </template>
    </el-table-column>
    <el-table-column v-if="isAdmin" label="操作" min-width="150">
      <template #default="{ row }">
        <template v-if="row.url">
          <el-button v-if="row.status !== 'approved'" link type="success" @click="$emit('approve', row)"
            >通过</el-button
          >
          <el-button v-if="row.status !== 'rejected'" link type="danger" @click="$emit('reject', row)">驳回</el-button>
        </template>
        <span v-else class="empty-action">-</span>
      </template>
    </el-table-column>
  </el-table>
</template>

<script setup lang="ts">
import { CopyDocument } from '@element-plus/icons-vue'

import type { Recording } from '@/types/recording'
import { profColor } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import { normalizeUrl, statusLabel, statusType } from '@/composables/useRecordingList'

defineProps<{
  isAdmin: boolean
  showSkeleton: boolean
  items: Recording[]
  editingId: number | null
  editingNoteId: number | null
}>()

defineEmits<{
  'selection-change': [rows: Recording[]]
  'copy-url': [url: string]
  'start-edit': [row: Recording]
  'start-note-edit': [row: Recording]
  'cancel-edit': []
  'cancel-note-edit': []
  submit: [row: Recording]
  'submit-note': [row: Recording]
  approve: [row: Recording]
  reject: [row: Recording]
}>()

const editingUrl = defineModel<string>('editingUrl', { required: true })
const editingNote = defineModel<string>('editingNote', { required: true })

/** 表格行 key（配合 reserve-selection 跨页保留勾选）。 */
const rowKey = (row: Recording) => row.id
</script>

<style scoped src="./recording-shared.css"></style>

<style scoped>
.url-edit {
  display: flex;
  gap: 8px;
  align-items: center;
}

.url-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 帮众视角：链接脱敏，仅显示已提交状态 */
.submitted-hint {
  font-size: 12px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 1px 10px;
  font-weight: 500;
}

.empty-remark,
.empty-action {
  color: var(--ink-300);
}

/* 桌面端备注编辑（表格单元格内） */
.note-edit {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.note-edit__btns {
  display: flex;
  gap: 6px;
}

.note-display {
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>

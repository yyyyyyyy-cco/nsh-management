<template>
  <div class="rec-list">
    <SkeletonTable v-if="showSkeleton && items.length === 0" variant="rows" :rows="5" />
    <EmptyState v-else-if="!loading && items.length === 0" description="暂无录屏记录" :image-size="72" />
    <div v-for="row in items" :key="row.id" class="rec-row" :class="{ 'rec-row--admin': isAdmin }">
      <div class="rec-row__main">
        <el-checkbox
          v-if="isAdmin"
          class="rec-row__check"
          :model-value="selectedIds.includes(row.id)"
          @change="$emit('toggle-select', row.id)"
        />
        <span class="rec-row__name">{{ row.member_name }}</span>
        <!-- 帮众：ID 旁的提交状态胶囊 -->
        <template v-if="!isAdmin">
          <span v-if="row.url" class="rec-row__state">已提交</span>
          <span v-if="row.note" class="rec-row__state">已备注</span>
        </template>
        <el-tag class="rec-row__status" :type="statusType(row.status)" effect="light" size="small">
          {{ statusLabel(row.status) }}
        </el-tag>
      </div>
      <div class="rec-row__meta">
        <span class="prof-cell">
          <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
          {{ row.profession || '-' }}
        </span>
        <span class="rec-row__round">第{{ row.round_number }}局</span>
      </div>

      <div v-if="row.review_remark" class="rec-row__remark">审核备注：{{ row.review_remark }}</div>

      <!-- 行内编辑：录屏链接 -->
      <div v-if="editingId === row.id" class="rec-row__edit">
        <el-input v-model="editingUrl" placeholder="请输入录屏链接" size="small" />
        <div class="rec-row__edit-btns">
          <el-button type="primary" @click="$emit('submit', row)">保存</el-button>
          <el-button @click="$emit('cancel-edit')">取消</el-button>
        </div>
      </div>

      <!-- 行内编辑：备注（仅管理员可见，提交后不回显） -->
      <div v-else-if="editingNoteId === row.id" class="rec-row__edit">
        <el-input
          v-model="editingNote"
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 5 }"
          placeholder="备注（仅管理员可见，可填写任何内容）"
        />
        <div class="rec-row__edit-btns">
          <el-button type="primary" @click="$emit('submit-note', row)">保存备注</el-button>
          <el-button @click="$emit('cancel-note-edit')">取消</el-button>
        </div>
      </div>

      <!-- 帮众：提交/修改链接 + 备注（状态胶囊见 ID 旁） -->
      <div v-else-if="!isAdmin" class="rec-row__actions">
        <el-button class="rec-act rec-act--link" @click="$emit('start-edit', row)">
          {{ row.url ? '修改链接' : '提交链接' }}
        </el-button>
        <el-button class="rec-act rec-act--note" @click="$emit('start-note-edit', row)">
          {{ row.note ? '修改备注' : '备注' }}
        </el-button>
      </div>

      <!-- 管理员：备注 + 链接 + 复制 + 审核 -->
      <div v-else class="rec-row__admin">
        <div v-if="row.note" class="rec-row__remark">备注：{{ row.note }}</div>
        <div class="rec-row__linkline">
          <template v-if="row.url">
            <a :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link rec-row__url">{{ row.url }}</a>
            <el-button link type="primary" size="small" :icon="CopyDocument" title="复制链接" @click="$emit('copy-url', row.url)" />
          </template>
          <span v-else class="empty-url">未提交</span>
        </div>
        <div v-if="row.url" class="rec-row__actions">
          <el-button v-if="row.status !== 'approved'" class="rec-act" type="success" plain @click="$emit('approve', row)">通过</el-button>
          <el-button v-if="row.status !== 'rejected'" class="rec-act" type="danger" plain @click="$emit('reject', row)">驳回</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { CopyDocument } from '@element-plus/icons-vue'

import type { Recording } from '@/types/recording'
import { profColor } from '@/utils/profession'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import EmptyState from '@/components/common/EmptyState.vue'
import { normalizeUrl, statusLabel, statusType } from '@/composables/useRecordingList'

defineProps<{
  isAdmin: boolean
  loading: boolean
  showSkeleton: boolean
  items: Recording[]
  selectedIds: number[]
  editingId: number | null
  editingNoteId: number | null
}>()

defineEmits<{
  'toggle-select': [id: number]
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
</script>

<style scoped src="./recording-shared.css"></style>

<style scoped>
/* ===== 移动端行列表（isMobile 时渲染） ===== */
.rec-list {
  display: flex;
  flex-direction: column;
  min-height: 140px; /* 空态/加载遮罩的占位高度 */
  touch-action: manipulation;
}

.rec-row {
  padding: 12px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.rec-row:last-child {
  border-bottom: none;
}

.rec-row__main {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.rec-row__check {
  flex-shrink: 0;
  padding: 10px 6px 10px 0;
}

.rec-row__name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
  color: var(--ink-900);
}

/* 次要信息行：职业 · 局数 */
.rec-row__meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 3px;
  font-size: 12.5px;
  color: var(--ink-500);
}

.rec-row__meta .prof-cell {
  flex-shrink: 0;
}

.rec-row__round {
  flex-shrink: 0;
  font-size: 12.5px;
  color: var(--ink-500);
}

.rec-row__meta .rec-row__round::before {
  content: '·';
  margin-right: 6px;
  color: var(--ink-300);
}

.rec-row__status {
  flex-shrink: 0;
  margin-left: auto;
}

.rec-row__remark {
  margin-top: 6px;
  font-size: 12px;
  color: var(--ink-500);
  overflow-wrap: anywhere;
}

.rec-row__edit {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 10px;
}

.rec-row__edit-btns {
  display: flex;
  gap: 8px;
}

.rec-row__edit-btns .el-button {
  flex: 1;
  min-height: 44px;
  margin-left: 0;
}

.rec-row__actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

/* 提交状态胶囊：已提交/已备注（手机端行内强提示） */
.rec-row__state {
  flex-shrink: 0;
  font-size: 11.5px;
  font-weight: 600;
  color: var(--gold-700);
  background: var(--gold-100);
  border: 1px solid var(--gold-200);
  border-radius: var(--radius-xl);
  padding: 3px 10px;
  line-height: 1.4;
  white-space: nowrap;
}

.rec-row__actions .el-button.rec-act {
  flex: 1;
  min-height: 44px;
  margin-left: 0;
  border-radius: var(--radius-md);
  font-weight: 600;
}

/* 提交链接：鎏金描边（规避 primary+plain 与主题渐变叠加的浑浊观感） */
.rec-row__actions .el-button.rec-act--link {
  background: var(--gold-50);
  border: 1px solid var(--gold-300);
  color: var(--gold-700);
}

.rec-row__actions .el-button.rec-act--link:active {
  background: var(--gold-100);
  border-color: var(--gold-400);
}

/* 备注：墨色描边（次要动作） */
.rec-row__actions .el-button.rec-act--note {
  background: var(--ink-bg-paper);
  border: 1px solid var(--edge-strong);
  color: var(--ink-700);
}

.rec-row__actions .el-button.rec-act--note:active {
  background: var(--ink-bg-wash);
  border-color: var(--gold-300);
  color: var(--gold-700);
}

.rec-row__admin {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
}

.rec-row__linkline {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}

/* 管理员行（勾选区存在）：职业/链接/备注行缩进约 2 字符宽，与 ID 对齐 */
.rec-row--admin .rec-row__meta,
.rec-row--admin .rec-row__linkline,
.rec-row--admin .rec-row__remark {
  padding-left: 28px;
}

.rec-row__url {
  flex: 1;
  min-width: 0;
  max-width: none;
}
</style>

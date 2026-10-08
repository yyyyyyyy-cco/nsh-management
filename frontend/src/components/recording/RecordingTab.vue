<template>
  <div class="recording-tab">
    <RecordingProgressBar
      :progress="progress"
      :round-filter="roundFilter"
      @toggle-round="toggleRound"
      @clear-round="roundFilter = null"
    />

    <!-- 工具栏：按ID搜索（帮众/管理员）+ 管理员操作 -->
    <div class="toolbar">
      <el-input
        aria-label="按ID搜索"
        v-model="nameFilter"
        placeholder="按ID搜索"
        clearable
        style="width: 200px"
        :prefix-icon="Search"
      />
      <template v-if="auth.isAdmin">
        <el-button type="success" plain :disabled="selectedIds.length === 0" @click="onBatchApprove">
          批量审核通过（{{ selectedIds.length }}）
        </el-button>
        <el-select aria-label="状态筛选" v-model="statusFilter" placeholder="状态筛选" clearable style="width: 120px">
          <el-option label="待审核" value="pending" />
          <el-option label="未提交" value="unsubmitted" />
          <el-option label="已通过" value="approved" />
          <el-option label="已驳回" value="rejected" />
        </el-select>
      </template>
    </div>

    <!-- 移动端（≤768px）行列表 / 桌面端表格 -->
    <RecordingMobileList
      v-if="isMobile"
      :is-admin="auth.isAdmin"
      :loading="loading"
      :show-skeleton="showSkeleton"
      :items="pagedItems"
      :selected-ids="selectedIds"
      :editing-id="editingId"
      :editing-note-id="editingNoteId"
      v-model:editingUrl="editingUrl"
      v-model:editingNote="editingNote"
      @toggle-select="toggleSelect"
      @copy-url="onCopyUrl"
      @start-edit="startEdit"
      @start-note-edit="startNoteEdit"
      @cancel-edit="editingId = null"
      @cancel-note-edit="editingNoteId = null"
      @submit="onSubmit"
      @submit-note="onSubmitNote"
      @approve="onApprove"
      @reject="onReject"
    />
    <RecordingTablePanel
      v-else
      :is-admin="auth.isAdmin"
      :show-skeleton="showSkeleton"
      :items="pagedItems"
      :editing-id="editingId"
      :editing-note-id="editingNoteId"
      v-model:editingUrl="editingUrl"
      v-model:editingNote="editingNote"
      @selection-change="onSelectionChange"
      @copy-url="onCopyUrl"
      @start-edit="startEdit"
      @start-note-edit="startNoteEdit"
      @cancel-edit="editingId = null"
      @cancel-note-edit="editingNoteId = null"
      @submit="onSubmit"
      @submit-note="onSubmitNote"
      @approve="onApprove"
      @reject="onReject"
    />

    <!-- 分页：录屏行为「成员 × 局数」量级（数十至数百行），分页渲染避免全量 DOM 与控件开销 -->
    <div v-if="filteredItems.length > 0" class="pager">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="filteredItems.length"
        :page-sizes="[20, 50, 100]"
        layout="total, sizes, prev, pager, next"
        background
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { Search } from '@element-plus/icons-vue'

import { useAuthStore } from '@/stores/auth'
import { useRecordingList } from '@/composables/useRecordingList'
import RecordingMobileList from '@/components/recording/RecordingMobileList.vue'
import RecordingProgressBar from '@/components/recording/RecordingProgressBar.vue'
import RecordingTablePanel from '@/components/recording/RecordingTablePanel.vue'

const props = defineProps<{ scheduleId: number }>()

const auth = useAuthStore()

// 数据与操作逻辑（见 composables/useRecordingList）
const {
  loading,
  showSkeleton,
  progress,
  selectedIds,
  statusFilter,
  nameFilter,
  roundFilter,
  editingId,
  editingUrl,
  editingNoteId,
  editingNote,
  filteredItems,
  pagedItems,
  page,
  pageSize,
  toggleRound,
  onCopyUrl,
  load,
  onSelectionChange,
  toggleSelect,
  startEdit,
  startNoteEdit,
  onSubmitNote,
  onSubmit,
  onApprove,
  onReject,
  onBatchApprove,
} = useRecordingList(props)

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))

/** Tab 重新激活时刷新（出勤库变动后同步成员与进度）。 */
function reload() {
  load()
}

defineExpose({ reload })
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

/* 分页条：底部右对齐 */
.pager {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }

  .toolbar .el-button,
  .toolbar .el-select {
    flex: 1;
  }

  .toolbar .el-input {
    flex: 1 1 100%;
    width: 100% !important;
  }
}
</style>

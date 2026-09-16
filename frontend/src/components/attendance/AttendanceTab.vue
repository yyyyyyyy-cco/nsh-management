<template>
  <div class="attendance-tab">
    <AttendanceStatsBar
      :stats="stats"
      :has-gap-target="hasGapTarget"
      :profession-gap="professionGap"
      :custom-config="customConfig"
      :is-admin="auth.isAdmin"
      @open-config="profCfgVisible = true"
    />

    <AttendanceToolbar
      :is-admin="auth.isAdmin"
      :loading="loading"
      :selected-count="selectedIds.length"
      v-model:keyword="keyword"
      v-model:professionFilter="professionFilter"
      v-model:typeFilter="typeFilter"
      v-model:statusFilter="statusFilter"
      @import-formal="onImportFormal"
      @import-substitute="substituteVisible = true"
      @import-member="memberImportVisible = true"
      @add-filler="fillerVisible = true"
      @batch-leave="onBatch('leave')"
      @batch-normal="onBatch('normal')"
      @import-leave="leaveImportVisible = true"
      @open-remove="onOpenRemove"
    />

    <!-- 移动端（≤768px）行列表 / 桌面端表格 -->
    <AttendanceMobileList
      v-if="isMobile"
      :is-admin="auth.isAdmin"
      :loading="loading"
      :show-skeleton="showSkeleton"
      :items="filteredItems"
      :selected-ids="selectedIds"
      @toggle-select="toggleSelect"
      @toggle="onToggle"
      @profession-change="onProfessionChange"
      @edit-remark="onEditRemark"
      @delete="onDelete"
    />
    <AttendanceTablePanel
      v-else
      :is-admin="auth.isAdmin"
      :show-skeleton="showSkeleton"
      :items="filteredItems"
      @selection-change="onSelectionChange"
      @toggle="onToggle"
      @profession-change="onProfessionChange"
      @edit-remark="onEditRemark"
      @delete="onDelete"
    />

    <FillerDialog v-model="fillerVisible" :schedule-id="scheduleId" @success="load" />
    <SubstituteImportDialog v-model="substituteVisible" :schedule-id="scheduleId" @success="load" />
    <LeaveImportDialog v-model="leaveImportVisible" :schedule-id="scheduleId" :records="items" @success="load" />
    <ImportMemberDialog v-model="memberImportVisible" :schedule-id="scheduleId" @success="load" />
    <ProfessionConfigDialog
      v-model:visible="profCfgVisible"
      :schedule-id="scheduleId"
      :initial="effectiveTargets"
      :has-custom="!!customConfig"
      @saved="onProfessionConfigSaved"
    />

    <!-- 一键移除：候选池中未被排入排表的已出勤（正常）成员 -->
    <el-dialog v-model="removeVisible" title="移除未排入排表的人员" width="min(420px, 92vw)" append-to-body>
      <div class="remove-hint">
        以下成员已出勤（正常），但在排表候选池中未被排入排表，确认后将移出出勤表：
      </div>
      <el-checkbox-group v-model="removeSelected" class="remove-list">
        <el-checkbox v-for="r in removableItems" :key="r.id" :value="r.member_name" class="remove-item">
          <span class="remove-item__name">{{ r.member_name }}</span>
          <span class="remove-item__prof" :style="{ color: profColor(r.profession) }">{{ r.profession }}</span>
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <el-button @click="removeVisible = false">取消</el-button>
        <el-button type="danger" :disabled="removeSelected.length === 0" @click="onConfirmRemove">
          移除（{{ removeSelected.length }}）
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'

import type { ScheduleInfo } from '@/types/schedule'
import { useAuthStore } from '@/stores/auth'
import { useAttendanceList } from '@/composables/useAttendanceList'
import { profColor } from '@/utils/profession'
import AttendanceMobileList from '@/components/attendance/AttendanceMobileList.vue'
import AttendanceStatsBar from '@/components/attendance/AttendanceStatsBar.vue'
import AttendanceTablePanel from '@/components/attendance/AttendanceTablePanel.vue'
import AttendanceToolbar from '@/components/attendance/AttendanceToolbar.vue'
import FillerDialog from '@/components/attendance/FillerDialog.vue'
import ImportMemberDialog from '@/components/attendance/ImportMemberDialog.vue'
import LeaveImportDialog from '@/components/attendance/LeaveImportDialog.vue'
import ProfessionConfigDialog from '@/components/attendance/ProfessionConfigDialog.vue'
import SubstituteImportDialog from '@/components/attendance/SubstituteImportDialog.vue'

const props = defineProps<{ scheduleId: number; schedule: ScheduleInfo }>()

const auth = useAuthStore()

// 数据与操作逻辑（见 composables/useAttendanceList）
const {
  loading,
  showSkeleton,
  items,
  stats,
  selectedIds,
  keyword,
  professionFilter,
  typeFilter,
  statusFilter,
  customConfig,
  profCfgVisible,
  removeVisible,
  removableItems,
  removeSelected,
  filteredItems,
  effectiveTargets,
  hasGapTarget,
  professionGap,
  load,
  onSelectionChange,
  toggleSelect,
  onProfessionChange,
  onEditRemark,
  onProfessionConfigSaved,
  onImportFormal,
  onToggle,
  onBatch,
  onDelete,
  onOpenRemove,
  onConfirmRemove,
} = useAttendanceList(props)

const fillerVisible = ref(false)
const substituteVisible = ref(false)
const leaveImportVisible = ref(false)
const memberImportVisible = ref(false)

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
  selectedIds.value = [] // 形态切换时清空勾选，避免残留「看不见的已勾选」
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped>
/* ===== 出勤状态开关（浅金风，颜色更浅更柔和） ===== */
.attendance-tab :deep(.el-switch.is-checked .el-switch__core) {
  background: linear-gradient(135deg, #f0e0a8 0%, #e8cd72 100%);
  border-color: transparent;
}

.attendance-tab :deep(.el-switch .el-switch__core) {
  border-radius: 999px;
}

.attendance-tab :deep(.el-switch__inner) {
  font-size: 12px;
}

/* ===== 一键移除弹窗 ===== */
.remove-hint {
  font-size: 12px;
  color: var(--ink-500);
  margin-bottom: 12px;
  line-height: 1.6;
}

.remove-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  max-height: 300px;
  overflow-y: auto;
  padding: 4px 2px;
}

.remove-item {
  display: flex;
  align-items: center;
  width: 100%;
  margin-right: 0;
  padding: 4px 8px;
  border-radius: var(--radius-md);
}

.remove-item:hover {
  background: var(--gold-50);
}

.remove-item__name {
  font-weight: 600;
  color: var(--ink-800);
  margin-right: 8px;
}

.remove-item__prof {
  font-size: 12px;
}

@media (max-width: 768px) {
  /* 状态开关隐藏外置文字，仅靠开关颜色/滑块标识状态，节省列宽 */
  .attendance-tab :deep(.el-switch__label--left),
  .attendance-tab :deep(.el-switch__label--right) {
    display: none;
  }

  /* inline-prompt 内部文字缩小，避免窄屏溢出 */
  .attendance-tab :deep(.el-switch__inner) {
    font-size: 11px;
  }
}
</style>

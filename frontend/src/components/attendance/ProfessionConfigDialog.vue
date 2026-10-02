<template>
  <el-dialog
    :model-value="visible"
    title="修改本场职业配置"
    width="400px"
    append-to-body
    @update:model-value="emit('update:visible', $event)"
    @open="initForm"
  >
    <el-alert
      type="info"
      :closable="false"
      class="tip"
      title="保存后仅本场生效，不影响系统配置；恢复默认后沿用系统配置的职业目标。"
    />
    <div class="cfg-list">
      <div v-for="p in PROF_ORDER" :key="p" class="cfg-row">
        <span class="prof-name" :style="{ color: profColor(p) }">{{ p }}</span>
        <el-input-number
          v-model="form[p]"
          :min="0"
          :max="60"
          size="small"
          controls-position="right"
          class="cfg-input"
        />
      </div>
    </div>
    <template #footer>
      <el-button v-if="hasCustom" type="warning" plain :loading="loading" @click="onReset">恢复默认</el-button>
      <el-button @click="emit('update:visible', false)">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { updateScheduleProfessionConfig } from '@/api/schedules'
import { PROF_ORDER } from '@/composables/lineupBoard'
import { profColor } from '@/utils/profession'

const props = defineProps<{
  visible: boolean
  scheduleId: number
  /** 当前生效目标人数（单场覆盖或系统配置），打开弹窗时作为初始值。 */
  initial: Record<string, number>
  /** 是否已存在单场自定义配置（决定是否显示「恢复默认」）。 */
  hasCustom: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'saved', configs: Record<string, number> | null): void
}>()

const loading = ref(false)
const form = ref<Record<string, number>>({})

/** 打开弹窗时以当前生效配置初始化表单。 */
function initForm() {
  const next: Record<string, number> = {}
  for (const p of PROF_ORDER) next[p] = props.initial[p] ?? 0
  form.value = next
}

async function onSave() {
  loading.value = true
  try {
    const schedule = await updateScheduleProfessionConfig(props.scheduleId, form.value)
    emit('saved', schedule.profession_config ?? form.value)
    ElMessage.success('已保存本场职业配置')
  } finally {
    loading.value = false
  }
}

async function onReset() {
  await ElMessageBox.confirm('确定恢复默认吗？本场将沿用系统配置的职业目标。', '提示', { type: 'warning' })
  loading.value = true
  try {
    await updateScheduleProfessionConfig(props.scheduleId, null)
    emit('saved', null)
    ElMessage.success('已恢复默认（沿用系统配置）')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tip {
  margin-bottom: 14px;
}

.cfg-list {
  max-height: 340px;
  overflow-y: auto;
}

.cfg-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.cfg-row:last-child {
  border-bottom: none;
}

.prof-name {
  font-size: 13px;
  font-weight: 700;
}

.cfg-input {
  width: 110px;
}
</style>

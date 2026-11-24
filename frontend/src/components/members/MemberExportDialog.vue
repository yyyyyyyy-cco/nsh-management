<template>
  <el-dialog v-model="visible" :title="title" width="420px" destroy-on-close append-to-body>
    <p class="tip">选择要导出的成员类型（至少一类），当前关键词与职业筛选继续生效。</p>
    <el-checkbox-group v-model="selected" class="status-group">
      <el-checkbox v-for="item in MEMBER_STATUSES" :key="item.value" :value="item.value">
        {{ item.label }}
      </el-checkbox>
    </el-checkbox-group>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" :disabled="selected.length === 0" @click="onConfirm">
        导出
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { MEMBER_STATUSES } from '@/utils/constants'

const props = defineProps<{
  modelValue: boolean
  format: 'xlsx' | 'png'
  defaultStatuses: string[]
  loading: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  confirm: [statuses: string[]]
}>()

const selected = ref<string[]>([])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const title = computed(() => (props.format === 'xlsx' ? '导出 Excel' : '导出图片'))

watch(
  () => props.modelValue,
  (open) => {
    if (open) selected.value = [...props.defaultStatuses]
  },
)

function onConfirm() {
  const statuses = MEMBER_STATUSES.filter((item) => selected.value.includes(item.value)).map((item) => item.value)
  if (statuses.length === 0) return
  emit('confirm', statuses)
}
</script>

<style scoped>
.tip {
  margin: 0 0 14px;
  color: var(--ink-500);
  font-size: 13px;
  line-height: 1.6;
}

.status-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>

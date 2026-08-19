<template>
  <el-dialog v-model="visible" title="导入替补成员" width="480px" destroy-on-close>
    <el-alert
      v-if="candidates.length === 0"
      type="info"
      :closable="false"
      class="tip"
      title="暂无可导入的替补成员"
    />
    <el-table v-else :data="candidates" size="small" max-height="360" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="44" />
      <el-table-column prop="name" label="ID" min-width="100" />
      <el-table-column prop="main_profession" label="主职业" min-width="80" />
      <el-table-column label="副职业" min-width="80">
        <template #default="{ row }">{{ row.sub_profession || '-' }}</template>
      </el-table-column>
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
    </el-table>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" :disabled="selected.length === 0" @click="onImport">
        导入（{{ selected.length }}）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'

import { getSubstituteCandidates, importSubstitutes } from '@/api/attendance'
import type { SubstituteCandidate } from '@/types/attendance'

const props = defineProps<{ scheduleId: number }>()
const emit = defineEmits<{ success: [] }>()
const visible = defineModel<boolean>({ required: true })

const loading = ref(false)
const candidates = ref<SubstituteCandidate[]>([])
const selected = ref<SubstituteCandidate[]>([])

watch(visible, (v) => {
  if (v) load()
})

async function load() {
  try {
    candidates.value = await getSubstituteCandidates(props.scheduleId)
  } catch {
    // 错误提示已由 http 拦截器统一处理
    candidates.value = []
  }
  selected.value = []
}

function onSelectionChange(rows: SubstituteCandidate[]) {
  selected.value = rows
}

async function onImport() {
  loading.value = true
  try {
    const result = await importSubstitutes(
      props.scheduleId,
      selected.value.map((m) => m.id),
    )
    ElMessage.success(result.message)
    visible.value = false
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tip {
  margin-bottom: 8px;
}
</style>

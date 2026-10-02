<template>
  <el-dialog v-model="visible" title="导入常驻库成员" width="520px" destroy-on-close append-to-body>
    <el-alert
      v-if="candidates.length === 0"
      type="info"
      :closable="false"
      class="tip"
      title="常驻库中暂无未导入的成员"
    />
    <template v-else>
      <!-- 搜索过滤 -->
      <el-input
        v-model="keyword"
        placeholder="搜索 ID 过滤"
        clearable
        :prefix-icon="Search"
        class="search-input"
      />
      <el-table
        :data="filtered"
        size="small"
        max-height="360"
        @selection-change="onSelectionChange"
      >
        <el-table-column type="selection" width="44" />
        <el-table-column prop="name" label="ID" min-width="90" />
        <el-table-column prop="main_profession" label="主职业" min-width="80" />
        <el-table-column label="副职业" min-width="80">
          <template #default="{ row }">{{ row.sub_profession || '-' }}</template>
        </el-table-column>
        <el-table-column label="类型" min-width="60">
          <template #default="{ row }">
            <el-tag v-if="row.member_status === 'substitute'" type="info" effect="plain" size="small">替补</el-tag>
            <el-tag v-else type="primary" effect="plain" size="small">正式</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="remark" label="备注" min-width="100" show-overflow-tooltip />
      </el-table>
    </template>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" :disabled="selected.length === 0" @click="onImport">
        导入（{{ selected.length }}）
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { getMemberCandidates, importAttendanceMembers } from '@/api/attendance'
import type { SubstituteCandidate } from '@/types/attendance'

const props = defineProps<{ scheduleId: number }>()
const emit = defineEmits<{ success: [] }>()
const visible = defineModel<boolean>({ required: true })

const loading = ref(false)
const candidates = ref<SubstituteCandidate[]>([])
const selected = ref<SubstituteCandidate[]>([])
const keyword = ref('')

const filtered = computed(() => {
  if (!keyword.value) return candidates.value
  const kw = keyword.value.toLowerCase()
  return candidates.value.filter((c) => c.name.toLowerCase().includes(kw))
})

watch(visible, (v) => {
  if (v) {
    keyword.value = ''
    load()
  }
})

async function load() {
  try {
    candidates.value = await getMemberCandidates(props.scheduleId)
  } catch {
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
    const result = await importAttendanceMembers(
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

.search-input {
  margin-bottom: 10px;
}
</style>
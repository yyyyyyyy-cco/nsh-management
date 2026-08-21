<template>
  <el-dialog v-model="visible" title="Excel 导入成员" width="520px" destroy-on-close append-to-body>
    <el-alert type="info" :closable="false" class="tip">
      表头格式：姓名、主职业、副职业（可选）、状态（正式/替补）、备注（可选）。重名成员自动跳过。
    </el-alert>
    <el-upload
      drag
      :auto-upload="false"
      :limit="1"
      accept=".xlsx,.xls"
      :on-change="onFileChange"
      :on-remove="onFileRemove"
      class="uploader"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">拖拽文件到此处，或 <em>点击选择</em></div>
    </el-upload>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" :disabled="!file" @click="onImport">开始导入</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage, type UploadFile } from 'element-plus'

import { importMembers } from '@/api/members'

const props = defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; success: [] }>()

const loading = ref(false)
const file = ref<File | null>(null)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

function onFileChange(uploadFile: UploadFile) {
  file.value = uploadFile.raw || null
}

function onFileRemove() {
  file.value = null
}

async function onImport() {
  if (!file.value) return
  loading.value = true
  try {
    const result = await importMembers(file.value)
    ElMessage.success(result.message)
    if (result.errors.length > 0) {
      ElMessage.warning(`导入完成，${result.errors.length} 条数据有问题：${result.errors.join('；')}`)
    }
    visible.value = false
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.tip {
  margin-bottom: 16px;
}

.uploader {
  width: 100%;
}
</style>

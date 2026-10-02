<template>
  <el-dialog v-model="visible" title="添加补人" width="420px" destroy-on-close append-to-body>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="70px">
      <el-form-item label="ID" prop="name">
        <el-input v-model="form.name" maxlength="32" placeholder="请输入补人名称" />
      </el-form-item>
      <el-form-item label="职业" prop="profession">
        <el-select v-model="form.profession" placeholder="请选择职业" style="width: 100%">
          <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSubmit">添加</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { addFiller } from '@/api/attendance'
import { PROFESSIONS } from '@/utils/constants'

const props = defineProps<{ modelValue: boolean; scheduleId: number }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; success: [] }>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const form = reactive({ name: '', profession: '' })

const rules: FormRules = {
  name: [{ required: true, message: '请输入补人名称', trigger: 'blur' }],
  profession: [{ required: true, message: '请选择职业', trigger: 'change' }],
}

async function onSubmit() {
  if (!formRef.value) return
  form.name = form.name.trim()
  await formRef.value.validate()
  loading.value = true
  try {
    await addFiller(props.scheduleId, { ...form })
    ElMessage.success('添加成功')
    visible.value = false
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>

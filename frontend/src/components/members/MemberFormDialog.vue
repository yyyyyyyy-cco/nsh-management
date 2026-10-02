<template>
  <el-dialog v-model="visible" :title="isEdit ? '编辑成员' : '添加成员'" width="480px" destroy-on-close append-to-body>
    <el-form ref="formRef" :model="form" :rules="rules" label-width="80px">
      <el-form-item label="ID" prop="name">
        <el-input v-model="form.name" maxlength="32" placeholder="请输入ID" />
      </el-form-item>
      <el-form-item label="主职业" prop="main_profession">
        <el-select v-model="form.main_profession" placeholder="请选择主职业" style="width: 100%">
          <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p">
            <span class="opt"><i class="opt-dot" :style="{ background: profColor(p) }" />{{ p }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="副职业" prop="sub_profession">
        <el-select v-model="form.sub_profession" placeholder="可选" clearable style="width: 100%">
          <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p">
            <span class="opt"><i class="opt-dot" :style="{ background: profColor(p) }" />{{ p }}</span>
          </el-option>
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-radio-group v-model="form.status">
          <el-radio v-for="s in MEMBER_STATUSES" :key="s.value" :value="s.value">{{ s.label }}</el-radio>
        </el-radio-group>
      </el-form-item>
      <el-form-item label="备注" prop="remark">
        <el-input v-model="form.remark" type="textarea" :rows="2" maxlength="255" placeholder="可选" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="onSubmit">保存</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { createMember, updateMember } from '@/api/members'
import { MEMBER_STATUSES, PROFESSIONS } from '@/utils/constants'
import { profColor } from '@/utils/profession'

const props = defineProps<{ modelValue: boolean; member: unknown }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean]; success: [] }>()

const formRef = ref<FormInstance>()
const loading = ref(false)
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value),
})

const isEdit = computed(() => Boolean(props.member))

const form = reactive({
  name: '',
  main_profession: '',
  sub_profession: undefined as string | undefined,
  status: 'formal',
  remark: '',
})

const rules: FormRules = {
  name: [{ required: true, message: '请输入ID', trigger: 'blur' }],
  main_profession: [{ required: true, message: '请选择主职业', trigger: 'change' }],
}

watch(
  () => props.modelValue,
  (value) => {
    if (!value) return
    const member = props.member as {
      name?: string
      main_profession?: string
      sub_profession?: string
      status?: string
      remark?: string
    } | null
    form.name = member?.name || ''
    form.main_profession = member?.main_profession || ''
    form.sub_profession = member?.sub_profession || undefined
    form.status = (member?.status as 'formal' | 'substitute') || 'formal'
    form.remark = member?.remark || ''
  },
)

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  loading.value = true
  try {
    if (isEdit.value) {
      await updateMember((props.member as { id: number }).id, { ...form })
    } else {
      await createMember({ ...form })
    }
    ElMessage.success('保存成功')
    visible.value = false
    emit('success')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.opt {
  display: flex;
  align-items: center;
  gap: 8px;
}

.opt-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

/* ===== 移动端：表单排版美化（标签左对齐加粗、间距收紧） ===== */
@media (max-width: 768px) {
  :deep(.el-form-item) {
    margin-bottom: 14px;
  }

  :deep(.el-form-item:last-child) {
    margin-bottom: 0;
  }

  :deep(.el-form-item__label) {
    font-size: 13px;
    font-weight: 600;
    color: var(--ink-700);
    margin-bottom: 6px;
  }
}
</style>

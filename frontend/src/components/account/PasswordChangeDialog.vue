<!-- 自助修改口令对话框（对应后端 `POST /api/v1/auth/password`）。
     默认由头部用户菜单打开；修改成功后**所有旧令牌立即失效**（后端 `token_version + 1`），
     故由父组件负责清除本地凭证并回到登录页。 -->
<template>
  <el-dialog
    :model-value="modelValue"
    title="修改密码"
    width="420px"
    :close-on-click-modal="false"
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
    @closed="resetForm"
  >
    <el-form ref="formRef" :model="form" :rules="rules" label-width="90px" @submit.prevent>
      <el-form-item label="当前密码" prop="currentPassword">
        <el-input v-model="form.currentPassword" type="password" show-password autocomplete="current-password" />
      </el-form-item>
      <el-form-item label="新密码" prop="newPassword">
        <el-input v-model="form.newPassword" type="password" show-password autocomplete="new-password" />
      </el-form-item>
      <el-form-item label="确认新密码" prop="confirmPassword">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          show-password
          autocomplete="new-password"
          @keyup.enter="submit"
        />
      </el-form-item>
      <p class="hint">8–128 位；不得为常见弱口令、不得包含登录名。修改后其他设备上的登录会立即失效。</p>
    </el-form>
    <template #footer>
      <el-button @click="emit('update:modelValue', false)">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="submit">确定修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'

import { changePassword } from '@/api/auth'
import { buildPasswordRules, validatePasswordForm } from '@/utils/passwordForm'

defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [boolean]; changed: [] }>()

const formRef = ref<FormInstance>()
const submitting = ref(false)
const errors = ref('')
const form = reactive({ currentPassword: '', newPassword: '', confirmPassword: '' })

// 展示用规则与服务端无关：只做即时提示；提交闸门是 validatePasswordForm（纯函数）
const rules = computed<FormRules>(() => buildPasswordRules(() => form))

function resetForm() {
  formRef.value?.resetFields()
  errors.value = ''
  form.currentPassword = ''
  form.newPassword = ''
  form.confirmPassword = ''
}

/**
 * 提交；成功后清空表单并通知父组件（父组件负责登出跳转）。错误提示由 http 拦截器统一给出。
 *
 * **闸门是纯函数** `validatePasswordForm`（确定、可脱离 DOM 测试）：el-form 的 `validate()`
 * 在实测中校验失败仍会放行到提交，故不把它当作提交条件；`rules` 只负责界面提示。
 */
async function submit() {
  const error = validatePasswordForm(form)
  if (error) {
    // 同步给界面提示（rules 的触发时机依赖 blur/change，点击提交时可能尚未显示）
    errors.value = error
    ElMessage.warning(error)
    return
  }
  errors.value = ''
  submitting.value = true
  try {
    await changePassword({ current_password: form.currentPassword, new_password: form.newPassword })
    emit('update:modelValue', false)
    emit('changed')
  } catch {
    // 错误提示由 http 拦截器统一给出（含「当前密码不正确」的 401）。
    // 这里必须吞掉拒绝：否则会从点击处理器逃逸成「未处理的 Promise 拒绝」，
    // 组件测试会以 unhandled error 形式报出（lint / build 都发现不了）。
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.hint {
  margin: 0 0 0 90px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--el-text-color-secondary);
}
</style>

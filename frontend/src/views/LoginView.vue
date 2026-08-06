<template>
  <div class="login-page">
    <el-card class="login-card" shadow="always">
      <h1 class="title">帮会联赛管理系统</h1>
      <p class="subtitle">逆水寒帮会联赛管理</p>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="loading" @click="onSubmit">登 录</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Lock, User } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function onSubmit() {
  if (!formRef.value) return
  await formRef.value.validate()
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string | undefined
    router.push(redirect || { name: 'home' })
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, #fff8e7 0%, #f5f0e8 100%);
}

.login-card {
  width: 400px;
  border-radius: 12px;
  padding: 24px 16px 8px;
}

.title {
  text-align: center;
  font-size: 24px;
  color: #b8960e;
  margin-bottom: 4px;
}

.subtitle {
  text-align: center;
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 24px;
}

.submit {
  width: 100%;
  margin-top: 8px;
}
</style>

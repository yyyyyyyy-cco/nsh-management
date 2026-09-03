<template>
  <div class="login-page">
    <!-- 水墨装饰 -->
    <div class="ink ink--1" />
    <div class="ink ink--2" />
    <div class="ink ink--3" />

    <div class="login-card">
      <div class="card-topline" />
      <div class="brand">
        <h1 class="brand-title">轻衫都会用的<br>帮会联赛管理系统</h1>
        <div class="brand-line" />
      </div>
      <el-form ref="formRef" :model="form" :rules="rules" size="large" @keyup.enter="onSubmit">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" :disabled="locked" @input="errorMsg = ''" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" show-password :prefix-icon="Lock" :disabled="locked" @input="errorMsg = ''" />
        </el-form-item>
        <el-alert
          v-if="errorMsg"
          :title="locked ? `账号已锁定，请 ${formatLockTime(lockSeconds)} 后重试` : errorMsg"
          type="error"
          show-icon
          :closable="false"
          class="login-error"
        />
        <el-button type="primary" class="submit" :loading="loading" :disabled="locked" @click="onSubmit">登 录</el-button>
      </el-form>
    </div>

    <!-- 底部备案信息 -->
    <footer class="beian">
      <a href="https://beian.miit.gov.cn/" target="_blank" rel="noreferrer">浙ICP备2026068650号-1</a>
      <a
        href="https://beian.mps.gov.cn/#/query/webSearch?code=33019202003234"
        target="_blank"
        rel="noreferrer"
        class="beian-ga"
      >
        <img :src="beianIcon" alt="公安备案图标" class="beian-icon" />
        浙公网安备33019202003234号
      </a>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { computed, onUnmounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { Lock, User } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'

import { useAuthStore } from '@/stores/auth'
import beianIcon from '@/assets/beian.png'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const formRef = ref<FormInstance>()
const loading = ref(false)
const errorMsg = ref('')
const form = reactive({ username: '', password: '' })

// 账号锁定倒计时（秒）：>0 时禁用表单输入与登录按钮
const lockSeconds = ref(0)
let lockTimer: ReturnType<typeof setInterval> | null = null
const locked = computed(() => lockSeconds.value > 0)

function formatLockTime(total: number): string {
  const m = Math.floor(total / 60)
  const s = total % 60
  return m > 0 ? `${m} 分 ${s} 秒` : `${s} 秒`
}

function startLockCountdown(seconds: number) {
  lockSeconds.value = seconds
  if (lockTimer) clearInterval(lockTimer)
  lockTimer = setInterval(() => {
    lockSeconds.value -= 1
    if (lockSeconds.value <= 0) {
      if (lockTimer) clearInterval(lockTimer)
      lockTimer = null
      errorMsg.value = '' // 解锁后清除锁定提示，恢复表单
    }
  }, 1000)
}

onUnmounted(() => {
  if (lockTimer) clearInterval(lockTimer)
})

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

/** 从登录接口错误中提取后端返回的具体提示，并识别锁定状态启动倒计时。 */
function getErrorMessage(err: unknown): string {
  if (axios.isAxiosError<{ message?: string; detail?: string; data?: { remaining_seconds?: number } | null }>(err)) {
    const body = err.response?.data
    const secs = body?.data?.remaining_seconds
    if (secs && secs > 0) {
      startLockCountdown(secs)
    }
    return body?.message || body?.detail || '网络错误，请稍后重试'
  }
  return '登录失败，请稍后重试'
}

async function onSubmit() {
  if (!formRef.value || locked.value) return // 锁定期间不允许提交
  try {
    await formRef.value.validate()
  } catch {
    return // 表单校验未通过
  }
  errorMsg.value = ''
  loading.value = true
  try {
    await auth.login(form.username, form.password)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string | undefined
    if (redirect) {
      router.push(redirect)
    } else if (auth.isDeveloper) {
      router.push({ name: 'config' })
    } else if (auth.user?.role === 'member') {
      router.push({ name: 'league-overview' })
    } else {
      router.push({ name: 'home' })
    }
  } catch (err) {
    // 登录接口的 401 已由 http.ts 放行到此处，展示具体错误（凭证错误 / 账号锁定）
    errorMsg.value = getErrorMessage(err)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  position: relative;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background:
    radial-gradient(1000px 600px at 15% 20%, rgba(212, 175, 55, 0.1), transparent 60%),
    radial-gradient(900px 500px at 85% 85%, rgba(139, 115, 85, 0.12), transparent 55%),
    linear-gradient(165deg, #f7f3ea 0%, #f2ecdd 55%, #ece4d2 100%);
}

/* ===== 水墨晕染 ===== */
.ink {
  position: absolute;
  border-radius: 50%;
  filter: blur(2px);
  animation: ink-drift 14s ease-in-out infinite alternate;
}

.ink--1 {
  width: 460px;
  height: 460px;
  left: -120px;
  top: -160px;
  background: radial-gradient(circle at 35% 35%, rgba(107, 91, 69, 0.14), transparent 65%);
}

.ink--2 {
  width: 520px;
  height: 520px;
  right: -180px;
  bottom: -200px;
  background: radial-gradient(circle at 60% 40%, rgba(43, 38, 32, 0.12), transparent 62%);
  animation-delay: -7s;
}

.ink--3 {
  width: 260px;
  height: 260px;
  right: 16%;
  top: 12%;
  background: radial-gradient(circle, rgba(212, 175, 55, 0.12), transparent 65%);
  animation-delay: -3s;
}

@keyframes ink-drift {
  from {
    transform: translate(0, 0) scale(1);
  }
  to {
    transform: translate(24px, -18px) scale(1.06);
  }
}

/* ===== 登录卡片 ===== */
.login-card {
  position: relative;
  width: 420px;
  background: rgba(255, 253, 248, 0.94);
  backdrop-filter: blur(6px);
  border: 1px solid var(--edge-strong);
  border-radius: 16px;
  padding: 46px 44px 38px;
  box-shadow: var(--shadow-lg);
  animation: card-in 0.5s var(--ease-out) both;
}

@keyframes card-in {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.card-topline {
  position: absolute;
  top: 0;
  left: 40px;
  right: 40px;
  height: 3px;
  border-radius: 0 0 3px 3px;
  background: var(--gold-line);
}

.brand {
  text-align: center;
  margin-bottom: 32px;
}

.brand-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 4px;
  line-height: 1.6;
  margin-bottom: 16px;
}

.brand-line {
  width: 52px;
  height: 2px;
  margin: 0 auto;
  border-radius: 2px;
  background: var(--gold-line);
}

.login-card :deep(.el-form-item) {
  margin-bottom: 26px;
}

.login-card :deep(.el-input__wrapper) {
  padding: 6px 14px;
}

.login-error {
  margin-bottom: 18px;
}

.submit {
  width: 100%;
  margin-top: 8px;
  height: 42px;
  font-size: 14px;
  letter-spacing: 8px;
  font-weight: 600;
}

/* ===== 底部备案信息 ===== */
.beian {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 12px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  font-size: 12px;
}

.beian a {
  color: var(--ink-400);
  text-decoration: none;
  transition: color 0.2s ease;
}

.beian a:hover {
  color: var(--gold-600);
}

.beian-ga {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.beian-icon {
  width: 14px;
  height: 14px;
  display: block;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .login-card {
    width: calc(100vw - 32px);
    max-width: 420px;
    padding: 36px 24px 30px;
  }

  .brand-title {
    font-size: 21px;
    letter-spacing: 2px;
  }
}

@media (max-width: 480px) {
  /* 隐藏超大水墨装饰，避免遮挡卡片 */
  .ink--1,
  .ink--2 {
    display: none;
  }

  .login-card {
    padding: 28px 18px 24px;
  }

  .brand {
    margin-bottom: 24px;
  }

  .brand-title {
    font-size: 19px;
    line-height: 1.5;
  }

  .login-card :deep(.el-form-item) {
    margin-bottom: 18px;
  }

  .submit {
    height: 46px; /* 增大触控点击区 */
    letter-spacing: 6px;
  }
}
</style>

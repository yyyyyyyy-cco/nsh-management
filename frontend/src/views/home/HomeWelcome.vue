<template>
  <div class="welcome-section">
    <div class="welcome-left">
      <h2 class="welcome-title">{{ greetingText }}，{{ auth.user?.username }}</h2>
      <p class="welcome-date">{{ dateText }}</p>
    </div>
    <el-tag v-if="auth.user?.role" :type="roleTagType" size="large" effect="plain" round>
      {{ roleLabel }}
    </el-tag>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import dayjs from 'dayjs'

import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const dateText = dayjs().format('YYYY年M月D日 dddd')

const greetingText = computed(() => {
  const h = dayjs().hour()
  if (h < 6) return '深夜了'
  if (h < 12) return '早上好'
  if (h < 14) return '中午好'
  if (h < 18) return '下午好'
  return '晚上好'
})

const roleTagType = computed(() => {
  const r = auth.user?.role
  return r === 'developer' ? 'info' : r === 'admin' ? 'danger' : ''
})

const roleLabel = computed(() => {
  const r = auth.user?.role
  return r === 'developer' ? '开发者' : r === 'admin' ? '管理员' : '帮众'
})
</script>

<style scoped>
.welcome-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.welcome-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: 1px;
  margin: 0 0 4px 0;
  overflow-wrap: anywhere;
}

.welcome-date {
  font-size: 13px;
  color: var(--ink-400);
  margin: 0;
}

@media (max-width: 480px) {
  .welcome-title {
    font-size: 18px;
  }

  /* 欢迎区：角色标签换行，避免溢出 */
  .welcome-section {
    flex-wrap: wrap;
    gap: 8px;
  }

  .welcome-date {
    font-size: 12px;
  }
}
</style>

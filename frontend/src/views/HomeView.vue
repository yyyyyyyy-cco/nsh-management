<template>
  <div class="home">
    <el-card shadow="never">
      <h2 class="welcome">欢迎回来，{{ auth.user?.username }}</h2>
      <p class="tip">系统功能模块开发中，请稍候。</p>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<style scoped>
.welcome {
  color: #1f2937;
  margin-bottom: 8px;
}

.tip {
  color: #6b7280;
}
</style>

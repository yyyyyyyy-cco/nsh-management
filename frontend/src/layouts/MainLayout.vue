<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">帮会联赛</div>
      <el-menu :default-active="activeMenu" router class="menu">
        <el-menu-item index="/">首页</el-menu-item>
      </el-menu>
    </aside>
    <div class="main">
      <header class="header">
        <div class="page-title">{{ pageTitle }}</div>
        <el-dropdown @command="onCommand">
          <span class="user-info">
            {{ auth.user?.username }}（{{ roleText }}）
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </header>
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  auth.fetchMe()
})

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => String(route.meta.title || ''))
const roleText = computed(() => (auth.isAdmin ? '管理员' : '帮众'))

async function onCommand(command: string | number | object) {
  if (command === 'logout') {
    await ElMessageBox.confirm('确定退出登录吗？', '提示', { type: 'warning' })
    auth.clear()
    router.push({ name: 'login' })
  }
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100%;
}

.sidebar {
  width: 200px;
  flex-shrink: 0;
  background: #fff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  font-size: 18px;
  font-weight: 700;
  color: #b8960e;
  border-bottom: 1px solid #e5e7eb;
}

.menu {
  border-right: none;
  padding: 8px;
  flex: 1;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header {
  height: 64px;
  flex-shrink: 0;
  background: #fff;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.user-info {
  cursor: pointer;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 4px;
}

.content {
  flex: 1;
  padding: 24px;
  overflow: auto;
  max-width: 1400px;
  width: 100%;
}
</style>

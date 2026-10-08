<template>
  <div class="layout">
    <!-- 移动端抽屉遮罩 -->
    <transition name="mask-fade">
      <div v-if="isMobile && drawerOpen" class="sidebar-mask" @click="drawerOpen = false" />
    </transition>
    <AppSidebar :collapsed="collapsed" :is-mobile="isMobile" :drawer-open="drawerOpen" @select-menu="onMenuSelect" />
    <div class="main">
      <AppHeader
        :route-loading="routeLoading"
        :collapsed="collapsed"
        :is-mobile="isMobile"
        @toggle-sidebar="onToggleSidebar"
      />
      <main class="content">
        <router-view v-slot="{ Component, route }">
          <transition name="page-switch" mode="out-in">
            <component :is="Component" :key="route.path" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { useAuthStore } from '@/stores/auth'
import { useRouteProgress } from '@/composables/useRouteProgress'
import AppHeader from './AppHeader.vue'
import AppSidebar from './AppSidebar.vue'

const auth = useAuthStore()

// 侧边栏折叠状态，localStorage 持久化，刷新后保持（仅 PC 端生效）
const collapsed = ref(localStorage.getItem('sidebar-collapsed') === '1')
watch(collapsed, (v) => localStorage.setItem('sidebar-collapsed', v ? '1' : '0'))

// 移动端（≤768px）抽屉式侧边栏
const isMobile = ref(false)
const drawerOpen = ref(false)
let mq: MediaQueryList | null = null

// 路由懒加载分包：鎏金进度线（见 composables/useRouteProgress）
const { routeLoading } = useRouteProgress()

function onMqChange(e: MediaQueryListEvent) {
  isMobile.value = e.matches
  if (!e.matches) drawerOpen.value = false // 回到 PC 宽度时关闭抽屉
}

onMounted(() => {
  auth.fetchMe()
  mq = window.matchMedia('(max-width: 768px)')
  isMobile.value = mq.matches
  mq.addEventListener('change', onMqChange)
})

onBeforeUnmount(() => {
  mq?.removeEventListener('change', onMqChange)
})

/** 移动端点按钮打开抽屉，PC 端切换折叠。 */
function onToggleSidebar() {
  if (isMobile.value) {
    drawerOpen.value = !drawerOpen.value
  } else {
    collapsed.value = !collapsed.value
  }
}

/** 移动端选中菜单后自动收起抽屉。 */
function onMenuSelect() {
  if (isMobile.value) drawerOpen.value = false
}
</script>

<style scoped>
.layout {
  display: flex;
  height: 100%;
}

/* ===== 移动端抽屉遮罩 ===== */
.sidebar-mask {
  position: fixed;
  inset: 0;
  z-index: 1000;
  background: var(--el-mask-color);
}

.mask-fade-enter-active,
.mask-fade-leave-active {
  transition: opacity var(--dur-normal) var(--ease-out);
}

.mask-fade-enter-from,
.mask-fade-leave-to {
  opacity: 0;
}

/* ===== 主区域 ===== */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
  position: relative;
}

.content {
  flex: 1;
  padding: 24px 26px;
  overflow: auto;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
}

/* ===== 移动端（≤768px） ===== */
@media (max-width: 768px) {
  .content {
    padding: 14px 12px;
  }
}
</style>

<template>
  <div class="layout">
    <!-- 移动端抽屉遮罩 -->
    <transition name="mask-fade">
      <div v-if="isMobile && drawerOpen" class="sidebar-mask" @click="drawerOpen = false" />
    </transition>
    <aside class="sidebar" :class="{ collapsed, 'mobile-open': isMobile && drawerOpen }">
      <div class="logo">
        <span class="logo-text">{{ collapsed ? (auth.user?.guild_name || '轻衫都会').charAt(0) : auth.user?.guild_name || '轻衫都会' }}</span>
      </div>
      <div class="logo-sub" v-show="!collapsed">逆水寒 · 帮会联赛管理</div>
      <el-menu :default-active="activeMenu" router class="menu" :collapse="collapsed" :collapse-transition="false" @select="onMenuSelect">
        <el-menu-item v-if="auth.user?.role === 'admin'" index="/" :title="collapsed ? '首页' : undefined">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'member'" index="/league-overview" :title="collapsed ? '录屏上传' : undefined">
          <el-icon><VideoCamera /></el-icon>
          <span>录屏上传</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'member'" index="/my-stats" :title="collapsed ? '个人战绩' : undefined">
          <el-icon><TrendCharts /></el-icon>
          <span>个人战绩</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'member'" index="/schedules" :title="collapsed ? '联赛日程' : undefined">
          <el-icon><Calendar /></el-icon>
          <span>联赛日程</span>
        </el-menu-item>
        <el-menu-item v-if="auth.isAdmin && !auth.isDeveloper" index="/members" :title="collapsed ? '常驻库' : undefined">
          <el-icon><UserFilled /></el-icon>
          <span>常驻库</span>
        </el-menu-item>
        <el-menu-item v-if="auth.user?.role === 'admin'" index="/schedules" :title="collapsed ? '联赛日程' : undefined">
          <el-icon><Calendar /></el-icon>
          <span>联赛日程</span>
        </el-menu-item>
        <el-menu-item v-if="auth.isAdmin" index="/config" :title="collapsed ? '系统配置' : undefined">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </el-menu-item>
      </el-menu>
      <div class="sidebar-footer" v-show="!collapsed">NSH League System</div>
    </aside>
    <div class="main">
      <header class="header">
        <div class="header-left">
          <button type="button" class="collapse-btn" :title="isMobile ? '打开导航菜单' : collapsed ? '展开侧边栏' : '收起侧边栏'" @click="onToggleSidebar">
            <span v-if="guildIconChar" class="collapse-btn__char">{{ guildIconChar }}</span>
            <el-icon v-else :size="15"><component :is="isMobile ? Menu : collapsed ? Expand : Fold" /></el-icon>
          </button>
          <div class="page-title">
            <span class="page-title__bar" />
            {{ pageTitle }}
          </div>
        </div>
        <el-dropdown @command="onCommand">
          <span class="user-info">
            <span class="user-name">{{ auth.user?.username }}</span>
            <span class="user-role">{{ roleText }}</span>
            <el-icon class="user-arrow"><ArrowDown /></el-icon>
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
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Calendar, Expand, Fold, HomeFilled, Menu, Setting, TrendCharts, UserFilled, VideoCamera } from '@element-plus/icons-vue'
import { ElMessageBox } from 'element-plus'

import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

// 侧边栏折叠状态，localStorage 持久化，刷新后保持（仅 PC 端生效）
const collapsed = ref(localStorage.getItem('sidebar-collapsed') === '1')
watch(collapsed, (v) => localStorage.setItem('sidebar-collapsed', v ? '1' : '0'))

// 移动端（≤768px）抽屉式侧边栏
const isMobile = ref(false)
const drawerOpen = ref(false)
let mq: MediaQueryList | null = null

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

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => String(route.meta.title || ''))
/** 帮会图标首字（管理员在系统配置设置，PC 与窄屏一致显示）。 */
const guildIconChar = computed(() => (auth.user?.guild_icon || '').charAt(0))
const roleText = computed(() => {
  const role = auth.user?.role
  return role === 'developer' ? '开发者' : role === 'admin' ? '管理员' : '帮众'
})

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

/* ===== 侧边栏：宣纸米白 ===== */
.sidebar {
  width: 208px;
  flex-shrink: 0;
  transition: width var(--dur-normal) var(--ease-out);
  background:
    radial-gradient(320px 240px at 50% 0%, rgba(217, 182, 74, 0.12), transparent 70%),
    linear-gradient(180deg, #fdfaf3 0%, #f8f2e6 100%);
  display: flex;
  flex-direction: column;
  position: relative;
}

/* 侧边栏右侧鎏金细线 */
.sidebar::after {
  content: '';
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 1px;
  background: linear-gradient(180deg, transparent, rgba(201, 161, 59, 0.45) 30%, rgba(201, 161, 59, 0.45) 70%, transparent);
}

/* ===== 折叠态：64px 仅图标 ===== */
.sidebar.collapsed { width: 64px; }
.sidebar.collapsed .logo { padding: 22px 0 18px; margin: 0 12px 10px; border-bottom: 1px solid var(--edge-soft); }
.sidebar.collapsed .logo-text { letter-spacing: 0; font-size: 20px; }
.sidebar.collapsed .menu { padding: 6px; }
/* 折叠时强制隐藏菜单文字、图标居中，避免 Element Plus 默认样式失效导致的内部偏移 */
.sidebar.collapsed .menu :deep(.el-menu-item) { justify-content: center; padding: 0; }
.sidebar.collapsed .menu :deep(.el-menu-item span) { display: none; }

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 22px 16px 6px;
}

.logo-text {
  font-family: var(--font-serif);
  font-size: 19px;
  font-weight: 700;
  letter-spacing: 3px;
  background: linear-gradient(135deg, #d9b64a 0%, #b18c2c 60%, #9c7a20 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.logo-sub {
  text-align: center;
  font-size: 10px;
  letter-spacing: 4px;
  color: var(--ink-300);
  padding-bottom: 18px;
  border-bottom: 1px solid var(--edge-soft);
  margin: 0 18px 10px;
}

.menu {
  --el-menu-bg-color: transparent;
  --el-menu-text-color: var(--ink-500);
  --el-menu-hover-bg-color: var(--gold-50);
  --el-menu-hover-text-color: var(--gold-700);
  --el-menu-active-color: var(--gold-700);
  --el-menu-item-height: 44px;
  border-right: none;
  padding: 6px 10px;
  flex: 1;
}

.menu :deep(.el-menu-item) {
  border-radius: var(--radius-md);
  margin-bottom: 4px;
  font-size: 13.5px;
  letter-spacing: 1px;
  position: relative;
  transition: background var(--dur-fast) var(--ease-out), color var(--dur-fast), box-shadow var(--dur-fast);
}

.menu :deep(.el-menu-item .el-icon) {
  font-size: 16px;
}

.menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(135deg, var(--gold-100) 0%, var(--gold-50) 100%);
  color: var(--gold-700);
  font-weight: 600;
  box-shadow: inset 0 0 0 1px var(--gold-200);
}

/* 激活项左侧金条 */
.menu :deep(.el-menu-item.is-active::before) {
  content: '';
  position: absolute;
  left: 0;
  top: 20%;
  bottom: 20%;
  width: 3px;
  border-radius: 2px;
  background: var(--gold-gradient);
}

.menu :deep(.el-menu-item.is-active .el-icon) {
  color: var(--gold-600);
}

.sidebar-footer {
  text-align: center;
  font-size: 9px;
  letter-spacing: 2px;
  color: var(--ink-300);
  padding: 14px 0;
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

/* ===== 移动端（≤768px）：抽屉式侧边栏 ===== */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1001;
    transform: translateX(-100%);
    transition: transform var(--dur-normal) var(--ease-out);
    box-shadow: none;
  }

  .sidebar.mobile-open {
    transform: translateX(0);
    box-shadow: var(--shadow-lg);
  }

  .sidebar.collapsed {
    width: 208px; /* 移动端忽略折叠态，抽屉始终全宽展示 */
  }

  .sidebar.collapsed .logo {
    padding: 22px 16px 6px;
    margin: 0;
    border-bottom: none;
  }

  .sidebar.collapsed .logo-text {
    letter-spacing: 3px;
    font-size: 19px;
  }

  .sidebar .logo-sub {
    display: block; /* 移动端抽屉忽略折叠态，副标题始终显示 */
  }

  .sidebar.collapsed .menu {
    padding: 6px 10px;
  }

  .sidebar.collapsed .menu :deep(.el-menu-item) {
    justify-content: flex-start;
    padding: 0 20px;
  }

  .sidebar.collapsed .menu :deep(.el-menu-item span) {
    display: inline;
  }

  .header {
    height: 56px;
    padding: 0 12px;
  }

  .header-left {
    gap: 10px;
  }

  .page-title {
    font-size: 15px;
  }

  .user-role,
  .user-arrow {
    display: none;
  }

  .user-name {
    font-size: 13px;
  }

  .content {
    padding: 14px 12px;
  }
}

/* ===== 主区域 ===== */
.main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.header {
  height: 62px;
  flex-shrink: 0;
  background: rgba(253, 250, 244, 0.9);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--edge-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 26px;
}

.header-left { display: flex; align-items: center; gap: 14px; }

.collapse-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: var(--radius-md);
  border: 1px solid var(--gold-200); background: var(--ink-bg-paper);
  color: var(--gold-700); cursor: pointer;
  transition: all var(--dur-fast);
}

.collapse-btn:hover { background: var(--gold-100); border-color: var(--gold-400); }

.collapse-btn__char {
  font-family: var(--font-serif);
  font-size: 16px;
  font-weight: 700;
  line-height: 1;
}

.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-serif);
  font-size: 17px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 1px;
}

.page-title__bar {
  width: 4px;
  height: 18px;
  border-radius: 2px;
  background: var(--gold-gradient);
}

.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 5px 10px;
  border-radius: var(--radius-xl);
  transition: background var(--dur-fast);
}

.user-info:hover {
  background: var(--gold-50);
}

.user-name {
  font-weight: 600;
  color: var(--ink-900);
  font-size: 13.5px;
}

.user-role {
  font-size: 11px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 1px 8px;
  font-weight: 500;
}

.user-arrow {
  color: var(--ink-400);
  font-size: 12px;
}

.content {
  flex: 1;
  padding: 24px 26px;
  overflow: auto;
  max-width: 1440px;
  width: 100%;
  margin: 0 auto;
}
</style>

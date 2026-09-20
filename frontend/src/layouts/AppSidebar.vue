<template>
  <aside class="sidebar" :class="{ collapsed, 'mobile-open': isMobile && drawerOpen }">
    <div class="logo">
      <span class="logo-text">{{ collapsed ? (auth.user?.guild_name || '轻衫都会').charAt(0) : auth.user?.guild_name || '轻衫都会' }}</span>
    </div>
    <div class="logo-sub" v-show="!collapsed">逆水寒 · 帮会联赛管理</div>
    <el-menu :default-active="activeMenu" router class="menu" :collapse="collapsed" :collapse-transition="false" @select="$emit('select-menu')">
      <el-menu-item v-if="auth.user?.role === 'admin'" index="/" :title="collapsed ? '首页' : undefined" @mouseenter="prefetchRoute('/')">
        <el-icon><HomeFilled /></el-icon>
        <span>首页</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'member'" index="/league-overview" :title="collapsed ? '录屏上传' : undefined" @mouseenter="prefetchRoute('/league-overview')">
        <el-icon><VideoCamera /></el-icon>
        <span>录屏上传</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'member'" index="/my-stats" :title="collapsed ? '个人战绩' : undefined" @mouseenter="prefetchRoute('/my-stats')">
        <el-icon><TrendCharts /></el-icon>
        <span>个人战绩</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'member'" index="/game-id-change" :title="collapsed ? '修改游戏 ID' : undefined" @mouseenter="prefetchRoute('/game-id-change')">
        <el-icon><EditPen /></el-icon>
        <span>修改游戏 ID</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'member'" index="/schedules" :title="collapsed ? '联赛日程' : undefined" @mouseenter="prefetchRoute('/schedules')">
        <el-icon><Calendar /></el-icon>
        <span>联赛日程</span>
      </el-menu-item>
      <el-menu-item v-if="auth.isAdmin && !auth.isDeveloper" index="/members" :title="collapsed ? '常驻库' : undefined" @mouseenter="prefetchRoute('/members')">
        <el-icon><UserFilled /></el-icon>
        <span>常驻库</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'admin'" index="/schedules" :title="collapsed ? '联赛日程' : undefined" @mouseenter="prefetchRoute('/schedules')">
        <el-icon><Calendar /></el-icon>
        <span>联赛日程</span>
      </el-menu-item>
      <!-- 管理员：个人战绩（与帮众同页，可自由按 ID 搜索任意成员） -->
      <el-menu-item v-if="auth.user?.role === 'admin'" index="/my-stats" :title="collapsed ? '个人战绩' : undefined" @mouseenter="prefetchRoute('/my-stats')">
        <el-icon><TrendCharts /></el-icon>
        <span>个人战绩</span>
      </el-menu-item>
      <el-menu-item v-if="auth.isAdmin" index="/config" :title="collapsed ? '系统配置' : undefined" @mouseenter="prefetchRoute('/config')">
        <el-icon><Setting /></el-icon>
        <span>系统配置</span>
      </el-menu-item>
      <el-menu-item v-if="auth.user?.role === 'developer'" index="/logs" :title="collapsed ? '系统日志' : undefined" @mouseenter="prefetchRoute('/logs')">
        <el-icon><Document /></el-icon>
        <span>系统日志</span>
      </el-menu-item>
    </el-menu>
    <div class="sidebar-footer" v-show="!collapsed">NSH League System</div>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { Calendar, Document, EditPen, HomeFilled, Setting, TrendCharts, UserFilled, VideoCamera } from '@element-plus/icons-vue'

import { useAuthStore } from '@/stores/auth'
import { prefetchRoute } from '@/router'

defineProps<{ collapsed: boolean; isMobile: boolean; drawerOpen: boolean }>()

defineEmits<{ 'select-menu': [] }>()

const route = useRoute()
const auth = useAuthStore()

const activeMenu = computed(() => route.path)
</script>

<style scoped>
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
}
</style>

<template>
  <!-- 路由懒加载分包期鎏金进度线（导航 >150ms 才出现） -->
  <transition name="progress-fade">
    <div v-if="routeLoading" class="route-progress"><span class="route-progress__bar" /></div>
  </transition>
  <header class="header">
    <div class="header-left">
      <button type="button" class="collapse-btn" :title="isMobile ? '打开导航菜单' : collapsed ? '展开侧边栏' : '收起侧边栏'" @click="$emit('toggle-sidebar')">
        <span v-if="guildIconChar" class="collapse-btn__char">{{ guildIconChar }}</span>
        <el-icon v-else :size="15"><component :is="isMobile ? Menu : collapsed ? Expand : Fold" /></el-icon>
      </button>
      <div class="page-title">
        <span class="page-title__bar" />
        {{ pageTitle }}
      </div>
    </div>
    <div class="header-right">
      <!-- 表格密度切换：紧凑 / 标准（全局生效，localStorage 持久化） -->
      <button
        type="button"
        class="density-btn"
        :class="{ 'density-btn--compact': density === 'compact' }"
        :title="density === 'compact' ? '切换为标准密度' : '切换为紧凑密度'"
        @click="toggleDensity"
      >
        <el-icon :size="15"><Rank /></el-icon>
      </button>
      <el-dropdown @command="onCommand">
        <span class="user-info">
          <span class="user-name">{{ auth.user?.username }}</span>
          <span class="user-role">{{ roleText }}</span>
          <el-icon class="user-arrow"><ArrowDown /></el-icon>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item v-if="auth.user?.role === 'member'" command="game-id-change">修改游戏 ID</el-dropdown-item>
            <!-- 修改密码：帮众按产品决策禁用自助改密（共享账号防失联），仅开发者/管理员可见；后端同步 403 拦截 -->
            <el-dropdown-item v-if="auth.user?.role !== 'member'" command="password">修改密码</el-dropdown-item>
            <el-dropdown-item command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 自助改密：成功后所有旧令牌失效，故关闭对话框后由父组件登出并回登录页 -->
    <PasswordChangeDialog v-model="showPasswordDialog" @changed="onPasswordChanged" />
  </header>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowDown, Expand, Fold, Menu, Rank } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useAuthStore } from '@/stores/auth'
import { useTableDensity } from '@/composables/useTableDensity'
import PasswordChangeDialog from '@/components/account/PasswordChangeDialog.vue'

defineProps<{ routeLoading: boolean; collapsed: boolean; isMobile: boolean }>()

defineEmits<{ 'toggle-sidebar': [] }>()

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const { density, toggle: toggleDensity } = useTableDensity()

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
    return
  }
  if (command === 'game-id-change') {
    router.push({ name: 'game-id-change' })
    return
  }
  if (command === 'password') {
    showPasswordDialog.value = true
  }
}

/** 弹层可见性（自助改密）。 */
const showPasswordDialog = ref(false)

/**
 * 改密成功后的收尾：后端已使**所有旧令牌失效**（含本机），因此主动清除本地凭证并回登录页，
 * 而不是等下一个请求 401 时被动登出。
 */
function onPasswordChanged() {
  auth.clear()
  ElMessage.success('密码已修改，请使用新密码重新登录')
  router.push({ name: 'login' })
}
</script>

<style scoped>
/* ===== 路由懒加载：鎏金进度线（>150ms 才出现，防闪烁） ===== */
.route-progress {
  position: absolute;
  top: 62px;
  left: 0;
  right: 0;
  height: 2px;
  overflow: hidden;
  z-index: 3000;
  pointer-events: none;
}

.route-progress__bar {
  display: block;
  width: 30%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(201, 161, 59, 0.4) 30%, var(--gold-500) 50%, rgba(201, 161, 59, 0.4) 70%, transparent);
  transform: translateX(-100%);
  animation: route-progress-sweep 1.1s ease-in-out infinite;
}

@keyframes route-progress-sweep {
  to {
    transform: translateX(433%);
  }
}

.progress-fade-enter-active {
  transition: opacity 150ms var(--ease-out);
}

.progress-fade-leave-active {
  transition: opacity 200ms var(--ease-out);
}

.progress-fade-enter-from,
.progress-fade-leave-to {
  opacity: 0;
}

.header {
  height: 62px;
  flex-shrink: 0;
  background: var(--ink-bg-cream);
  border-bottom: 1px solid var(--edge-soft);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 26px;
}

.header-left { display: flex; align-items: center; gap: 14px; }

.header-right { display: flex; align-items: center; gap: 10px; }

/* finesse · register=product · shell=global: 密度切换按钮（紧凑态金底高亮，移动端隐藏） */
.density-btn {
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: var(--radius-md);
  border: 1px solid var(--gold-200); background: var(--ink-bg-paper);
  color: var(--gold-700); cursor: pointer;
  transition: background var(--dur-fast), border-color var(--dur-fast);
}

.density-btn:hover { background: var(--gold-100); border-color: var(--gold-400); }

.density-btn--compact { background: var(--gold-100); border-color: var(--gold-400); }

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
  overflow-wrap: anywhere;
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

/* ===== 移动端（≤768px） ===== */
@media (max-width: 768px) {
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
  .user-arrow,
  .density-btn {
    display: none;
  }

  .user-name {
    font-size: 13px;
  }

  .route-progress {
    top: 56px;
  }
}
</style>

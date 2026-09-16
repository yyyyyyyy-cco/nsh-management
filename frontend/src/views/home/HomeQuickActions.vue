<template>
  <div class="card card--aux">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><Lightning /></el-icon>
        <span class="card__title">快捷操作</span>
      </div>
    </div>
    <div class="quick-actions">
      <div
        v-for="action in quickActions"
        :key="action.path"
        class="quick-action"
        :style="{ '--action-color': action.color }"
        @click="router.push(action.path)"
      >
        <el-icon class="quick-action__icon" :style="{ background: action.color }"><component :is="action.icon" /></el-icon>
        <span class="quick-action__label">{{ action.label }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Calendar, Lightning, Setting, UserFilled } from '@element-plus/icons-vue'

import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const quickActions = computed(() => {
  if (auth.isDeveloper) {
    return [
      { label: '系统配置', icon: Setting, path: '/config', color: '#D97706' },
    ]
  }
  return [
    { label: '常驻库', icon: UserFilled, path: '/members', color: '#2E8B57' },
    { label: '联赛日程', icon: Calendar, path: '/schedules', color: '#c9a13b' },
    { label: '系统配置', icon: Setting, path: '/config', color: '#D97706' },
  ]
})
</script>

<style scoped src="./home-shared.css"></style>

<style scoped>
/* ===== 快捷操作 ===== */
.quick-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  padding: 16px;
  align-content: center; /* 卡片拉高时图标组垂直居中 */
}

.quick-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  border-radius: var(--radius-md);
  border: 1px solid var(--edge-faint);
  cursor: pointer;
  transition: all var(--dur-normal) var(--ease-out);
}

.quick-action:hover {
  border-color: var(--gold-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-action__icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 19px;
  color: #fff !important;
  box-shadow: var(--shadow-sm);
}

.quick-action__label {
  font-size: 12px;
  font-weight: 600;
  color: var(--ink-600);
}

@media (max-width: 900px) {
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .quick-actions {
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    padding: 12px;
  }

  .quick-action {
    padding: 12px 4px;
  }

  .quick-action__icon {
    width: 36px;
    height: 36px;
    font-size: 17px;
  }
}
</style>

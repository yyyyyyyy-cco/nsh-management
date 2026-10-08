<!-- 帮众首页·快捷操作：整行四格（图标统一浅金底），≤768px 两列 -->
<template>
  <div class="card">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><Lightning /></el-icon>
        <span class="card__title">快捷操作</span>
      </div>
    </div>
    <div class="quick-grid">
      <button v-for="a in actions" :key="a.path" type="button" class="quick-item" @click="router.push(a.path)">
        <el-icon class="quick-item__icon"><component :is="a.icon" /></el-icon>
        <span class="quick-item__label">{{ a.label }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
import { Calendar, EditPen, Lightning, TrendCharts, VideoCamera } from '@element-plus/icons-vue'

const router = useRouter()

/** 帮众仅有的 4 个功能入口（与侧边栏菜单一致），录屏上传为赛后主任务放首位。 */
const actions = [
  { label: '录屏上传', icon: VideoCamera, path: '/league-overview' },
  { label: '个人战绩', icon: TrendCharts, path: '/my-stats' },
  { label: '修改游戏 ID', icon: EditPen, path: '/game-id-change' },
  { label: '联赛日程', icon: Calendar, path: '/schedules' },
]
</script>

<style scoped>
/* finesse · register=product · shell=member-home: 快捷操作整行四格（图标统一浅金，单色锁定）；≤768px 两列 */
.card {
  position: relative;
  background: var(--ink-bg-cream);
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--gold-line);
  opacity: 0.35;
}

.card__header {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  border-bottom: 1px solid var(--edge-faint);
}

.card__header-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card__header-icon {
  font-size: 15px;
}

.card__title {
  font-family: var(--font-serif);
  font-size: 15px;
  font-weight: 700;
  color: var(--ink-900);
  letter-spacing: 1px;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px;
}

.quick-item {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  min-height: 72px;
  padding: 10px 12px;
  border: 1px solid var(--edge-faint);
  border-radius: var(--radius-md);
  background: var(--ink-bg-paper);
  font-family: inherit;
  cursor: pointer;
  transition:
    border-color var(--dur-fast) var(--ease-out),
    box-shadow var(--dur-fast) var(--ease-out),
    transform var(--dur-fast) var(--ease-out);
}

.quick-item:hover {
  border-color: var(--gold-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.quick-item:hover .quick-item__icon {
  background: var(--gold-100);
}

.quick-item:active {
  transform: scale(0.98);
}

.quick-item:focus-visible {
  outline: 2px solid var(--gold-400);
  outline-offset: 2px;
}

.quick-item__icon {
  width: 38px;
  height: 38px;
  flex-shrink: 0;
  border-radius: 11px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  color: var(--gold-600);
  background: var(--gold-50);
  transition: background var(--dur-fast) var(--ease-out);
}

.quick-item__label {
  font-size: 13px;
  font-weight: 600;
  color: var(--ink-700);
  white-space: nowrap;
}

@media (max-width: 768px) {
  .quick-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    padding: 12px;
  }

  .quick-item {
    min-height: 64px;
    justify-content: flex-start;
  }

  .quick-item__label {
    white-space: normal;
  }
}
</style>

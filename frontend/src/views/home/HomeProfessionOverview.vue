<template>
  <div class="card card--aux">
    <div class="card__header">
      <div class="card__header-left">
        <el-icon class="card__header-icon"><PieChart /></el-icon>
        <span class="card__title">职业分布</span>
      </div>
    </div>
    <div class="card__body profession-grid">
      <template v-if="showSkeleton && professionStats.length === 0">
        <div v-for="i in 6" :key="i" class="profession-item">
          <span class="sk" style="width:10px;height:10px;border-radius:50%" />
          <span class="sk sk-line" style="width:52px" />
          <span class="sk sk-line sk-kpi-sm" />
        </div>
      </template>
      <template v-else>
        <div v-for="p in professionStats" :key="p.name" class="profession-item">
          <div class="profession-item__dot" :style="{ background: p.color }" />
          <span class="profession-item__name">{{ p.name }}</span>
          <span class="profession-item__count num">{{ p.count }}人</span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PieChart } from '@element-plus/icons-vue'

defineProps<{
  showSkeleton: boolean
  professionStats: { name: string; count: number; color: string }[]
}>()
</script>

<style scoped src="./home-shared.css"></style>

<style scoped>
/* ===== 职业分布 ===== */
.profession-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 16px !important;
}

.profession-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}

.profession-item__dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.profession-item__name {
  color: var(--ink-600);
  flex: 1;
}

.profession-item__count {
  color: var(--ink-400);
  font-size: 12px;
}

@media (max-width: 480px) {
  .profession-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

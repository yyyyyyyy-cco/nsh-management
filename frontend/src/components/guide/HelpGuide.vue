<template>
  <!-- 触发按钮：原生 button + aria-label，键盘可聚焦可触发（与顶栏 34px 图标按钮同款视觉） -->
  <button type="button" class="help-btn" aria-label="打开使用指南" title="使用指南" @click="guideRef?.open()">
    <el-icon :size="15" aria-hidden="true"><QuestionFilled /></el-icon>
  </button>
  <GuideDialog ref="guideRef" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'

import GuideDialog from './GuideDialog.vue'

const guideRef = ref<InstanceType<typeof GuideDialog>>()
</script>

<style scoped>
/* finesse · register=product：与 AppHeader 密度按钮同款令牌（金边纸底 34×34） */
.help-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border-radius: var(--radius-md);
  border: 1px solid var(--gold-200);
  background: var(--ink-bg-paper);
  color: var(--gold-700);
  cursor: pointer;
  transition:
    background var(--dur-fast),
    border-color var(--dur-fast);
}

.help-btn:hover {
  background: var(--gold-100);
  border-color: var(--gold-400);
}
</style>

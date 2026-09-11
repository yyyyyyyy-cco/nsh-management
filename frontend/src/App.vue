<template>
  <el-config-provider :locale="zhCn">
    <router-view v-slot="{ Component }">
      <Transition name="route-fade" mode="out-in">
        <component :is="Component" />
      </Transition>
    </router-view>
  </el-config-provider>
</template>

<script setup lang="ts">
// Element Plus 组件改为按需自动导入后，全局语言配置由 ElConfigProvider 提供
import zhCn from 'element-plus/es/locale/lang/zh-cn'
</script>

<style>
/* 路由切换淡入淡出过渡 */
.route-fade-enter-active,
.route-fade-leave-active {
  transition: opacity 0.2s ease;
}

.route-fade-enter-from,
.route-fade-leave-to {
  opacity: 0;
}

/* 减弱动态效果时禁用路由过渡 */
@media (prefers-reduced-motion: reduce) {
  .route-fade-enter-active,
  .route-fade-leave-active {
    transition: none !important;
  }
}
</style>

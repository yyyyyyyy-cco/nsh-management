<template>
  <router-view v-slot="{ Component }">
    <Transition name="route-fade" mode="out-in">
      <component :is="Component" />
    </Transition>
  </router-view>
</template>

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

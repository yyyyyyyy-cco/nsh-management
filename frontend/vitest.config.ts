import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

// ===== Vitest 配置（合规化计划 W2-2 前端部分；W4-11 补 Vue 插件） =====
// 设计与取舍：
//   · 与 vite.config.ts 分离：测试配置不混入生产构建配置，避免构建产物受影响；
//   · environment 用 jsdom：涉及 document / localStorage 的 composable 用例可直接运行；
//   · include 只匹配 src 下的 *.spec.ts，spec 与源码同目录（便于就近维护）。
//   · **plugins 必须包含 @vitejs/plugin-vue**：早期配置只服务纯逻辑用例，未加载 Vue 插件，
//     首个组件用例（W4-11 的 PasswordChangeDialog）会报
//     「Failed to parse source for import analysis … Install @vitejs/plugin-vue to handle .vue files」。
//   · 版本约束：vitest 5.x 要求 vite ^6.4/^7/^8，而本项目固定 vite 5.4，故安装 vitest 3.x
//     （2026-10-02 实测 npm ERESOLVE 冲突记录见 progress.md）。
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  test: {
    environment: 'jsdom',
    include: ['src/**/*.spec.ts'],
    reporters: ['default'],
  },
})
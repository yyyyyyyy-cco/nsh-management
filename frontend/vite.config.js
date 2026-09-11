import { fileURLToPath, URL } from 'node:url';
import vue from '@vitejs/plugin-vue';
import { defineConfig } from 'vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
export default defineConfig({
    plugins: [
        vue(),
        // Element Plus 组件按需自动导入（含 v-loading 等指令），减少 JS 体积；
        // 样式不随组件注入（importStyle: false）——main.ts 全量引入一次，
        // 保证项目深度主题覆盖（styles/element-plus.css）不被后注入的组件样式覆盖
        Components({
            resolvers: [ElementPlusResolver({ importStyle: false })],
            // 不生成 components.d.ts：模板中 el-* 组件保持项目原有的宽松类型行为
            dts: false,
        }),
    ],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
    server: {
        port: 5173,
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
            },
        },
    },
    build: {
        rollupOptions: {
            output: {
                // 仅把 echarts 拆为独立 chunk（体积大、多个分析页共享、可随路由延迟加载）；
                // 其余依赖交给 Rollup 按引用关系自动拆分：按需引入的 element-plus 组件随
                // 使用它们的路由 chunk 分发，避免全量合并后登录页被迫加载所有组件
                manualChunks: function (id) {
                    if (id.includes('echarts') || id.includes('zrender'))
                        return 'echarts';
                },
            },
        },
    },
});

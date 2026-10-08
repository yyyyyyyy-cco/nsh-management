import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { ElMessage } from 'element-plus'
// Element Plus 保留全量主题 CSS：组件 JS 由 unplugin-vue-components 按需引入（vite.config.ts），
// 而样式保留全量可确保项目深度主题覆盖（styles/element-plus.css）的加载顺序稳定、不随路由 chunk 后注入而失效
import 'element-plus/dist/index.css'

import App from './App.vue'
import router from './router'
import '@/styles/index.css'

/**
 * 部署后旧标签页动态加载新版本 chunk 失败（文件名已更新）时的降级处理：
 * 自动刷新一次恢复；仍失败则提示手动强刷（避免循环刷新）。
 * 页面正常挂载后清除标记，保证下一次部署仍可自动恢复。
 */
const CHUNK_RELOAD_FLAG = 'nsh-chunk-reloaded'
window.addEventListener('vite:preloadError', () => {
  if (sessionStorage.getItem(CHUNK_RELOAD_FLAG)) {
    ElMessage.error('系统已更新，请按 Ctrl+F5 强制刷新页面后继续使用')
    return
  }
  sessionStorage.setItem(CHUNK_RELOAD_FLAG, '1')
  window.location.reload()
})

// ===== 发版自动检测：让旧版本页面（含打开时命中旧缓存的页面）自动更新到新版本 =====
const UPDATE_RELOAD_FLAG = 'nsh-update-reloaded'
const UPDATE_NOTIFIED_FLAG = 'nsh-update-notified'
const UPDATE_CHECK_INTERVAL = 10 * 60 * 1000 // 兜底轮询间隔

/** 当前页面入口脚本文件名（形如 /assets/index-xxxx.js）；开发环境返回 null。 */
function currentEntryName(): string | null {
  const el = document.querySelector('script[type="module"][src*="/assets/"]')
  const src = el?.getAttribute('src') || ''
  return src.match(/\/assets\/index-[^"']+\.js/)?.[0] ?? null
}

/** 对比服务器最新构建与当前页面入口：不一致则自动更新（no-store 防缓存；异常静默）。 */
async function checkForUpdate(): Promise<void> {
  if (document.visibilityState !== 'visible') return
  try {
    const res = await fetch(`/?_=${Date.now()}`, { cache: 'no-store' })
    if (!res.ok) return
    const latest = (await res.text()).match(/\/assets\/index-[^"']+\.js/)?.[0]
    const current = currentEntryName()
    if (!latest || !current) return
    if (latest === current) {
      // 已是最新版本：清除标记，为下一次发版做准备
      sessionStorage.removeItem(UPDATE_RELOAD_FLAG)
      sessionStorage.removeItem(UPDATE_NOTIFIED_FLAG)
      return
    }
    // 正在输入（编辑表单/备注等）时不打断，等下次检查
    const active = document.activeElement
    const editing =
      !!active &&
      (active.tagName === 'INPUT' ||
        active.tagName === 'TEXTAREA' ||
        active.tagName === 'SELECT' ||
        (active as HTMLElement).isContentEditable)
    if (editing) return
    // 同一标签页已自动刷新过一次仍不一致：不再循环刷新，改为提示手动强刷
    if (sessionStorage.getItem(UPDATE_RELOAD_FLAG)) {
      if (!sessionStorage.getItem(UPDATE_NOTIFIED_FLAG)) {
        sessionStorage.setItem(UPDATE_NOTIFIED_FLAG, '1')
        ElMessage.warning('系统已更新，请按 Ctrl+F5 刷新页面以使用新版本')
      }
      return
    }
    sessionStorage.setItem(UPDATE_RELOAD_FLAG, '1')
    window.location.reload()
  } catch {
    // 网络异常等：静默忽略，等待下次检查
  }
}

// 打开后延迟检查（覆盖"打开时命中旧缓存"场景）+ 切回窗口时检查 + 定期兜底
window.setTimeout(checkForUpdate, 3000)
window.addEventListener('focus', checkForUpdate)
document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') void checkForUpdate()
})
window.setInterval(() => void checkForUpdate(), UPDATE_CHECK_INTERVAL)

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.mount('#app')

// 应用成功挂载说明当前页面资源完整：清除重试标记
sessionStorage.removeItem(CHUNK_RELOAD_FLAG)

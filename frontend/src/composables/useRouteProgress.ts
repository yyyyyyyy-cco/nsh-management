/** 路由懒加载分包：鎏金进度线状态（自 MainLayout.vue 拆出）。 */
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

export function useRouteProgress() {
  const router = useRouter()
  const routeLoading = ref(false)
  let progressTimer: number | undefined
  let removeBeforeEach: (() => void) | null = null
  let removeAfterEach: (() => void) | null = null
  let removeOnError: (() => void) | null = null

  onMounted(() => {
    // 路由进度：懒加载分包加载期 >150ms 显示鎏金线
    removeBeforeEach = router.beforeEach(() => {
      if (progressTimer !== undefined) window.clearTimeout(progressTimer)
      progressTimer = window.setTimeout(() => {
        routeLoading.value = true
      }, 150)
    })
    removeAfterEach = router.afterEach(() => {
      if (progressTimer !== undefined) {
        window.clearTimeout(progressTimer)
        progressTimer = undefined
      }
      routeLoading.value = false
    })
    removeOnError = router.onError(() => {
      if (progressTimer !== undefined) {
        window.clearTimeout(progressTimer)
        progressTimer = undefined
      }
      routeLoading.value = false
    })
  })

  onBeforeUnmount(() => {
    removeBeforeEach?.()
    removeAfterEach?.()
    removeOnError?.()
  })

  return { routeLoading }
}

/**
 * 骨架延迟显示：loading 持续超过 delay 毫秒才显示骨架，防止快请求闪烁
 * （数据 200ms 内返回时完全不出现骨架）；loading 结束立即隐藏。
 *
 * 用法：
 *   const showSkeleton = useSkeletonLoading(loading)
 *   模板：<SkeletonTable v-if="showSkeleton && !items.length" />
 */
import { onScopeDispose, ref, watch, type Ref } from 'vue'

export function useSkeletonLoading(loading: Ref<boolean>, delay = 200): Ref<boolean> {
  const show = ref(false)
  let timer: number | undefined

  function clear() {
    if (timer !== undefined) {
      window.clearTimeout(timer)
      timer = undefined
    }
  }

  watch(
    loading,
    (v) => {
      if (v) {
        clear()
        timer = window.setTimeout(() => {
          show.value = true
          timer = undefined
        }, delay)
      } else {
        clear()
        show.value = false
      }
    },
    { immediate: true },
  )

  onScopeDispose(clear)

  return show
}

/**
 * 数字滚动 composable — 数值从 0（或起始值）滚动到目标值。
 *
 * @param target  目标数值（ref 或 getter）
 * @param options duration 动画时长 ms（默认 800），decimals 小数位（默认 0）
 * @returns current 当前显示值（ref<number>）
 *
 * reduced-motion 检测：系统开启减弱动态效果时直接显示目标值，不执行动画。
 */
import { ref, watch, type Ref } from 'vue'

const prefersReduced = typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches

export function useCountUp(
  target: Ref<number | string | null | undefined>,
  options: { duration?: number; decimals?: number } = {},
) {
  const { duration = 800, decimals = 0 } = options
  const current = ref(0)

  let rafId = 0

  function animate(from: number, to: number) {
    cancelAnimationFrame(rafId)
    if (prefersReduced || duration <= 0) {
      current.value = to
      return
    }
    const start = performance.now()
    const diff = to - from
    function tick(now: number) {
      const elapsed = now - start
      const progress = Math.min(elapsed / duration, 1)
      // ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      current.value = Number((from + diff * eased).toFixed(decimals))
      if (progress < 1) {
        rafId = requestAnimationFrame(tick)
      } else {
        current.value = to
      }
    }
    rafId = requestAnimationFrame(tick)
  }

  watch(
    target,
    (val) => {
      const num = typeof val === 'string' ? parseFloat(val) : val
      if (num == null || isNaN(num)) {
        current.value = 0
        return
      }
      animate(current.value, num)
    },
    { immediate: true },
  )

  return current
}

<template>
  <div ref="el" class="echart" :style="elStyle" />
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
// ECharts 按需引入：仅注册项目用到的图表类型/组件/渲染器（全量引入约 1.1MB，按需约 1/3）
import * as echarts from 'echarts/core'
import { BarChart, HeatmapChart, LineChart, PieChart, RadarChart, ScatterChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  MarkLineComponent,
  RadarComponent,
  TooltipComponent,
  VisualMapComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import type { EChartsOption, EChartsType } from 'echarts'

echarts.use([
  LineChart,
  BarChart,
  PieChart,
  RadarChart,
  ScatterChart,
  HeatmapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  RadarComponent,
  VisualMapComponent,
  MarkLineComponent,
  CanvasRenderer,
])

const props = withDefaults(defineProps<{ option: Record<string, unknown>; height?: number | string }>(), {
  height: 300,
})

/** 高度支持数字（px）或字符串（如 "100%"），配合 flex 容器自适应。 */
const elStyle = computed(() => {
  const h = props.height
  return { height: typeof h === 'number' ? `${h}px` : h }
})

const el = ref<HTMLDivElement | null>(null)
let chart: EChartsType | null = null
let resizeObserver: ResizeObserver | null = null

onMounted(() => {
  if (!el.value) return
  const container = el.value
  /**
   * 弹窗等动态容器首次挂载瞬间可能无尺寸（echarts 会回退成 100×100），
   * 先等一帧；若仍无尺寸，交给 ResizeObserver 在容器有尺寸后兜底初始化。
   */
  const initChart = () => {
    if (!chart && container.clientWidth > 0 && container.clientHeight > 0) {
      chart = echarts.init(container)
      chart.setOption(props.option)
    }
  }
  requestAnimationFrame(initChart)
  resizeObserver = new ResizeObserver(() => {
    initChart()
    chart?.resize()
  })
  resizeObserver.observe(container)
})

watch(
  () => props.option,
  (opt) => {
    if (chart && opt) chart.setOption(opt as EChartsOption, { notMerge: true })
  },
  { deep: true },
)

onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.dispose()
  chart = null
})
</script>

<style scoped>
.echart {
  width: 100%;
}
</style>

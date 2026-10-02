<template>
  <!-- 空状态统一插画：手绘线条风 SVG（宣纸金线调），替代 el-empty 默认插画 -->
  <el-empty :description="description" :image-size="imageSize">
    <template #image>
      <svg class="empty-art" viewBox="0 0 120 120" :width="imageSize" :height="imageSize" aria-hidden="true">
        <!-- 无数据：展开的空白册页 -->
        <g v-if="variant === 'empty'">
          <path
            d="M24 44 Q41 37 58 43 L58 84 Q41 78 24 85 Z"
            fill="var(--ink-bg-paper)"
            stroke="var(--edge-strong)"
            stroke-width="2"
            stroke-linejoin="round"
          />
          <path
            d="M58 43 Q77 37 96 44 L96 85 Q77 78 58 84 Z"
            fill="var(--ink-bg-paper)"
            stroke="var(--edge-strong)"
            stroke-width="2"
            stroke-linejoin="round"
          />
          <path d="M58 43 L58 84" stroke="var(--edge-strong)" stroke-width="1.5" />
          <path
            d="M34 56 H50 M34 65 H46 M68 56 H86 M68 65 H80"
            fill="none"
            stroke="var(--ink-300)"
            stroke-width="1.5"
            stroke-linecap="round"
          />
          <path d="M92 27 l1.7 4 4 1.7 -4 1.7 -1.7 4 -1.7 -4 -4 -1.7 4 -1.7 Z" fill="var(--gold-400)" opacity="0.85" />
        </g>

        <!-- 无结果：放大镜 -->
        <g v-else-if="variant === 'search'">
          <circle cx="53" cy="53" r="26" fill="var(--ink-bg-paper)" stroke="var(--gold-400)" stroke-width="2.5" />
          <path d="M72.5 72.5 L91 91" stroke="var(--gold-500)" stroke-width="4" stroke-linecap="round" />
          <path
            d="M42 48 H64 M42 58 H55"
            fill="none"
            stroke="var(--ink-300)"
            stroke-width="1.5"
            stroke-linecap="round"
          />
          <path
            d="M63 63 l1.4 3.2 3.2 1.4 -3.2 1.4 -1.4 3.2 -1.4 -3.2 -3.2 -1.4 3.2 -1.4 Z"
            fill="var(--gold-400)"
            opacity="0.8"
          />
        </g>

        <!-- 图表无数据：折线坐标系 -->
        <g v-else-if="variant === 'chart'">
          <path
            d="M30 34 V86 H92"
            fill="none"
            stroke="var(--gold-400)"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <path
            d="M30 62 H92"
            fill="none"
            stroke="var(--ink-300)"
            stroke-width="1"
            stroke-dasharray="2 6"
            opacity="0.75"
            stroke-linecap="round"
          />
          <path
            d="M40 76 L56 60 L70 68 L86 44"
            fill="none"
            stroke="var(--gold-500)"
            stroke-width="2.5"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
          <circle cx="86" cy="44" r="4" fill="var(--gold-500)" stroke="var(--ink-bg-paper)" stroke-width="1.5" />
        </g>

        <!-- 加载失败：朱砂警示 -->
        <g v-else>
          <circle cx="60" cy="58" r="27" fill="var(--ink-bg-paper)" stroke="var(--cinnabar)" stroke-width="2.5" />
          <path d="M60 44 V62" stroke="var(--cinnabar)" stroke-width="3.2" stroke-linecap="round" />
          <circle cx="60" cy="71.5" r="2.2" fill="var(--cinnabar)" />
        </g>
      </svg>
    </template>
    <slot />
  </el-empty>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    /** 说明文字 */
    description?: string
    /** 插画变体：empty=无数据 / search=无结果 / chart=图表无数据 / error=加载失败 */
    variant?: 'empty' | 'search' | 'chart' | 'error'
    /** 插画尺寸（对齐原 el-empty image-size 用法） */
    imageSize?: number
  }>(),
  { description: '暂无数据', variant: 'empty', imageSize: 88 },
)
</script>

<style scoped>
/* finesse · register=product · shell=global: 空态 SVG 线条插画（宣纸金线，empty/search/chart/error 4 变体） */
.empty-art {
  display: block;
}
</style>

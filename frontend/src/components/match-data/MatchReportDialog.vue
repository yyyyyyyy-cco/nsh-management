<!-- 单场图文战报预览弹窗：加载全场数据 → 海报预览 → 导出 PNG（仅管理员入口） -->
<template>
  <el-dialog
    v-model="visible"
    title="单场图文战报"
    class="report-dialog"
    width="92%"
    top="4vh"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <!-- 加载骨架（固定高度块，避免布局跳动） -->
    <div v-if="loading" class="report-skeleton">
      <div class="sk sk-block" style="height:170px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:200px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:300px;border-radius:var(--radius-lg)" />
      <div class="sk sk-block" style="height:260px;border-radius:var(--radius-lg)" />
    </div>

    <!-- 加载失败 -->
    <el-empty v-else-if="loadFailed" description="战报数据加载失败">
      <el-button @click="loadReport">重试</el-button>
    </el-empty>

    <!-- 海报预览（视口滚动；导出截取内层 960px 原尺寸海报） -->
    <div v-else-if="report" class="poster-viewport">
      <div ref="posterRef" class="poster-frame">
        <MatchReportPoster :data="report" :schedule="schedule" />
      </div>
    </div>

    <template #footer>
      <el-button @click="visible = false">关闭</el-button>
      <el-button type="primary" :loading="exporting" :disabled="!report || loading" @click="onExport">导出 PNG</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

import { getLineup } from '@/api/lineups'
import { getIndicators } from '@/api/matchData'
import type { ScheduleInfo } from '@/types/schedule'
import MatchReportPoster from './report/MatchReportPoster.vue'
import { buildReportData, type MatchReportData } from './reportData'

const visible = defineModel<boolean>({ required: true })

const props = defineProps<{
  scheduleId: number
  schedule: ScheduleInfo | null
}>()

const loading = ref(false)
const loadFailed = ref(false)
const exporting = ref(false)
const report = ref<MatchReportData | null>(null)
const posterRef = ref<HTMLElement | null>(null)

watch(visible, (open) => {
  if (open) loadReport()
})

/** 加载数据：衍生指标记录（唯一数据源，仅统计我方阵营）+ 排表（判定我方阵营）。 */
async function loadReport() {
  loading.value = true
  loadFailed.value = false
  report.value = null
  try {
    const [indicators, lineup] = await Promise.all([
      getIndicators(props.scheduleId),
      // 排表仅用于判定我方阵营（口径与后端小队分析一致），失败时兜底取首条记录阵营
      getLineup(props.scheduleId).catch(() => null),
    ])
    report.value = buildReportData(indicators, lineup, props.schedule ?? null)
  } catch {
    // 错误提示由 http 拦截器统一处理，此处展示弹窗内错误态
    loadFailed.value = true
  } finally {
    loading.value = false
  }
}

/** 导出海报 PNG（html2canvas 动态加载，不进首屏 chunk；沿用排表总览导出先例）。 */
async function onExport() {
  const el = posterRef.value
  if (!el || !report.value) return
  exporting.value = true
  try {
    const { default: html2canvas } = await import('html2canvas')
    const canvas = await html2canvas(el, {
      backgroundColor: '#f7f3ea', // 与海报 CSS 底色（--ink-bg-page）一致
      scale: 2,
      useCORS: true,
      // 固定视口并取足够高度：长图完整渲染，不受当前窗口与滚动容器影响
      windowWidth: 1000,
      windowHeight: Math.max(window.innerHeight, 3000, el.scrollHeight + 80),
    })
    const link = document.createElement('a')
    const dateTag = props.schedule ? dayjs(props.schedule.match_time).format('YYYY-MM-DD') : String(props.scheduleId)
    link.download = `战报_${props.schedule?.opponent || ''}_${dateTag}.png`
    link.href = canvas.toDataURL('image/png')
    link.click()
    ElMessage.success('战报图片已导出')
  } catch (e) {
    ElMessage.error(`导出失败：${e instanceof Error ? e.message : '未知错误'}`)
  } finally {
    exporting.value = false
  }
}
</script>

<style scoped>
.report-skeleton {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 300px;
}

.poster-viewport {
  max-height: 72vh;
  overflow: auto;
}

.poster-frame {
  width: 960px;
  margin: 0 auto;
}

/* finesse · register=product · shell=match-report-poster: 预览视口滚动 + 960px 原尺寸导出；≤768px 横向滚动 */
@media (max-width: 768px) {
  .poster-frame {
    margin: 0; /* 窄屏左对齐，横向滚动查看（导出仍为 960px 原尺寸） */
  }

  .report-dialog :deep(.el-dialog__body) {
    padding: 12px;
  }
}
</style>

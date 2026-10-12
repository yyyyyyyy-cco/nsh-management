<template>
  <div class="arch-panel">
    <!-- 状态筛选：未提交 = 尚未填写链接（与录屏审核页同口径） -->
    <div class="arch-top">
      <el-select v-model="statusFilter" aria-label="状态筛选" placeholder="状态筛选" clearable style="width: 130px">
        <el-option v-for="opt in STATUS_OPTIONS" :key="opt.value" :label="opt.label" :value="opt.value" />
      </el-select>
    </div>

    <SkeletonTable v-if="showSkeleton && items.length === 0" :variant="isMobile ? 'rows' : 'table'" :rows="5" />
    <template v-else>
      <EmptyState v-if="!loading && filteredItems.length === 0" description="暂无录屏记录" :image-size="72" />
      <template v-else>
        <!-- 桌面端表格 -->
        <el-table v-if="!isMobile" :data="pagedItems">
          <el-table-column label="日期" min-width="110">
            <template #default="{ row }">{{ row.match_time.slice(0, 10) }}</template>
          </el-table-column>
          <el-table-column prop="opponent" label="对手" min-width="140" />
          <el-table-column label="局数" min-width="70" align="center">
            <template #default="{ row }">第{{ row.round_number }}局</template>
          </el-table-column>
          <el-table-column label="状态" min-width="90" align="center">
            <template #default="{ row }">
              <el-tag :type="tagType(row)" :effect="row.url ? 'light' : 'plain'" size="small">{{
                tagLabel(row)
              }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="录屏链接" min-width="260">
            <template #default="{ row }">
              <div v-if="row.url" class="url-display">
                <a :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link">{{ row.url }}</a>
                <el-button
                  link
                  type="primary"
                  size="small"
                  :icon="CopyDocument"
                  title="复制链接"
                  @click="onCopyUrl(row.url)"
                />
              </div>
              <span v-else class="empty-url">未提交</span>
            </template>
          </el-table-column>
          <el-table-column label="审核备注" min-width="150">
            <template #default="{ row }">
              <span v-if="row.review_remark">{{ row.review_remark }}</span>
              <span v-else class="empty-cell">-</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 移动端行列表 -->
        <div v-else class="arch-list">
          <div v-for="row in pagedItems" :key="`${row.schedule_id}-${row.round_number}`" class="arch-row">
            <div class="arch-row__main">
              <span class="arch-row__title">{{ row.opponent }}</span>
              <el-tag :type="tagType(row)" :effect="row.url ? 'light' : 'plain'" size="small">{{
                tagLabel(row)
              }}</el-tag>
            </div>
            <div class="arch-row__meta">
              <span>{{ row.match_time.slice(0, 10) }}</span>
              <span>第{{ row.round_number }}局</span>
            </div>
            <div class="arch-row__meta">
              <template v-if="row.url">
                <a :href="normalizeUrl(row.url)" target="_blank" rel="noopener" class="url-link arch-row__url">{{
                  row.url
                }}</a>
                <el-button
                  link
                  type="primary"
                  size="small"
                  :icon="CopyDocument"
                  title="复制链接"
                  @click="onCopyUrl(row.url)"
                />
              </template>
              <span v-else class="empty-url">未提交</span>
            </div>
            <div v-if="row.review_remark" class="arch-row__remark">审核备注：{{ row.review_remark }}</div>
          </div>
        </div>

        <!-- 分页：全量数据前端分页，口径与录屏 Tab 一致 -->
        <div v-if="filteredItems.length > 0" class="pager">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="filteredItems.length"
            :page-sizes="[20, 50, 100]"
            layout="total, sizes, prev, pager, next"
            background
          />
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { CopyDocument } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

import { getMemberRecordingHistory } from '@/api/members'
import type { MemberRecordingHistoryItem } from '@/types/memberArchive'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import { normalizeUrl, statusLabel, statusType } from '@/composables/useRecordingList'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const props = defineProps<{ memberId: number }>()

const STATUS_OPTIONS = [
  { value: 'unsubmitted', label: '未提交' },
  { value: 'pending', label: '待审核' },
  { value: 'approved', label: '已通过' },
  { value: 'rejected', label: '已驳回' },
] as const

// 初始即加载态，避免先渲染空态再切骨架的闪烁（与成员详情页口径一致）
const loading = ref(true)
const showSkeleton = useSkeletonLoading(loading)
const items = ref<MemberRecordingHistoryItem[]>([])
const statusFilter = ref('')

/** 展示状态：未提交 = 尚未填写链接（与录屏审核页「未提交」筛选同口径）。 */
function displayStatus(row: MemberRecordingHistoryItem): string {
  return !row.url && row.status === 'pending' ? 'unsubmitted' : row.status
}

function tagType(row: MemberRecordingHistoryItem): string {
  return displayStatus(row) === 'unsubmitted' ? 'info' : statusType(row.status)
}

function tagLabel(row: MemberRecordingHistoryItem): string {
  return displayStatus(row) === 'unsubmitted' ? '未提交' : statusLabel(row.status)
}

const filteredItems = computed(() => {
  if (!statusFilter.value) return items.value
  return items.value.filter((r) => displayStatus(r) === statusFilter.value)
})

// ===== 分页（全量数据前端分页）=====
const page = ref(1)
const pageSize = ref(20)
const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return filteredItems.value.slice(start, start + pageSize.value)
})

// 筛选或页大小变化时回到第一页（避免停留在越界页码显示空白）
watch([statusFilter, pageSize], () => {
  page.value = 1
})

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

/** 复制录屏链接到剪贴板（与录屏 Tab 同款行为）。 */
async function onCopyUrl(url: string) {
  try {
    await navigator.clipboard.writeText(url)
    ElMessage.success('录屏链接已复制')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

async function load() {
  loading.value = true
  try {
    items.value = await getMemberRecordingHistory(props.memberId)
  } catch {
    // 错误提示已由 http 拦截器统一处理，此处仅保证 loading 关闭
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  load()
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped src="./member-archive-shared.css"></style>

<style scoped>
.url-display {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}

.arch-row__url {
  flex: 1;
  min-width: 0;
  max-width: none;
}
</style>

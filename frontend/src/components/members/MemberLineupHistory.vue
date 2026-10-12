<template>
  <div class="arch-panel">
    <SkeletonTable v-if="showSkeleton && items.length === 0" :variant="isMobile ? 'rows' : 'table'" :rows="5" />
    <template v-else>
      <EmptyState v-if="!loading && items.length === 0" description="暂无排表记录" :image-size="72" />
      <template v-else>
        <!-- 桌面端表格 -->
        <el-table v-if="!isMobile" :data="pagedItems">
          <el-table-column label="日期" min-width="110">
            <template #default="{ row }">{{ row.match_time.slice(0, 10) }}</template>
          </el-table-column>
          <el-table-column prop="opponent" label="对手" min-width="140" />
          <el-table-column prop="category" label="分组" min-width="90" />
          <el-table-column label="队伍" min-width="70" align="center">
            <template #default="{ row }">第{{ row.team_index + 1 }}队</template>
          </el-table-column>
          <el-table-column label="位置" min-width="70" align="center">
            <template #default="{ row }">第{{ row.slot_index + 1 }}位</template>
          </el-table-column>
          <el-table-column label="槽位备注" min-width="150">
            <template #default="{ row }">
              <span v-if="row.slot_remark">{{ row.slot_remark }}</span>
              <span v-else class="empty-cell">-</span>
            </template>
          </el-table-column>
        </el-table>

        <!-- 移动端行列表 -->
        <div v-else class="arch-list">
          <div v-for="row in pagedItems" :key="row.schedule_id" class="arch-row">
            <div class="arch-row__main">
              <span class="arch-row__title">{{ row.opponent }}</span>
            </div>
            <div class="arch-row__meta">
              <span>{{ row.match_time.slice(0, 10) }}</span>
              <span>{{ row.category }} · 第{{ row.team_index + 1 }}队 · 第{{ row.slot_index + 1 }}位</span>
            </div>
            <div v-if="row.slot_remark" class="arch-row__remark">槽位备注：{{ row.slot_remark }}</div>
          </div>
        </div>

        <!-- 分页：全量数据前端分页，口径与录屏 Tab 一致 -->
        <div v-if="items.length > 0" class="pager">
          <el-pagination
            v-model:current-page="page"
            v-model:page-size="pageSize"
            :total="items.length"
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
import { computed, onMounted, onUnmounted, ref } from 'vue'

import { getMemberLineupHistory } from '@/api/members'
import type { MemberLineupHistoryItem } from '@/types/memberArchive'
import EmptyState from '@/components/common/EmptyState.vue'
import SkeletonTable from '@/components/common/SkeletonTable.vue'
import { useSkeletonLoading } from '@/composables/useSkeletonLoading'

const props = defineProps<{ memberId: number }>()

// 初始即加载态，避免先渲染空态再切骨架的闪烁（与成员详情页口径一致）
const loading = ref(true)
const showSkeleton = useSkeletonLoading(loading)
const items = ref<MemberLineupHistoryItem[]>([])

// ===== 分页（全量数据前端分页）=====
const page = ref(1)
const pageSize = ref(20)
const pagedItems = computed(() => {
  const start = (page.value - 1) * pageSize.value
  return items.value.slice(start, start + pageSize.value)
})

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

async function load() {
  loading.value = true
  try {
    items.value = await getMemberLineupHistory(props.memberId)
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

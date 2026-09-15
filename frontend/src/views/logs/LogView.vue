<template>
  <div class="log-view">
    <!-- 概览统计 -->
    <div class="stats-row">
      <el-card shadow="never" class="stat-card">
        <div class="stat-value num">{{ stats?.today_requests ?? 0 }}</div>
        <div class="stat-label">今日操作数</div>
      </el-card>
      <el-card shadow="never" class="stat-card" :class="{ 'stat-card--error': (stats?.today_errors ?? 0) > 0 }">
        <div class="stat-value num">{{ stats?.today_errors ?? 0 }}</div>
        <div class="stat-label">今日错误数</div>
      </el-card>
      <el-card shadow="never" class="stat-card stat-card--wide">
        <div class="stat-label stat-label--top">近 7 天错误分布</div>
        <div class="weekly-bar">
          <div v-for="item in stats?.weekly_errors ?? []" :key="item.date" class="weekly-item">
            <div class="weekly-col">
              <div class="weekly-count num">{{ item.count }}</div>
              <div
                class="weekly-block"
                :class="{ 'weekly-block--empty': item.count === 0 }"
                :style="{ height: weeklyHeight(item.count) + 'px' }"
              />
            </div>
            <div class="weekly-date">{{ item.date.slice(5) }}</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 日志列表 -->
    <el-card shadow="never" class="section-card">
      <template #header>
        <div class="card-header">
          <span>操作日志</span>
          <div class="header-actions">
            <el-button type="danger" plain @click="clearDialogVisible = true">清理日志</el-button>
            <el-button @click="onSearch">刷新</el-button>
          </div>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-input
          v-model="filters.username"
          placeholder="账号名"
          clearable
          style="width: 150px"
          @keyup.enter="onSearch"
        />
        <el-select v-model="filters.guild_id" placeholder="全部帮会" clearable style="width: 160px">
          <el-option
            v-for="g in guilds"
            :key="g.id"
            :label="g.name"
            :value="g.id"
          />
        </el-select>
        <el-select v-model="filters.module" placeholder="全部模块" clearable style="width: 140px">
          <el-option v-for="(label, key) in moduleLabels" :key="key" :label="label" :value="key" />
        </el-select>
        <el-select v-model="filters.level" placeholder="全部级别" clearable style="width: 120px">
          <el-option label="信息" value="info" />
          <el-option label="警告" value="warning" />
          <el-option label="错误" value="error" />
        </el-select>
        <el-date-picker
          v-model="dateRange"
          type="datetimerange"
          range-separator="至"
          start-placeholder="开始时间"
          end-placeholder="结束时间"
          style="width: 340px"
        />
        <el-button type="primary" @click="onSearch">查询</el-button>
        <el-button @click="onReset">重置</el-button>
      </div>

      <!-- 移动端（≤768px）：日志行列表，点击展开详情 -->
      <div v-if="isMobile" class="log-rows">
        <SkeletonTable v-if="showSkeleton && !logs.length" variant="rows" :rows="5" />
        <el-empty v-else-if="!loading && !logs.length" description="暂无日志记录" :image-size="72" />
        <div v-for="row in logs" :key="row.id" class="log-row" @click="showDetail(row)">
          <div class="log-row__main">
            <span class="log-row__name">{{ row.username || '匿名' }}</span>
            <el-tag :type="levelTagType(row.level)" effect="light" size="small">{{ levelLabel(row.level) }}</el-tag>
            <span class="log-row__module">{{ moduleLabels[row.module] ?? row.module }}</span>
            <span class="log-row__action log-row__action--tag">{{ actionLabels[row.action] ?? row.action }}</span>
          </div>
          <div class="log-row__meta">
            <span class="log-row__time num">{{ formatTime(row.created_at) }}</span>
            <span class="log-row__path">{{ row.method }} {{ row.path }}</span>
          </div>
        </div>
      </div>

      <SkeletonTable v-else-if="showSkeleton && !logs.length" variant="table" :rows="5" />
      <el-table v-else :data="logs" border @row-click="showDetail">
        <el-table-column label="时间" min-width="150">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="级别" width="80">
          <template #default="{ row }">
            <el-tag :type="levelTagType(row.level)" effect="light" size="small">
              {{ levelLabel(row.level) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作人" min-width="110">
          <template #default="{ row }">
            <span v-if="row.username">{{ row.username }}</span>
            <span v-else class="muted">匿名</span>
            <el-tag v-if="row.role" :type="roleTagType(row.role)" size="small" effect="plain" class="role-tag">
              {{ roleLabel(row.role) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="模块" width="90">
          <template #default="{ row }">{{ moduleLabels[row.module] ?? row.module }}</template>
        </el-table-column>
        <el-table-column label="动作" width="90">
          <template #default="{ row }">
            <el-tag :type="actionTagType(row.action)" size="small" effect="plain">
              {{ actionLabels[row.action] ?? row.action }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="请求" min-width="220" show-overflow-tooltip>
          <template #default="{ row }">
            <span class="method">{{ row.method }}</span>
            <span class="path">{{ row.path }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态码" width="90">
          <template #default="{ row }">
            <span :class="statusClass(row.status_code)">{{ row.status_code ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="ip" label="IP" min-width="110" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ip || '-' }}</template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>

    <!-- 详情弹窗 -->
    <el-dialog v-model="detailVisible" title="日志详情" width="640px">
      <el-descriptions v-if="detailRow" :column="2" border size="small">
        <el-descriptions-item label="时间">{{ formatTime(detailRow.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="级别">{{ levelLabel(detailRow.level) }}</el-descriptions-item>
        <el-descriptions-item label="账号">{{ detailRow.username ?? '匿名' }}</el-descriptions-item>
        <el-descriptions-item label="角色">{{ detailRow.role ? roleLabel(detailRow.role) : '-' }}</el-descriptions-item>
        <el-descriptions-item label="帮会 ID">{{ detailRow.guild_id ?? '-' }}</el-descriptions-item>
        <el-descriptions-item label="IP">{{ detailRow.ip || '-' }}</el-descriptions-item>
        <el-descriptions-item label="模块">{{ moduleLabels[detailRow.module] ?? detailRow.module }}</el-descriptions-item>
        <el-descriptions-item label="动作">{{ actionLabels[detailRow.action] ?? detailRow.action }}</el-descriptions-item>
        <el-descriptions-item label="请求" :span="2">
          {{ detailRow.method }} {{ detailRow.path }}
        </el-descriptions-item>
        <el-descriptions-item label="状态码">{{ detailRow.status_code ?? '-' }}</el-descriptions-item>
      </el-descriptions>
      <div v-if="detailRow?.detail" class="detail-block">
        <div class="detail-title">详细信息</div>
        <pre class="detail-pre">{{ formatDetail(detailRow.detail) }}</pre>
      </div>
    </el-dialog>

    <!-- 清理弹窗 -->
    <el-dialog v-model="clearDialogVisible" title="清理日志" width="420px">
      <p class="tip">删除指定天数之前的审计日志（文件日志按 10MB × 5 自动轮转，无需手动清理）。</p>
      <div class="clear-row">
        <span>清理</span>
        <el-input-number v-model="clearDays" :min="1" :max="3650" />
        <span>天前的日志</span>
      </div>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="clearing" @click="onClear">确认清理</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
/** 系统日志页（仅开发者）：审计日志查询、概览统计与清理。 */
import { onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import dayjs from 'dayjs'

import { clearLogs, getLogs, getLogStats } from '@/api/logs'
import { getGuilds } from '@/api/config'
import type { Guild } from '@/types/config'
import type { LogStats, OperationLog } from '@/types/log'
import { ElMessage, ElMessageBox } from 'element-plus'

import { useSkeletonLoading } from '@/composables/useSkeletonLoading'
import SkeletonTable from '@/components/common/SkeletonTable.vue'

const stats = ref<LogStats | null>(null)
const logs = ref<OperationLog[]>([])
const total = ref(0)
const loading = ref(false)
const showSkeleton = useSkeletonLoading(loading)
const page = ref(1)
const pageSize = ref(20)
const guilds = ref<Guild[]>([])

const filters = reactive<{
  username: string
  guild_id: number | null
  module: string | null
  level: string | null
}>({ username: '', guild_id: null, module: null, level: null })
const dateRange = ref<[Date, Date] | null>(null)

const detailVisible = ref(false)
const detailRow = ref<OperationLog | null>(null)
const clearDialogVisible = ref(false)
const clearDays = ref(90)
const clearing = ref(false)

// 移动端（≤768px）响应式切换
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => { isMobile.value = e.matches }

const moduleLabels: Record<string, string> = {
  members: '常驻库',
  schedules: '联赛日程',
  attendance: '出勤库',
  lineups: '排表',
  recordings: '录屏审核',
  'match-data': '数据分析',
  'squad-adjustments': '小队调整',
  config: '系统配置',
  developer: '开发者',
  auth: '认证',
  'my-stats': '个人战绩',
  other: '其他',
}

const actionLabels: Record<string, string> = {
  create: '创建',
  update: '更新',
  delete: '删除',
  login: '登录',
  login_failed: '登录失败',
  import: '导入',
  other: '其他',
}

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

function levelLabel(level: string): string {
  return level === 'error' ? '错误' : level === 'warning' ? '警告' : '信息'
}

function levelTagType(level: string): 'danger' | 'warning' | 'info' {
  return level === 'error' ? 'danger' : level === 'warning' ? 'warning' : 'info'
}

function roleLabel(role: string): string {
  return role === 'developer' ? '开发者' : role === 'admin' ? '管理员' : '帮众'
}

function roleTagType(role: string): '' | 'danger' | 'info' {
  return role === 'developer' ? '' : role === 'admin' ? 'danger' : 'info'
}

function actionTagType(action: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (action === 'delete' || action === 'login_failed') return 'danger'
  if (action === 'create') return 'success'
  if (action === 'update') return 'warning'
  if (action === 'login') return ''
  return 'info'
}

function statusClass(code: number | null): string {
  if (code == null) return ''
  if (code >= 500) return 'status-error'
  if (code >= 400) return 'status-warning'
  return 'status-ok'
}

function weeklyHeight(count: number): number {
  const max = Math.max(1, ...(stats.value?.weekly_errors ?? []).map((i) => i.count))
  return count === 0 ? 4 : Math.max(4, Math.round((count / max) * 56))
}

function formatDetail(detail: string): string {
  try {
    return JSON.stringify(JSON.parse(detail), null, 2)
  } catch {
    return detail
  }
}

async function load() {
  loading.value = true
  try {
    const res = await getLogs({
      username: filters.username || undefined,
      guild_id: filters.guild_id ?? undefined,
      module: filters.module ?? undefined,
      level: filters.level ?? undefined,
      start_time: dateRange.value?.[0]?.toISOString() ?? undefined,
      end_time: dateRange.value?.[1]?.toISOString() ?? undefined,
      page: page.value,
      page_size: pageSize.value,
    })
    logs.value = res.items
    total.value = res.total
  } finally {
    loading.value = false
  }
}

async function loadStats() {
  stats.value = await getLogStats()
}

function onSearch() {
  page.value = 1
  load()
  loadStats()
}

function onReset() {
  filters.username = ''
  filters.guild_id = null
  filters.module = null
  filters.level = null
  dateRange.value = null
  onSearch()
}

function showDetail(row: OperationLog) {
  detailRow.value = row
  detailVisible.value = true
}

async function onClear() {
  try {
    await ElMessageBox.confirm(
      `确定删除 ${clearDays.value} 天前的所有日志吗？此操作不可恢复。`,
      '清理日志',
      { type: 'warning' },
    )
  } catch {
    return
  }
  clearing.value = true
  try {
    const res = await clearLogs(clearDays.value)
    ElMessage.success(res.message)
    clearDialogVisible.value = false
    onSearch()
  } finally {
    clearing.value = false
  }
}

watch([page, pageSize], load)

onMounted(async () => {
  mq.addEventListener('change', onMqChange)
  load()
  loadStats()
  guilds.value = await getGuilds()
})

onUnmounted(() => {
  mq.removeEventListener('change', onMqChange)
})
</script>

<style scoped>
.log-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* ===== 概览统计 ===== */
.stats-row {
  display: flex;
  gap: 16px;
}

.stat-card {
  flex: 0 0 180px;
  text-align: center;
}

.stat-card--error :deep(.el-card__body) {
  background: rgba(217, 83, 79, 0.04);
}

.stat-card--wide {
  flex: 1;
  text-align: left;
}

.stat-value {
  font-size: 28px;
  font-weight: 600;
  color: var(--ink-900, #2b2620);
}

.stat-label {
  margin-top: 4px;
  font-size: 12px;
  color: var(--ink-500, #8a8378);
}

.stat-label--top {
  margin: 0 0 8px;
}

/* 近 7 天错误柱状分布（纯 CSS，避免引入图表库） */
.weekly-bar {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.weekly-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.weekly-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 76px;
}

.weekly-count {
  font-size: 12px;
  color: var(--ink-700, #4a443c);
  margin-bottom: 2px;
}

.weekly-block {
  width: 26px;
  border-radius: 4px 4px 0 0;
  background: linear-gradient(180deg, #d9534f 0%, #c9302c 100%);
}

.weekly-block--empty {
  background: var(--line-300, #e6dfce);
}

.weekly-date {
  font-size: 11px;
  color: var(--ink-500, #8a8378);
}

/* ===== 列表 ===== */
.section-card {
  flex: 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.filter-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.log-list :deep(.el-table__row) {
  cursor: pointer;
}

.muted {
  color: var(--ink-500, #8a8378);
}

.role-tag {
  margin-left: 4px;
}

.method {
  font-weight: 600;
  margin-right: 6px;
  color: var(--gold-700, #a67c1a);
}

.path {
  font-family: monospace;
  font-size: 12px;
}

.status-ok {
  color: var(--green-600, #4f9d5d);
}

.status-warning {
  color: var(--gold-700, #a67c1a);
}

.status-error {
  color: #c9302c;
  font-weight: 600;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 12px;
}

/* ===== 详情 ===== */
.detail-block {
  margin-top: 12px;
}

.detail-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}

.detail-pre {
  margin: 0;
  padding: 10px;
  max-height: 240px;
  overflow: auto;
  background: var(--paper-100, #faf6ec);
  border: 1px solid var(--line-300, #e6dfce);
  border-radius: 6px;
  font-size: 12px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.clear-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tip {
  margin: 0 0 12px;
  font-size: 13px;
  color: var(--ink-500, #8a8378);
}

/* 窄屏适配 */
@media (max-width: 768px) {
  .stats-row {
    flex-direction: column;
  }

  .stat-card {
    flex: none;
  }
}

/* ===== 移动端日志行列表（isMobile 时渲染，替换表格） ===== */
.log-rows {
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

.log-row {
  padding: 10px 2px;
  border-bottom: 1px solid var(--edge-faint);
  cursor: pointer;
}

.log-row:last-child {
  border-bottom: none;
}

.log-row:active {
  background: var(--gold-50);
  margin: 0 -2px;
  padding: 10px 0;
}

.log-row__main {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.log-row__name {
  font-weight: 600;
  color: var(--ink-900);
  font-size: 14px;
}

.log-row__module {
  font-size: 11px;
  color: var(--ink-400);
  margin-left: auto;
}

.log-row__action--tag {
  font-size: 11px;
  color: var(--gold-700);
  background: var(--gold-100);
  border-radius: var(--radius-xl);
  padding: 0 6px;
  line-height: 18px;
}

.log-row__meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  flex-wrap: wrap;
}

.log-row__time {
  font-size: 12px;
  color: var(--ink-400);
}

.log-row__path {
  font-size: 12px;
  color: var(--ink-500);
  font-family: monospace;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}
</style>

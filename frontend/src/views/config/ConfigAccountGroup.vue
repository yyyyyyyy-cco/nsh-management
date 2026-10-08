<template>
  <!-- 单个帮会账号分组卡片（可折叠） -->
  <el-card shadow="never" class="section-card">
    <template #header>
      <div class="card-header card-header--collapse" @click="collapsed = !collapsed">
        <span>{{ group.guildName }}</span>
        <div class="header-actions">
          <el-button v-if="group.guildId" type="primary" size="small" @click.stop="$emit('create', group.guildId)"
            >创建账号</el-button
          >
          <el-icon class="collapse-icon" :class="{ 'is-collapsed': collapsed }"><ArrowDown /></el-icon>
        </div>
      </div>
    </template>
    <el-collapse-transition>
      <div v-show="!collapsed">
        <!-- 移动端（≤768px）：账号行列表 -->
        <div v-if="isMobile" class="acct-rows">
          <div v-for="row in group.accounts" :key="row.id" class="acct-row">
            <div class="acct-row__main">
              <span class="acct-row__name">{{ row.username }}</span>
              <el-tag :type="roleTagType(row.role)" effect="light" size="small">{{ roleLabel(row.role) }}</el-tag>
              <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light" size="small">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </div>
            <div class="acct-row__actions">
              <el-button link type="primary" size="small" @click="$emit('edit', row)">编辑</el-button>
              <el-button
                v-if="row.role !== 'developer' && row.id !== currentUserId"
                link
                :type="row.status === 'active' ? 'warning' : 'success'"
                size="small"
                @click="$emit('toggle-status', row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button
                v-if="row.role !== 'developer' && row.id !== currentUserId"
                link
                type="danger"
                size="small"
                @click="$emit('delete', row)"
              >
                删除
              </el-button>
            </div>
          </div>
        </div>
        <el-table v-else :data="group.accounts" border>
          <el-table-column prop="username" label="登录名" min-width="130" />
          <el-table-column label="密码" min-width="100">
            <template #default="{ row }">
              <!-- 安全：明文密码仅开发者可见，管理员/帮众显示占位符 -->
              <span v-if="auth.isDeveloper && row.plain_password">{{ row.plain_password }}</span>
              <span v-else class="no-password">-</span>
            </template>
          </el-table-column>
          <el-table-column label="角色" min-width="80">
            <template #default="{ row }">
              <el-tag :type="roleTagType(row.role)" effect="light">
                {{ roleLabel(row.role) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="状态" min-width="80">
            <template #default="{ row }">
              <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light">
                {{ row.status === 'active' ? '启用' : '禁用' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" min-width="170">
            <template #default="{ row }">
              <el-button link type="primary" @click="$emit('edit', row)">编辑</el-button>
              <el-button
                v-if="row.role !== 'developer' && row.id !== currentUserId"
                link
                :type="row.status === 'active' ? 'warning' : 'success'"
                @click="$emit('toggle-status', row)"
              >
                {{ row.status === 'active' ? '禁用' : '启用' }}
              </el-button>
              <el-button
                v-if="row.role !== 'developer' && row.id !== currentUserId"
                link
                type="danger"
                @click="$emit('delete', row)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-collapse-transition>
  </el-card>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'

import type { Account } from '@/types/config'
import { useAuthStore } from '@/stores/auth'

defineProps<{
  group: { guildId: number | null; guildName: string; accounts: Account[] }
  isMobile: boolean
  currentUserId: number | undefined
}>()

defineEmits<{
  create: [guildId: number]
  edit: [row: Account]
  'toggle-status': [row: Account]
  delete: [row: Account]
}>()

const auth = useAuthStore()

/** 分组折叠状态（每个分组卡片独立维护） */
const collapsed = ref(false)

function roleTagType(role: string): string {
  return role === 'developer' ? '' : role === 'admin' ? 'danger' : 'info'
}

function roleLabel(role: string): string {
  return role === 'developer' ? '开发者' : role === 'admin' ? '管理员' : '帮众'
}
</script>

<style scoped>
.section-card {
  margin-bottom: 16px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header--collapse {
  cursor: pointer;
  user-select: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.collapse-icon {
  color: var(--ink-400);
  transition: transform 0.2s ease;
}

.collapse-icon.is-collapsed {
  transform: rotate(-90deg);
}

.no-password {
  color: var(--ink-200);
}

/* ===== 移动端账号行列表（isMobile 时渲染，替换表格） ===== */
.acct-rows {
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

.acct-row {
  padding: 10px 2px;
  border-bottom: 1px solid var(--edge-faint);
}

.acct-row:last-child {
  border-bottom: none;
}

.acct-row__main {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.acct-row__name {
  font-weight: 600;
  color: var(--ink-900);
  font-size: 14px;
}

.acct-row__actions {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 4px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

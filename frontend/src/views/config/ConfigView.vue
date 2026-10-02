<template>
  <div class="config-view">
    <el-tabs v-model="activeTab">
      <!-- 职业配置 -->
      <el-tab-pane v-if="!auth.isDeveloper" label="职业配置" name="profession">
        <ConfigProfessionPanel :is-mobile="isMobile" />
      </el-tab-pane>

      <!-- 图标设置（仅管理员） -->
      <el-tab-pane v-if="!auth.isDeveloper" label="图标设置" name="icon">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>侧边栏图标字</span></div>
          </template>
          <p class="tip">输入一个字符，作为侧边栏折叠按钮的显示图标（留空则显示默认图标）。</p>
          <div class="icon-set-row">
            <el-input aria-label="如：帮、战、金" v-model="iconChar" maxlength="4" placeholder="如：帮、战、金" style="width: 160px" />
            <el-button type="primary" :loading="saving" @click="onSaveIcon">保存</el-button>
            <el-button :loading="saving" @click="onClearIcon">清除</el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 账号管理（仅开发者） -->
      <el-tab-pane v-if="auth.isDeveloper" label="账号管理" name="account">
        <!-- 帮会管理（创建/更名/删除，帮会变更后刷新账号列表） -->
        <ConfigGuildPanel @changed="accountRef?.reload()" />

        <!-- 账号列表（按帮会分组） -->
        <ConfigAccountPanel ref="accountRef" :is-mobile="isMobile" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { updateGuildIcon } from '@/api/config'
import { useAuthStore } from '@/stores/auth'
import ConfigAccountPanel from './ConfigAccountPanel.vue'
import ConfigGuildPanel from './ConfigGuildPanel.vue'
import ConfigProfessionPanel from './ConfigProfessionPanel.vue'

const auth = useAuthStore()
const activeTab = ref(auth.isDeveloper ? 'account' : 'profession')
const saving = ref(false)

// 移动端（≤768px，与 MainLayout 抽屉断点一致）渲染行列表，桌面端渲染表格
const mq = window.matchMedia('(max-width: 768px)')
const isMobile = ref(mq.matches)
const onMqChange = (e: MediaQueryListEvent) => {
  isMobile.value = e.matches
}

const accountRef = ref<InstanceType<typeof ConfigAccountPanel>>()

// ===== 图标设置（仅管理员，设置本帮会侧边栏首字）=====
const iconChar = ref('')

async function onSaveIcon() {
  if (!auth.user?.guild_id) return
  saving.value = true
  try {
    await updateGuildIcon(auth.user.guild_id, iconChar.value)
    ElMessage.success('图标已更新')
    await auth.fetchMe()
  } finally {
    saving.value = false
  }
}

async function onClearIcon() {
  if (!auth.user?.guild_id) return
  saving.value = true
  try {
    await updateGuildIcon(auth.user.guild_id, '')
    iconChar.value = ''
    ElMessage.success('图标已清除，恢复默认')
    await auth.fetchMe()
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  mq.addEventListener('change', onMqChange)
  if (!auth.isDeveloper) {
    iconChar.value = auth.user?.guild_icon || ''
  }
})

onUnmounted(() => mq.removeEventListener('change', onMqChange))
</script>

<style scoped>
.config-view {
  padding: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tip {
  color: var(--ink-400);
  font-size: 13px;
  margin-bottom: 16px;
}

.icon-set-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>

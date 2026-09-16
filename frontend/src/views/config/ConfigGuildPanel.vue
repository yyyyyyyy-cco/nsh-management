<template>
  <!-- 帮会管理（仅开发者） -->
  <el-card shadow="never" class="section-card">
    <template #header>
      <div class="card-header">
        <span>帮会管理</span>
        <el-button type="primary" @click="showGuildDialog()">创建帮会</el-button>
      </div>
    </template>
    <el-table :data="guilds" border empty-text="暂无帮会，请先创建">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="name" label="帮会名称" min-width="200" />
      <el-table-column label="创建时间" min-width="160">
        <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" min-width="140">
        <template #default="{ row }">
          <el-button link type="primary" @click="showRenameDialog(row)">更名</el-button>
          <el-button link type="danger" @click="onDeleteGuild(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
  </el-card>

  <!-- 创建帮会弹窗 -->
  <el-dialog v-model="guildDialogVisible" title="创建帮会" width="420px">
    <el-form ref="guildFormRef" :model="guildForm" :rules="guildRules" label-width="90px">
      <el-form-item label="帮会名称" prop="name">
        <el-input v-model="guildForm.name" placeholder="请输入帮会名称" />
      </el-form-item>
      <el-form-item label="管理员密码" prop="admin_password">
        <el-input v-model="guildForm.admin_password" type="password" show-password placeholder="8-128 位，需含字母和数字" />
      </el-form-item>
      <el-form-item label="帮众密码" prop="member_password">
        <el-input v-model="guildForm.member_password" type="password" show-password placeholder="8-128 位，需含字母和数字" />
      </el-form-item>
      <p class="dialog-tip">将自动创建该帮会的管理员账号和帮众账号。密码保存后无法回查，请妥善保管，忘记可用重置密码功能。初始密码需为 8-128 位且包含字母和数字。</p>
    </el-form>
    <template #footer>
      <el-button @click="guildDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSaveGuild">确定</el-button>
    </template>
  </el-dialog>

  <!-- 帮会更名弹窗（仅开发者） -->
  <el-dialog v-model="renameDialogVisible" title="帮会更名" width="400px">
    <el-form label-width="80px">
      <el-form-item label="帮会名称">
        <el-input v-model="renameForm.name" placeholder="请输入新帮会名称" maxlength="64" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="renameDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSaveRename">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import type { FormInstance, FormItemRule, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import { createGuild, deleteGuild, getGuilds, renameGuild } from '@/api/config'
import type { Guild } from '@/types/config'

const emit = defineEmits<{ changed: [] }>()

const saving = ref(false)

// 帮会管理
const guilds = ref<Guild[]>([])
const guildDialogVisible = ref(false)
const guildFormRef = ref<FormInstance>()
const guildForm = ref({ name: '', admin_password: '', member_password: '' })

/** 密码校验：8-128 位且同时包含字母和数字（与后端一致） */
const passwordValidator: FormItemRule['validator'] = (_rule, value: string, callback) => {
  if (!value) {
    callback(new Error('请输入初始密码'))
  } else if (value.length < 8 || value.length > 128) {
    callback(new Error('密码长度需为 8-128 位'))
  } else if (!/[A-Za-z]/.test(value) || !/\d/.test(value)) {
    callback(new Error('密码需同时包含字母和数字'))
  } else {
    callback()
  }
}
const guildRules: FormRules = {
  name: [
    { required: true, message: '请输入帮会名称', trigger: 'blur' },
    { min: 2, max: 64, message: '长度在 2 到 64 个字符', trigger: 'blur' },
  ],
  admin_password: [{ required: true, validator: passwordValidator, trigger: 'blur' }],
  member_password: [{ required: true, validator: passwordValidator, trigger: 'blur' }],
}

onMounted(loadGuilds)

async function loadGuilds() {
  guilds.value = await getGuilds()
}

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}

// ===== 帮会操作 =====
function showGuildDialog() {
  guildForm.value = { name: '', admin_password: '', member_password: '' }
  guildDialogVisible.value = true
}

async function onDeleteGuild(guild: Guild) {
  await ElMessageBox.confirm(
    `确定删除帮会「${guild.name}」吗？该操作将级联删除该帮会的所有账号、成员、赛程、出勤、排表、录屏与分析数据，且不可恢复！`,
    '危险操作',
    { type: 'warning', confirmButtonText: '确认删除' },
  )
  const result = await deleteGuild(guild.id)
  ElMessage.success(result.message)
  await loadGuilds()
  emit('changed')
}

// ===== 帮会更名（仅开发者）=====
const renameDialogVisible = ref(false)
const renameForm = ref<{ id: number; name: string }>({ id: 0, name: '' })

function showRenameDialog(guild: Guild) {
  renameForm.value = { id: guild.id, name: guild.name }
  renameDialogVisible.value = true
}

async function onSaveRename() {
  const name = renameForm.value.name.trim()
  if (name.length < 2 || name.length > 64) {
    ElMessage.warning('帮会名称长度需在 2 到 64 个字符')
    return
  }
  saving.value = true
  try {
    const result = await renameGuild(renameForm.value.id, name)
    ElMessage.success(`帮会已更名为「${result.name}」`)
    renameDialogVisible.value = false
    await loadGuilds()
    emit('changed')
  } finally {
    saving.value = false
  }
}

async function onSaveGuild() {
  const valid = await guildFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const result = await createGuild(guildForm.value)
    ElMessage.success(`帮会「${result.name}」创建成功`)
    guildDialogVisible.value = false
    await loadGuilds()
    emit('changed')
  } finally {
    saving.value = false
  }
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

.dialog-tip {
  color: var(--ink-400);
  font-size: 12px;
  margin: 0;
  padding-left: 80px;
}

/* ===== 移动端适配 ===== */
@media (max-width: 768px) {
  .card-header {
    flex-wrap: wrap;
    gap: 8px;
  }

  .dialog-tip {
    padding-left: 0;
  }
}
</style>

<template>
  <!-- 账号列表（按帮会分组，可折叠；分组卡片见 ConfigAccountGroup） -->
  <ConfigAccountGroup
    v-for="group in accountGroups"
    :key="group.guildId ?? 'none'"
    :group="group"
    :is-mobile="isMobile"
    :current-user-id="currentUserId"
    @create="(guildId: number) => showAccountDialog(undefined, guildId)"
    @edit="showAccountDialog"
    @toggle-status="onToggleStatus"
    @delete="onDeleteAccount"
  />

  <!-- 账号编辑弹窗 -->
  <el-dialog
    v-model="accountDialogVisible"
    :title="editingAccount ? '编辑账号' : '创建账号'"
    width="420px"
  >
    <el-form ref="accountFormRef" :model="accountForm" :rules="accountRules" label-width="80px">
      <el-form-item label="登录名" prop="username">
        <el-input v-model="accountForm.username" placeholder="请输入登录名" />
      </el-form-item>
      <el-form-item label="密码" prop="password">
        <el-input
          v-model="accountForm.password"
          type="password"
          :placeholder="editingAccount ? '留空则不修改' : '请输入密码'"
          show-password
        />
      </el-form-item>
      <el-form-item v-if="!editingAccount" label="角色" prop="role">
        <el-select v-model="accountForm.role" style="width: 100%">
          <el-option label="管理员" value="admin" />
          <el-option label="帮众" value="member" />
        </el-select>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="accountDialogVisible = false">取消</el-button>
      <el-button type="primary" :loading="saving" @click="onSaveAccount">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'

import {
  createAccount,
  deleteAccount,
  getAccounts,
  updateAccount,
  updateAccountStatus,
} from '@/api/config'
import type { Account } from '@/types/config'
import { useAuthStore } from '@/stores/auth'
import ConfigAccountGroup from './ConfigAccountGroup.vue'

defineProps<{ isMobile: boolean }>()

const auth = useAuthStore()

const saving = ref(false)

const accounts = ref<Account[]>([])
const accountDialogVisible = ref(false)
const editingAccount = ref<Account | null>(null)
const accountFormRef = ref<FormInstance>()
const accountForm = ref({
  username: '',
  password: '',
  role: 'member' as 'admin' | 'member',
  guildId: null as number | null,
})
const accountRules: FormRules = {
  username: [
    { required: true, message: '请输入登录名', trigger: 'blur' },
    { min: 3, max: 64, message: '长度在 3 到 64 个字符', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 128, message: '长度在 6 到 128 个字符', trigger: 'blur' },
  ],
  role: [{ required: true, message: '请选择角色', trigger: 'change' }],
}

const currentUserId = computed(() => auth.user?.id)

// 账号按帮会分组
const accountGroups = computed(() => {
  const map = new Map<number | null, { guildId: number | null; guildName: string; accounts: Account[] }>()
  for (const a of accounts.value) {
    const key = a.guild_id
    if (!map.has(key)) {
      map.set(key, {
        guildId: key,
        guildName: a.guild_name ?? '无帮会（开发者）',
        accounts: [],
      })
    }
    map.get(key)!.accounts.push(a)
  }
  return [...map.values()]
})

onMounted(loadAccounts)

async function loadAccounts() {
  accounts.value = await getAccounts()
}

// ===== 账号操作 =====
function showAccountDialog(account?: Account, guildId?: number | null) {
  editingAccount.value = account || null
  accountForm.value = {
    username: account?.username || '',
    password: '',
    role: (account?.role === 'developer' ? 'member' : account?.role) || 'member',
    guildId: account?.guild_id ?? guildId ?? null,
  }
  accountDialogVisible.value = true
}

async function onSaveAccount() {
  const valid = await accountFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingAccount.value) {
      const data: { username?: string; password?: string } = {}
      if (accountForm.value.username !== editingAccount.value.username) {
        data.username = accountForm.value.username
      }
      if (accountForm.value.password) {
        data.password = accountForm.value.password
      }
      await updateAccount(editingAccount.value.id, data)
      ElMessage.success('账号更新成功')
    } else {
      await createAccount({
        username: accountForm.value.username,
        password: accountForm.value.password,
        role: accountForm.value.role,
        guild_id: accountForm.value.guildId,
      })
      ElMessage.success('账号创建成功')
    }
    accountDialogVisible.value = false
    loadAccounts()
  } finally {
    saving.value = false
  }
}

async function onToggleStatus(account: Account) {
  const newStatus = account.status === 'active' ? 'disabled' : 'active'
  const action = newStatus === 'active' ? '启用' : '禁用'

  await ElMessageBox.confirm(`确定${action}账号「${account.username}」吗？`, '提示', {
    type: 'warning',
  })

  await updateAccountStatus(account.id, { status: newStatus })
  ElMessage.success(`账号已${action}`)
  loadAccounts()
}

async function onDeleteAccount(account: Account) {
  await ElMessageBox.confirm(`确定删除账号「${account.username}」吗？删除后不可恢复！`, '危险操作', {
    type: 'warning',
    confirmButtonText: '确认删除',
  })
  const result = await deleteAccount(account.id)
  ElMessage.success(result.message)
  loadAccounts()
}

/** 供父级（帮会变更后）刷新账号列表。 */
function reload() {
  loadAccounts()
}

defineExpose({ reload })
</script>

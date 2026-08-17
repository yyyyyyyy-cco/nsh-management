<template>
  <div class="config-view">
    <el-tabs v-model="activeTab">
      <!-- 职业配置 -->
      <el-tab-pane label="职业配置" name="profession">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>职业目标人数配置</span>
              <el-button type="primary" :loading="saving" @click="onSaveProfessions">保存配置</el-button>
            </div>
          </template>
          <p class="tip">配置各职业的目标人数，用于出勤库的职业缺口分析。</p>
          <el-table :data="professionConfigs" border>
            <el-table-column prop="profession" label="职业" width="120" />
            <el-table-column label="目标人数" width="200">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.target_count"
                  :min="0"
                  :max="999"
                  size="small"
                  style="width: 120px"
                />
              </template>
            </el-table-column>
            <el-table-column label="说明">
              <template #default="{ row }">
                <span class="profession-tip">{{ getProfessionTip(row.profession) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 账号管理 -->
      <el-tab-pane label="账号管理" name="account">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>账号列表</span>
              <el-button type="primary" @click="showAccountDialog()">创建账号</el-button>
            </div>
          </template>
          <el-table :data="accounts" border>
            <el-table-column prop="username" label="登录名" min-width="150" />
            <el-table-column label="角色" width="100">
              <template #default="{ row }">
                <el-tag :type="row.role === 'admin' ? 'danger' : 'info'" effect="light">
                  {{ row.role === 'admin' ? '管理员' : '帮众' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === 'active' ? 'success' : 'warning'" effect="light">
                  {{ row.status === 'active' ? '启用' : '禁用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="创建时间" width="180">
              <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
            </el-table-column>
            <el-table-column label="操作" width="200" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="showAccountDialog(row)">编辑</el-button>
                <el-button
                  v-if="row.id !== currentUserId"
                  link
                  :type="row.status === 'active' ? 'warning' : 'success'"
                  @click="onToggleStatus(row)"
                >
                  {{ row.status === 'active' ? '禁用' : '启用' }}
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 账号编辑弹窗 -->
    <el-dialog
      v-model="accountDialogVisible"
      :title="editingAccount ? '编辑账号' : '创建账号'"
      width="400px"
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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import dayjs from 'dayjs'

import {
  batchUpdateProfessionConfigs,
  createAccount,
  getAccounts,
  getProfessionConfigs,
  updateAccount,
  updateAccountStatus,
} from '@/api/config'
import type { Account, ProfessionConfig } from '@/types/config'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const activeTab = ref('profession')
const saving = ref(false)

// 职业配置
const professionConfigs = ref<ProfessionConfig[]>([])

// 账号管理
const accounts = ref<Account[]>([])
const accountDialogVisible = ref(false)
const editingAccount = ref<Account | null>(null)
const accountFormRef = ref<FormInstance>()
const accountForm = ref({
  username: '',
  password: '',
  role: 'member' as 'admin' | 'member',
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

const professionTips: Record<string, string> = {
  铁衣: '主T，前排坦克',
  素问: '治疗，奶妈',
  神相: '远程输出',
  碎梦: '近战刺客',
  血河: '近战输出',
  玄机: '远程输出',
  九灵: '远程召唤',
  潮光: '远程辅助',
  龙吟: '近战输出',
  鸿音: '远程辅助',
  沧澜: '近战控制',
}

onMounted(load)

async function load() {
  await Promise.all([loadProfessions(), loadAccounts()])
}

async function loadProfessions() {
  professionConfigs.value = await getProfessionConfigs()
}

async function loadAccounts() {
  accounts.value = await getAccounts()
}

function getProfessionTip(profession: string): string {
  return professionTips[profession] || ''
}

async function onSaveProfessions() {
  saving.value = true
  try {
    const configs = professionConfigs.value.map((c) => ({
      profession: c.profession,
      target_count: c.target_count,
    }))
    const result = await batchUpdateProfessionConfigs(configs)
    ElMessage.success(result.message)
  } finally {
    saving.value = false
  }
}

function showAccountDialog(account?: Account) {
  editingAccount.value = account || null
  accountForm.value = {
    username: account?.username || '',
    password: '',
    role: account?.role || 'member',
  }
  accountDialogVisible.value = true
}

async function onSaveAccount() {
  const valid = await accountFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingAccount.value) {
      // 编辑账号
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
      // 创建账号
      await createAccount(accountForm.value)
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

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}
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
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 16px;
}

.profession-tip {
  color: #9ca3af;
  font-size: 12px;
}
</style>

<template>
  <div class="config-view">
    <el-tabs v-model="activeTab">
      <!-- 职业配置 -->
      <el-tab-pane v-if="!auth.isDeveloper" label="职业配置" name="profession">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>职业目标人数配置</span>
              <el-button type="primary" :loading="saving" @click="onSaveProfessions">保存配置</el-button>
            </div>
          </template>
          <p class="tip">配置各职业的目标人数，用于出勤库的职业缺口分析。</p>
          <el-table :data="professionConfigs" border>
            <el-table-column prop="profession" label="职业" min-width="100">
              <template #default="{ row }">
                <span class="prof-cell">
                  <i class="prof-dot" :style="{ background: profColor(row.profession) }" />
                  {{ row.profession }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="目标人数" min-width="150">
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
                <el-input
                  v-model="row.remark"
                  placeholder="说明（可选）"
                  size="small"
                  maxlength="255"
                  clearable
                />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 图标设置（仅管理员） -->
      <el-tab-pane v-if="!auth.isDeveloper" label="图标设置" name="icon">
        <el-card shadow="never">
          <template #header>
            <div class="card-header"><span>侧边栏图标字</span></div>
          </template>
          <p class="tip">输入一个字符，作为侧边栏折叠按钮的显示图标（留空则显示默认图标）。</p>
          <div class="icon-set-row">
            <el-input v-model="iconChar" maxlength="4" placeholder="如：帮、战、金" style="width: 160px" />
            <el-button type="primary" :loading="saving" @click="onSaveIcon">保存</el-button>
            <el-button :loading="saving" @click="onClearIcon">清除</el-button>
          </div>
        </el-card>
      </el-tab-pane>

      <!-- 账号管理（仅开发者） -->
      <el-tab-pane v-if="auth.isDeveloper" label="账号管理" name="account">
        <!-- 创建帮会按钮（仅开发者） -->
        <el-card v-if="auth.isDeveloper" shadow="never" class="section-card">
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

        <!-- 账号列表（按帮会分组，可折叠） -->
        <el-card v-for="group in accountGroups" :key="group.guildId ?? 'none'" shadow="never" class="section-card">
          <template #header>
            <div class="card-header card-header--collapse" @click="toggleGroup(group.guildId)">
              <span>{{ group.guildName }}</span>
              <div class="header-actions">
                <el-button v-if="group.guildId" type="primary" size="small" @click.stop="showAccountDialog(undefined, group.guildId)">创建账号</el-button>
                <el-icon class="collapse-icon" :class="{ 'is-collapsed': isGroupCollapsed(group.guildId) }"><ArrowDown /></el-icon>
              </div>
            </div>
          </template>
          <el-collapse-transition>
            <div v-show="!isGroupCollapsed(group.guildId)">
              <el-table :data="group.accounts" border>
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
                    <el-button link type="primary" @click="showAccountDialog(row)">编辑</el-button>
                    <el-button
                      v-if="row.role !== 'developer' && row.id !== currentUserId"
                      link
                      :type="row.status === 'active' ? 'warning' : 'success'"
                      @click="onToggleStatus(row)"
                    >
                      {{ row.status === 'active' ? '禁用' : '启用' }}
                    </el-button>
                    <el-button
                      v-if="row.role !== 'developer' && row.id !== currentUserId"
                      link
                      type="danger"
                      @click="onDeleteAccount(row)"
                    >
                      删除
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-collapse-transition>
        </el-card>
      </el-tab-pane>
    </el-tabs>

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
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import type { FormInstance, FormItemRule, FormRules } from 'element-plus'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

import {
  batchUpdateProfessionConfigs,
  createAccount,
  createGuild,
  deleteAccount,
  deleteGuild,
  getAccounts,
  getGuilds,
  getProfessionConfigs,
  renameGuild,
  updateAccount,
  updateAccountStatus,
  updateGuildIcon,
} from '@/api/config'
import type { Account, Guild, ProfessionConfig } from '@/types/config'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const activeTab = ref(auth.isDeveloper ? 'account' : 'profession')
const saving = ref(false)

// 职业配置
const professionConfigs = ref<ProfessionConfig[]>([])

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

// 账号管理
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

// 账号分组卡片折叠状态
const collapsedGroups = ref<Set<number | null>>(new Set())

function isGroupCollapsed(guildId: number | null): boolean {
  return collapsedGroups.value.has(guildId)
}

function toggleGroup(guildId: number | null) {
  const next = new Set(collapsedGroups.value)
  if (next.has(guildId)) {
    next.delete(guildId)
  } else {
    next.add(guildId)
  }
  collapsedGroups.value = next
}

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

/** 职业色映射（依据 ui-style-guide §9）。 */
const PROF_COLORS: Record<string, string> = {
  铁衣: '#ffc800', 素问: '#FF9CF2', 神相: '#3E6BF4', 碎梦: '#00FFFB',
  血河: '#F04545', 玄机: '#f6ff00', 九灵: '#8B5CF6', 潮光: '#4F95FF',
  龙吟: '#3fe155', 鸿音: '#C6834D', 沧澜: '#605EF0',
}

function profColor(prof: string) {
  return PROF_COLORS[prof] || '#c9a13b'
}

onMounted(load)

async function load() {
  const tasks: Promise<void>[] = [loadAccounts()]
  if (auth.isDeveloper) {
    tasks.push(loadGuilds())
  } else {
    tasks.push(loadProfessions())
    iconChar.value = auth.user?.guild_icon || ''
  }
  await Promise.all(tasks)
}

async function loadProfessions() {
  professionConfigs.value = await getProfessionConfigs()
}

async function loadGuilds() {
  guilds.value = await getGuilds()
}

async function loadAccounts() {
  accounts.value = await getAccounts()
}

function roleTagType(role: string): string {
  return role === 'developer' ? '' : role === 'admin' ? 'danger' : 'info'
}

function roleLabel(role: string): string {
  return role === 'developer' ? '开发者' : role === 'admin' ? '管理员' : '帮众'
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
  await Promise.all([loadGuilds(), loadAccounts()])
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
    await Promise.all([loadGuilds(), loadAccounts()])
  } finally {
    saving.value = false
  }
}

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

async function onDeleteAccount(account: Account) {
  await ElMessageBox.confirm(`确定删除账号「${account.username}」吗？删除后不可恢复！`, '危险操作', {
    type: 'warning',
    confirmButtonText: '确认删除',
  })
  const result = await deleteAccount(account.id)
  ElMessage.success(result.message)
  loadAccounts()
}

async function onSaveGuild() {
  const valid = await guildFormRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    const result = await createGuild(guildForm.value)
    ElMessage.success(`帮会「${result.name}」创建成功`)
    guildDialogVisible.value = false
    await Promise.all([loadGuilds(), loadAccounts()])
  } finally {
    saving.value = false
  }
}

// ===== 职业配置操作 =====
async function onSaveProfessions() {
  saving.value = true
  try {
    const configs = professionConfigs.value.map((c) => ({
      profession: c.profession,
      target_count: c.target_count,
      remark: c.remark,
    }))
    const result = await batchUpdateProfessionConfigs(configs)
    ElMessage.success(result.message)
  } finally {
    saving.value = false
  }
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

function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm')
}
</script>

<style scoped>
.config-view {
  padding: 0;
}

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

.tip {
  color: #6b7280;
  font-size: 13px;
  margin-bottom: 16px;
}

.icon-set-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.dialog-tip {
  color: #9ca3af;
  font-size: 12px;
  margin: 0;
  padding-left: 80px;
}

.profession-tip {
  color: var(--ink-400);
  font-size: 12px;
}

.prof-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: var(--ink-900);
}

.prof-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.no-password {
  color: var(--ink-200);
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

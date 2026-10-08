/** 系统配置 API。 */
import http from '@/api/http'
import type {
  Account,
  AccountCreateRequest,
  AccountStatusUpdateRequest,
  AccountUpdateRequest,
  Guild,
  GuildCreateRequest,
  ProfessionConfig,
} from '@/types/config'

// ========== 职业配置 ==========

/** 获取职业配置列表 */
export async function getProfessionConfigs(): Promise<ProfessionConfig[]> {
  return http.get('/config/professions')
}

/** 更新单个职业配置 */
export async function updateProfessionConfig(profession: string, targetCount: number): Promise<ProfessionConfig> {
  return http.put(`/config/professions/${profession}`, { target_count: targetCount })
}

/** 批量更新职业配置 */
export async function batchUpdateProfessionConfigs(
  configs: Array<{ profession: string; target_count: number }>,
): Promise<{ message: string }> {
  return http.put('/config/professions', { configs })
}

// ========== 账号管理 ==========

/** 获取账号列表 */
export async function getAccounts(): Promise<Account[]> {
  return http.get('/config/accounts')
}

/** 创建账号 */
export async function createAccount(data: AccountCreateRequest): Promise<Account> {
  return http.post('/config/accounts', data)
}

/** 更新账号信息 */
export async function updateAccount(userId: number, data: AccountUpdateRequest): Promise<Account> {
  return http.put(`/config/accounts/${userId}`, data)
}

/** 更新账号状态 */
export async function updateAccountStatus(userId: number, data: AccountStatusUpdateRequest): Promise<Account> {
  return http.put(`/config/accounts/${userId}/status`, data)
}

/** 删除账号 */
export async function deleteAccount(userId: number): Promise<{ message: string }> {
  return http.delete(`/config/accounts/${userId}`)
}

// ========== 帮会管理 ==========

/** 获取帮会列表 */
export async function getGuilds(): Promise<Guild[]> {
  return http.get('/config/guilds')
}

/** 创建帮会 */
export async function createGuild(data: GuildCreateRequest): Promise<Guild> {
  return http.post('/config/guilds', data)
}

/** 删除帮会（级联删除全部关联数据） */
export async function deleteGuild(guildId: number): Promise<{ message: string }> {
  return http.delete(`/config/guilds/${guildId}`)
}

/** 帮会更名（仅开发者） */
export function renameGuild(guildId: number, name: string): Promise<Guild> {
  return http.put(`/config/guilds/${guildId}`, { name })
}

/** 设置本帮会图标字（管理员，空串清除） */
export function updateGuildIcon(guildId: number, iconChar: string): Promise<Guild> {
  return http.put(`/config/guilds/${guildId}/icon`, { icon_char: iconChar })
}

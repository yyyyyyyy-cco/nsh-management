/** 系统配置类型定义。 */

/** 职业配置 */
export interface ProfessionConfig {
  id: number
  guild_id: number | null
  profession: string
  target_count: number
  remark?: string | null
}

/** 账号信息 */
export interface Account {
  id: number
  guild_id: number | null
  guild_name: string | null
  username: string
  plain_password: string | null
  role: 'developer' | 'admin' | 'member'
  status: 'active' | 'disabled'
  created_at: string
}

/** 创建账号请求 */
export interface AccountCreateRequest {
  username: string
  password: string
  role: 'admin' | 'member'
  guild_id: number | null
}

/** 更新账号请求 */
export interface AccountUpdateRequest {
  username?: string
  password?: string
}

/** 更新账号状态请求 */
export interface AccountStatusUpdateRequest {
  status: 'active' | 'disabled'
}

/** 帮会信息 */
export interface Guild {
  id: number
  name: string
  icon_char?: string | null
  created_at: string
}

/** 创建帮会请求（管理员/帮众初始密码由创建者指定） */
export interface GuildCreateRequest {
  name: string
  admin_password: string
  member_password: string
}

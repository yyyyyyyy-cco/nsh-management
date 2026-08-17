/** 系统配置类型定义。 */

/** 职业配置 */
export interface ProfessionConfig {
  id: number
  guild_id: number
  profession: string
  target_count: number
}

/** 账号信息 */
export interface Account {
  id: number
  guild_id: number
  username: string
  role: 'admin' | 'member'
  status: 'active' | 'disabled'
  created_at: string
}

/** 创建账号请求 */
export interface AccountCreateRequest {
  username: string
  password: string
  role: 'admin' | 'member'
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

/** 用户信息。 */
export interface UserInfo {
  id: number
  guild_id: number | null
  guild_name?: string | null
  guild_icon?: string | null
  username: string
  role: 'developer' | 'admin' | 'member'
  status: string
}

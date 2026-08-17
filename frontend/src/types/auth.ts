/** 用户信息。 */
export interface UserInfo {
  id: number
  guild_id: number | null
  username: string
  role: 'developer' | 'admin' | 'member'
  status: string
}

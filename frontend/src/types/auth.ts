/** 用户信息。 */
export interface UserInfo {
  id: number
  guild_id: number
  username: string
  role: 'admin' | 'member'
  status: string
}

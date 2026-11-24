/** 成员信息。 */
export type MemberStatus = 'formal' | 'substitute' | 'external'

export interface MemberInfo {
  id: number
  guild_id: number
  name: string
  main_profession: string
  sub_profession: string | null
  status: MemberStatus
  remark: string | null
  created_at: string
}

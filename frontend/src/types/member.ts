/** 成员信息。 */
export interface MemberInfo {
  id: number
  guild_id: number
  name: string
  main_profession: string
  sub_profession: string | null
  status: 'formal' | 'substitute'
  remark: string | null
  created_at: string
}

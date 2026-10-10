/** 职业目录类型定义（与 backend/app/schemas/profession.py 对齐）。 */

/** 职业目录条目（GET /professions，含停用职业）。 */
export interface ProfessionOut {
  id: number
  name: string
  sort_order: number
  color: string
  is_active: boolean
  created_at: string
}

/** 新增职业请求。 */
export interface ProfessionCreateRequest {
  name: string
  color?: string
  sort_order?: number
}

/** 更新职业请求（局部；name 变更触发后端改名级联，is_active=false 即停用）。 */
export interface ProfessionUpdateRequest {
  name?: string | null
  color?: string | null
  sort_order?: number | null
  is_active?: boolean | null
}

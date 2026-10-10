/** 职业目录 API。 */
import http from '@/api/http'
import type { ProfessionCreateRequest, ProfessionOut, ProfessionUpdateRequest } from '@/types/profession'

/** 获取职业目录（全量含停用；前端据此渲染选择器与历史数据配色）。 */
export async function getProfessions(): Promise<ProfessionOut[]> {
  return http.get('/professions')
}

/** 新增职业（仅开发者；名称含停用职业全局唯一，排序缺省追加末位）。 */
export async function createProfession(data: ProfessionCreateRequest): Promise<ProfessionOut> {
  return http.post('/professions', data)
}

/** 更新职业（仅开发者；is_active=false 即停用，至少保留一个启用职业）。 */
export async function updateProfession(id: number, data: ProfessionUpdateRequest): Promise<ProfessionOut> {
  return http.put(`/professions/${id}`, data)
}

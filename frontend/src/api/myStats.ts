/** 个人战绩查询 API。 */
import http from '@/api/http'
import type { MyStatsResponse } from '@/types/myStats'

/** 按游戏 ID 查询个人历史战绩 */
export async function getMyStats(playerName: string): Promise<MyStatsResponse> {
  return http.get('/my-stats', { params: { player_name: playerName } })
}

/** 模糊搜索匹配的玩家名（自动补全候选），按数据量排序 */
export async function getPlayerNames(q: string): Promise<string[]> {
  const res: { names: string[] } = await http.get('/my-stats/player-names', { params: { q } })
  return res.names
}

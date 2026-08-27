/** 个人战绩查询 API。 */
import http from '@/api/http'
import type { MyStatsResponse } from '@/types/myStats'

/** 按游戏 ID 查询个人历史战绩 */
export async function getMyStats(playerName: string): Promise<MyStatsResponse> {
  return http.get('/my-stats', { params: { player_name: playerName } })
}

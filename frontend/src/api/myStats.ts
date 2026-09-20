/** 个人战绩查询 API。 */
import http from '@/api/http'
import type { MyStatsResponse } from '@/types/myStats'

/** 按游戏 ID 查询个人历史战绩（默认合并该成员已确认的新旧 ID；false 为仅查此 ID） */
export async function getMyStats(playerName: string, mergeAliases = true): Promise<MyStatsResponse> {
  return http.get('/my-stats', { params: { player_name: playerName, merge_aliases: mergeAliases } })
}

/** 模糊搜索匹配的玩家名（自动补全候选：比赛数据 + 已确认改名关系的新旧名称） */
export async function getPlayerNames(q: string): Promise<string[]> {
  const res: { names: string[] } = await http.get('/my-stats/player-names', { params: { q } })
  return res.names
}

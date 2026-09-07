/** 系统日志类型定义。 */

/** 审计日志 */
export interface OperationLog {
  id: number
  user_id: number | null
  username: string | null
  role: string | null
  guild_id: number | null
  module: string
  action: string
  method: string
  path: string
  status_code: number | null
  level: 'info' | 'warning' | 'error'
  detail: string | null
  ip: string | null
  created_at: string
}

/** 日志分页列表 */
export interface LogList {
  total: number
  items: OperationLog[]
}

/** 近 7 天错误分布项 */
export interface WeeklyErrorItem {
  date: string
  count: number
}

/** 日志概览统计 */
export interface LogStats {
  today_requests: number
  today_errors: number
  weekly_errors: WeeklyErrorItem[]
}

/** 日志查询参数 */
export interface LogQuery {
  username?: string | null
  guild_id?: number | null
  module?: string | null
  level?: string | null
  start_time?: string | null
  end_time?: string | null
  page: number
  page_size: number
}

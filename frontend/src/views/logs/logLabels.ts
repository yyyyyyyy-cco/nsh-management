/** 系统日志页标签与格式化工具（自 LogView.vue 拆出）。 */
import dayjs from 'dayjs'

export const moduleLabels: Record<string, string> = {
  members: '常驻库',
  schedules: '联赛日程',
  attendance: '出勤库',
  lineups: '排表',
  recordings: '录屏审核',
  'match-data': '数据分析',
  'squad-adjustments': '小队调整',
  config: '系统配置',
  developer: '开发者',
  auth: '认证',
  'my-stats': '个人战绩',
  other: '其他',
}

export const actionLabels: Record<string, string> = {
  create: '创建',
  update: '更新',
  delete: '删除',
  login: '登录',
  login_failed: '登录失败',
  import: '导入',
  other: '其他',
}

export function formatTime(value: string): string {
  return dayjs(value).format('YYYY-MM-DD HH:mm:ss')
}

export function levelLabel(level: string): string {
  return level === 'error' ? '错误' : level === 'warning' ? '警告' : '信息'
}

export function levelTagType(level: string): 'danger' | 'warning' | 'info' {
  return level === 'error' ? 'danger' : level === 'warning' ? 'warning' : 'info'
}

export function roleLabel(role: string): string {
  return role === 'developer' ? '开发者' : role === 'admin' ? '管理员' : '帮众'
}

export function roleTagType(role: string): '' | 'danger' | 'info' {
  return role === 'developer' ? '' : role === 'admin' ? 'danger' : 'info'
}

export function actionTagType(action: string): '' | 'success' | 'warning' | 'danger' | 'info' {
  if (action === 'delete' || action === 'login_failed') return 'danger'
  if (action === 'create') return 'success'
  if (action === 'update') return 'warning'
  if (action === 'login') return ''
  return 'info'
}

export function statusClass(code: number | null): string {
  if (code == null) return ''
  if (code >= 500) return 'status-error'
  if (code >= 400) return 'status-warning'
  return 'status-ok'
}

export function formatDetail(detail: string): string {
  try {
    return JSON.stringify(JSON.parse(detail), null, 2)
  } catch {
    return detail
  }
}

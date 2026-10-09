/** 使用指南内容：与渲染分离，改文案不动组件（先例：match-data/analysis.ts）。 */
export type Role = 'developer' | 'admin' | 'member'

/** 章节渲染类型：步骤清单 / FAQ 折叠 / 角色差异表 / 页面详解 */
export type GuideKind = 'steps' | 'faq' | 'roles' | 'pages'

export interface GuideItem {
  title: string
  body?: string
  steps?: string[]
  roles?: Role[] // 未声明 = 所有角色可见
}

export interface GuideSection {
  key: string
  label: string
  kind: GuideKind
  intro?: string
  items: GuideItem[]
}

/** 页面详解条目：逐页操作引导（仅独立路由页面给 path，用于「打开该页面」） */
export interface PageGuide {
  key: string
  name: string
  entry: string
  path?: string
  roles: Role[]
  intro: string
  steps: string[]
  points: string[]
  tips?: string[]
}

export interface GuidePageGroup {
  key: string
  label: string
  pages: PageGuide[]
}

export interface RoleMatrixRow {
  area: string
  developer: string
  admin: string
  member: string
}

export const ROLE_LABELS: Record<Role, string> = {
  developer: '开发者',
  admin: '管理员',
  member: '帮众',
}

export const GUIDE_SECTIONS: GuideSection[] = [
  {
    key: 'quick-start',
    label: '快速上手',
    kind: 'steps',
    intro: '按角色选择你的上手路径：',
    items: [
      {
        title: '管理员：从建赛程到看战报',
        roles: ['admin'],
        steps: [
          '系统配置：确认职业配置与帮众账号',
          '联赛日程：创建赛程（对手 / 时间 / 局数）',
          '出勤库：一键导入正式成员，登记请假与补人',
          '排表：把候选人拖入 10 队 × 6 槽位并保存',
          '录屏审核：逐条或批量审核帮众提交的录屏链接',
          '数据分析：导入比赛 CSV，浏览各分析 Tab，可生成战报海报',
        ],
      },
      {
        title: '帮众：录屏与战绩',
        roles: ['member'],
        steps: [
          '首页：查看近 10 局战绩、数据亮点与录屏待办',
          '联赛总览：为每局提交录屏链接',
          '个人战绩：按游戏 ID 查询历史数据',
          '修改游戏 ID：提交改名申请（管理员审核）',
        ],
      },
      {
        title: '开发者：初始化与审计',
        roles: ['developer'],
        steps: ['系统配置：创建帮会、派发账号', '系统日志：查看操作审计与错误统计'],
      },
    ],
  },
  {
    key: 'pages',
    label: '页面详解',
    kind: 'pages',
    intro: '按页面查看详细操作引导（点击展开）：',
    items: [],
  },
  {
    key: 'faq',
    label: '常见问题',
    kind: 'faq',
    items: [
      {
        title: '帮众忘记密码 / 为什么不能自己修改密码？',
        body: '帮众账号为帮会共享账号，为防止改密后其他使用者无法登录，帮众不支持自助改密；忘记密码请管理员在「系统配置 → 账号管理」中重置。',
      },
      {
        title: '改了游戏 ID，旧 ID 的战绩会丢吗？',
        body: '不会。改名申请审核通过后，系统自动建立新旧 ID 关联，个人战绩自动合并展示；存在关联冲突时可切换「仅查此 ID」精确查询。',
      },
      {
        title: '出勤率是怎么计算的？',
        body: '出勤率 = 正常次数 ÷（正常次数 + 请假次数）。排序时出勤率相同按正常次数排列，无出勤记录恒排最后。',
      },
      {
        title: 'CSV 重复导入会叠加吗？',
        body: '不会。同一赛程同一局为「覆盖」语义：重新导入会先清除该局已有数据，再写入新数据。',
      },
      {
        title: '录屏链接提交后还能修改吗？',
        body: '可以。重新提交会将该条录屏恢复为「待审核」状态，需要管理员重新审核。',
      },
      {
        title: '为什么有些菜单我看不到？',
        body: '菜单按角色显示：开发者仅见系统配置与系统日志，管理员可见全部管理功能，帮众仅见录屏与个人相关功能。详见「角色差异」标签页。',
      },
      {
        title: '首页「历史比赛」是怎么统计的？',
        body: '统计全部已结束（比赛时间已过）的场次，与帮众首页「已赛场次」同口径。',
      },
      {
        title: '数据分析里的指标公式在哪查看？',
        body: '在数据分析页点击「指标说明」，内含原始字段、16 项衍生指标、阵营对比与综合评分的完整口径。',
      },
    ],
  },
  {
    key: 'roles',
    label: '角色差异',
    kind: 'roles',
    intro: '以下为各角色功能范围摘要，菜单以登录后实际显示为准。',
    items: [],
  },
]

export const ROLE_MATRIX: RoleMatrixRow[] = [
  { area: '常驻库 / 出勤库', developer: '—', admin: '管理', member: '—' },
  { area: '联赛排表', developer: '—', admin: '管理', member: '—' },
  { area: '录屏审核', developer: '—', admin: '审核', member: '提交' },
  { area: '数据分析 / 分析调整', developer: '—', admin: '管理', member: '只读（赛程详情内）' },
  { area: '联赛日程', developer: '—', admin: '管理', member: '查看' },
  { area: '个人战绩', developer: '—', admin: '查询全部', member: '查询' },
  { area: '游戏 ID 改名', developer: '—', admin: '审核（常驻库）', member: '提交申请' },
  { area: '系统配置', developer: '帮会与账号管理', admin: '账号与职业配置', member: '—' },
  { area: '系统日志', developer: '查看', admin: '—', member: '—' },
]

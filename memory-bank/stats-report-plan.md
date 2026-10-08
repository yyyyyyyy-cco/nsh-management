# 成员战绩与战报 实施方案

> **状态**：已实施完成（2026-09-17，后端 compileall + 前端 vue-tsc/vite build 通过），待浏览器验收
> **确认决策**：① 成员战绩采用独立成员详情页 ② 管理员开放「个人战绩」菜单 ③ 战报先做单场（汇总报告列入二期）
> **关联权威源**：`design-document-v2.md`（功能定义，v2.5 已同步）、`ui-style-guide.md`（视觉规范）、`.agent/rules/file-length-rule.md`（行数限制）

---

## 1. 背景与目标

### 1.1 背景

- **成员战绩**：现有「个人战绩」（`/my-stats`）仅帮众菜单可见；后端 `GET /my-stats` 本就未限角色（`get_current_user`），管理员缺 UI 入口，无法从成员维度查看历史战绩。
- **战报输出**：数据分析模块（8 Tab、16 项衍生指标、6 榜、阵营对比、小队分析）数据完备，但缺少可直接分享到群聊的「汇报产物」（HTML 报告导出已于 2026-08 移除，未重建）。

### 1.2 目标

| 功能 | 目标 |
|------|------|
| 成员详情战绩页 | 管理员从常驻库点击成员 → 查看该成员基本信息（职业/状态/备注/出勤率）+ 历史战绩（复用个人战绩全部组件）；同时开放管理员「个人战绩」菜单入口（自由按 ID 搜索） |
| 单场图文战报 | 数据分析页一键生成单场「图文战报」PNG（仅统计我方阵营：对局信息 + 我方总览 + MVP 与数据之王 + 六榜 TOP3 + 逐局战况 + 小队战况），用于群内分享 |

### 1.3 决策记录（2026-09-17，用户确认）

| 决策点 | 选择 | 说明 |
|--------|------|------|
| 战绩查看形态 | 独立成员详情页（`/members/:id`） | 空间充裕、移动端体验好、可深链分享，未来可扩展出勤/录屏等档案信息 |
| 管理员菜单 | 开放「个人战绩」入口 | 与常驻库入口互补；后端接口本就未限角色，仅需侧边栏条件调整 |
| 战报范围 | 先做单场战报 | 汇总报告（周/月/全周期）列入二期（§6），需新增多场聚合接口 |

---

## 2. 功能一：成员详情战绩页

### 2.1 需求说明

- **用户场景**：管理员在常驻库查看某成员后，想了解其近期比赛表现（概览/趋势/单局明细/排名），用于考核、排表参考、沟通反馈。
- **数据基础**：成员表 `name` 即游戏 ID（全站「ID」文案已统一），战绩按 `member.name` 精确匹配 `match_data.player_name` 查询；战绩范围与该成员「个人战绩」一致（最近 10 场）。
  - 后续更新（2026-09-20）：成员详情战绩已支持按经审核确认的新旧 ID 合并查询，冲突时提示并跳转个人战绩精确查询，详见 `design-game-id-change.md`；本条其余历史描述保留。

### 2.2 交互设计

```
常驻库列表 ──点击成员 ID（桌面端）/ 成员名后「›」（移动端）──▶ 成员详情页 /members/:id
侧边栏「个人战绩」菜单（管理员新增）──▶ /my-stats 自由搜索任意 ID（现有页面，零改动）
```

**详情页结构**（自上而下）：

1. **顶部**：返回按钮（回常驻库）+ 成员信息卡
   - ID（大字号）、主/副职业色标签、状态标签（正式/替补）、备注
   - 出勤率（百分比；<50% 红色预警，与出勤率面板口径一致；无记录显示「-」）
2. **战绩区**（复用 my-stats 组件，按顺序）：
   - `StatsOverview`（参战场次/主力职业/场均 KDA/击杀/伤害/治疗）
   - `StatsTrendChart`（10 项指标趋势）
   - `StatsRankingPosition`（每局各维度排名）
   - `StatsMatchTable`（单局明细 + 全场/阵营排名）
3. **空态**：该成员无比赛数据 → `el-empty`「该成员暂无比赛数据」；加载中走现有骨架屏（`useSkeletonLoading`）。

### 2.3 技术方案

**后端**（1 个薄路由，复用现有服务）：

- 新增 `GET /api/v1/members/{member_id}` → `MemberOut`
  - 实现：`member_service.get_member()`（已存在，update/delete 在用）+ `MemberOut.model_validate`
  - 权限：`require_admin`（常驻库管理员专属）
  - ⚠ **路由注册顺序**：必须注册在 `/members/export`、`/export-image`、`/profession-stats`、`/attendance-rate` **之后**（FastAPI 按注册顺序匹配，否则 `/members/export` 会被 `{member_id}` 捕获报 422）
- 战绩数据：复用 `GET /my-stats?player_name=`（admin 可调用，零改动）
- 出勤率：复用 `GET /members/attendance-rate`（返回全成员列表，前端按 `member_id` 过滤；`AttendanceRateItem` 已含 `member_id`）

**前端**：

- 路由：`members/:id`（`name: 'member-detail'`、`meta: { title: '成员详情', adminOnly: true }`）
- 新页面：`views/members/MemberDetailView.vue`（≤200 行）
  - `Promise.all([getMember(id), getMyStats(member.name), getAttendanceRate()])` 并行加载
  - 成员信息卡拆为 `components/members/MemberDetailHeader.vue`（≤150 行）
  - 返回按钮：`router.push('/members')`（固定回列表，深链进入也正确）
  - 成员不存在（404）：提示「成员不存在或已删除」并返回常驻库
- 入口改造：
  - `MemberTablePanel.vue`：桌面端 ID 列改为可点击（金线 hover、`title="查看成员详情"`）；移动端行列表成员名后加 `›` 提示 + 点击进入；统一 `emit('detail', row)`，由 `MemberListView.vue` 路由跳转
  - `AppSidebar.vue`：「个人战绩」菜单 `v-if` 增加 admin 角色；菜单插入位置建议「联赛日程」与「系统配置」之间
- API/类型：`api/members.ts` 加 `getMember(id): Promise<MemberInfo>`；无需新类型

### 2.4 权限与边界

| 角色 | /members/:id | /my-stats | 常驻库入口 |
|------|-------------|-----------|-----------|
| developer | ❌（现有守卫跳 config） | ❌（现有拦截） | ❌ |
| admin | ✅ | ✅（新增菜单） | ✅ |
| member | ❌（守卫跳 league-overview） | ✅（不变） | ❌ |

- 成员被删除后刷新详情页：404 → 提示并返回常驻库
- `MyStatsView` 文案**零改动**（「个人战绩」对管理员查询语义一致；自动补全候选来自比赛数据，与常驻库无耦合）

### 2.5 文件清单

| 类型 | 文件 | 说明 |
|------|------|------|
| 修改 | `backend/app/api/v1/members.py` | +1 端点 `GET /{member_id}`，注册于文件末尾 |
| 新增 | `frontend/src/views/members/MemberDetailView.vue` | 详情页（加载 + 布局 + 空态） |
| 新增 | `frontend/src/components/members/MemberDetailHeader.vue` | 成员信息卡（职业/状态/备注/出勤率） |
| 修改 | `frontend/src/router/index.ts` | +1 路由 |
| 修改 | `frontend/src/api/members.ts` | +`getMember` |
| 修改 | `frontend/src/components/members/MemberTablePanel.vue` | ID/名字点击入口 |
| 修改 | `frontend/src/views/members/MemberListView.vue` | detail 事件 → 路由跳转 |
| 修改 | `frontend/src/layouts/AppSidebar.vue` | 菜单条件 + 位置 |

---

## 3. 功能二：单场图文战报

### 3.1 需求说明

- **用户场景**：联赛结束、比赛数据导入后，管理员一键生成「图文战报」图片，发到帮会群，用于汇报战绩与亮点。
- **定位**：整场（全部已导入的局）汇总，**仅统计我方阵营**（排表成员命中数最多的阵营，与后端小队分析口径一致）；产物为 PNG 图片（群内分享友好）。
- **不依赖后端改动**：全部数据来自现有分析接口。

### 3.2 交互设计

```
数据分析页（MatchDataTab 工具栏）──点击「生成战报」（仅管理员）──▶ 战报预览弹窗
    ├── 海报预览（960px 设计宽，长图）
    └── 底部：「导出 PNG」按钮（html2canvas，动态 import）+ 「关闭」
```

**海报结构**（固定 960px 宽，垂直长图；全部区块仅统计我方阵营）：

1. **头部**：帮会名 + 「联赛战报」标题 + 生成日期；对手/时间/总结果徽章/各局结果；规模行（我方参战人数/人次/已导入局数）
2. **我方总览**：击杀 / 助攻 / 对玩家伤害 / 对建筑伤害 / 治疗 / 焚骨 六数字卡
3. **MVP 与数据之王**：MVP 金卡（我方最高单局评分：评分/KDA/击杀/伤害，标注所属局）+ 数据之王六格（击杀/伤害/建筑/治疗/承伤/焚骨，各取我方最佳单局）
4. **高光榜单**：击杀 / 对玩家伤害 / 治疗 / 对建筑伤害 / 重伤 / 总分 六榜 TOP3（我方按玩家去重保留最佳单局；重伤榜按重伤次数倒序；总分榜取各局综合评分最佳单局，口径与 MVP 一致）
5. **逐局战况**：每局一块（局号 + 结果徽章 + 我方击杀/伤害/治疗 + 该局 MVP/击杀王/重伤第一＝该局我方重伤次数最多者；未导入局显式占位）
6. **小队战况**：按排表 + 分析调整副本归属聚合我方各队（进攻 1/2、防守 1/2）击杀/助攻/重伤/对玩家伤害/对建筑伤害/治疗/承伤/焚骨八项；排表队伍完整呈现（空队显示 0），未排表成员单列；无排表时区块自动隐藏。小队分析内手动分配未排表成员（分析调整副本）后，战报同步该归属（目标队伍已不存在于排表时忽略，与小队分析视图口径一致）
7. **页脚**：水印「轻衫都会用的帮会联赛管理系统 · 生成于 YYYY-MM-DD」

### 3.3 技术方案

**数据加载**（打开弹窗时三请求并发）：

| 数据 | 接口 | 用途 |
|------|------|------|
| 全场衍生指标记录 | `getIndicators(scheduleId)`（不传 round_no = 全部已导入局） | 数据源：每人每局基础字段 + 16 项衍生指标 |
| 排表 | `getLineup(scheduleId)`（失败降级为 null） | 判定我方阵营 + 小队战况聚合 |
| 分析调整副本 | `getSquadAdjustments(scheduleId)`（失败降级为 null） | 小队战况归属（覆盖排表：小队分析内未排表成员的手动分配） |
| 赛程信息 | 由父级传入 `schedule` 对象 | 对手/时间/总结果/各局结果 |

> **我方阵营判定**（与后端 `squad-analysis` 口径一致）：排表成员名命中数最多的阵营；无命中时兜底取首条记录阵营。过滤后所有统计（总览/MVP/榜单/逐局/小队）仅含我方记录；MVP/榜单/小队聚合由 `reportData.ts` 前端组装（复用 `computeScores`）。

> 赛程对象获取：`ScheduleDetailView` 已加载 `schedule` 后才挂载 `MatchDataTab`，只需扩展 props（`MatchDataTab` 仅在此处使用，已核实）。`schedule.round_results` 为各局结果数组。

**组件拆分**（行数规则）：

| 组件 | 职责 | 行数 |
|------|------|------|
| `match-data/MatchReportDialog.vue` | 弹窗壳：指标+排表+分析调整副本加载（判我方/小队归属）+ 导出逻辑 + 局部状态 | ~170 |
| `match-data/reportData.ts` | 接口响应 → 战报渲染数据（我方判定/过滤、MVP/数据之王/逐局/榜单去重/小队聚合） | ~250 |
| `match-data/report/MatchReportPoster.vue` | 海报根容器（960px 固定宽）+ 7 区块组合 | ~60 |
| `match-data/report/PosterHeader.vue` | 头部 + 对局信息 + 各局结果 + 规模行 | ~160 |
| `match-data/report/PosterOverview.vue` | 我方总览六数字卡 | ~75 |
| `match-data/report/PosterMvpKings.vue` | MVP 金卡 + 数据之王六格 | ~180 |
| `match-data/report/PosterRankings.vue` | 六榜 TOP3（去重玩家；总分取综合评分最佳单局） | ~155 |
| `match-data/report/PosterRounds.vue` | 逐局战况（我方） | ~130 |
| `match-data/report/PosterSquads.vue` | 小队战况（按排表 + 分析调整副本归属聚合各队） | ~105 |

**导出实现**（沿用排表总览先例 `LineupOverviewPanel`）：

```ts
const { default: html2canvas } = await import('html2canvas') // 动态加载，不进首屏 chunk
const canvas = await html2canvas(posterRef.value, {
  backgroundColor: '#FAF7F0', // 宣纸底色
  scale: 2,
  useCORS: true,
  windowWidth: 1000, // 固定视口，产物不受当前窗口影响
})
// 下载：战报_{对手}_{YYYY-MM-DD}.png
```

**CSS 约束**（html2canvas 兼容）：不用 `backdrop-filter`/`filter`/复杂 `mask`；颜色走 `theme.css` 令牌；职业色用 `utils/profession.ts` 的 `PROF_COLORS`；海报内部不响应式（固定 960px），弹窗内容区按需横向滚动，桌面优先；预览缩放不得改变海报 DOM 自身尺寸（导出截取内层原尺寸元素）。

### 3.4 边界与异常

- 该场无任何已导入数据：「生成战报」按钮禁用（`tooltip`：请先导入比赛数据）
- 仅导入部分局：允许生成，头部标注「已导入 X/Y 局」
- 阵营数 > 2（异常数据）：取前 2 个阵营，不报错
- 接口失败：提示错误，不打开弹窗（或弹窗内错误态）
- 帮众不可见「生成战报」按钮（`v-if="auth.isAdmin"`）

### 3.5 文件清单

| 类型 | 文件 | 说明 |
|------|------|------|
| 新增 | `components/match-data/MatchReportDialog.vue` | 预览弹窗 + 导出 |
| 新增 | `components/match-data/reportData.ts` | 数据组装 |
| 新增 | `components/match-data/report/`（MatchReportPoster + 4 子组件） | 海报 |
| 修改 | `components/match-data/MatchDataTab.vue` | 工具栏按钮 + props 扩展（`schedule`） |
| 修改 | `views/schedules/ScheduleDetailView.vue` | 传入 `:schedule` |

> 后端零改动；无数据库迁移。

---

## 4. 影响面汇总

- **数据库**：无迁移
- **后端**：+1 端点（`GET /members/{member_id}`）
- **前端**：+2 组新组件（成员详情页/战报弹窗与海报）、修改点 5 处（路由/侧边栏/成员表/常驻库视图/分析页与赛程详情传参）
- **文档联动**：`design-document-v2.md`（v2.5 已同步功能定义）、backend/frontend docs（已登记待开始项）；实施完成后更新 `progress.md`（目录树 + 模块表 + 更新记录）与 frontend docs 状态

## 5. 验证方案

1. **后端**：`backend\.venv\Scripts\python.exe -m compileall app`；导入冒烟 `python -c "from app.main import app"`；重点回归 `GET /members/export` 与 `/profession-stats` 仍优先于 `/{member_id}` 匹配（curl/TestClient 各请求一次）
2. **前端**：`cd frontend && npm run build`（vue-tsc 类型检查 + vite 生产构建）
3. **浏览器验证**（由用户执行）：
   - 管理员：常驻库 → 点击成员 → 详情页（信息/出勤率/战绩齐全）；「个人战绩」菜单可用
   - 帮众登录回归：菜单与路由无变化；`/my-stats` 正常
   - 管理员：数据分析 → 生成战报 → 预览 → 导出 PNG（检查排版完整、无溢出、字体正常）
   - 移动端断点（≤768px）：详情页布局、战报弹窗抽查
4. **项目约定**：不执行 git 提交；浏览器操作仅在用户明确指示时执行

## 6. 二期规划（暂定，不在本轮范围）

- 汇总报告（周/月/全周期：出勤 + 战绩 + 录屏聚合，需新增多场聚合接口与新视图）
- 战报增强：综合评分 TOP、指标自选、海报模板
- 成员详情档案化：出勤历史明细、录屏提交记录、排表历史
- `MyStatsView` 搜索结果匹配到常驻库成员时，提供「查看成员详情」跳转

## 7. 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-09-17 | 初稿：方案确认（三项决策），功能设计/文件清单/验证方案定稿 |
| 2026-09-17 | 实施完成：后端 GET /members/{member_id}；前端成员详情页（MemberDetailView/MemberDetailHeader/路由/入口/管理员菜单）与单场图文战报（MatchReportDialog/reportData.ts/report 海报 5 组件/MatchDataTab 入口 + schedule 透传）；profTagStyle 抽取至 utils/profession；vue-tsc + vite build 通过 |
| 2026-09-17 | v2 重设计（用户反馈原版太简陋、无信息含量）：海报扩展为 8 区块（新增全场总览/MVP 与数据之王/逐局战况，阵营对比扩至 6 指标+差值、榜单去重玩家、职业加伤害占比）；数据层改为单接口（getIndicators）前端组装；vue-tsc + vite build 通过 |
| 2026-09-17 | 口径调整（用户要求：不要两个阵营、只要我方）：仅统计我方阵营（排表命中判定，与后端小队分析一致）——删除阵营对比区块、总览扩为六卡、逐局改我方击杀/伤害/治疗；数据加载增加排表（判我方，失败降级）；vue-tsc + vite build 通过 |
| 2026-09-18 | 区块替换（用户要求：职业分布没必要）：移除职业分布，新增「小队战况」——按排表归属聚合我方各队（进攻 1/2、防守 1/2 + 未排表）击杀/对玩家伤害/治疗；未排表成员单列、无排表时区块自动隐藏（零额外请求，复用已加载排表）；vue-tsc + vite build 通过 |
| 2026-09-20 | 小队归属修复（用户反馈：小队分析内分配未排表成员后，战报小队仍显示未分配）：根因为战报仅按正式排表聚合，未读取分析调整副本；MatchReportDialog 增加 `getSquadAdjustments` 并发加载（失败降级为 null 不阻断），`buildReportData` 增加 adjustments 参数并叠加覆盖小队归属（目标队伍不存在于排表时忽略，与小队分析视图口径一致）；reportData.ts 登记行数豁免；vue-tsc + vite build 通过 |
| 2026-09-20 | 逐局战况新增「重伤第一」（用户要求：每局的重伤第一也挂出来）：`ReportRoundInfo` 增加 `deathKing`（取该局我方重伤次数最多者，并列取首个最大值，与击杀王同口径），PosterRounds 副行显示「重伤第一 名字 N 次」并允许换行防长名溢出；vue-tsc + vite build 通过 |
| 2026-09-20 | 小队战况新增「重伤」列（用户要求：小队战况里面把重伤也加上）：`ReportSquadItem` 增加 `deaths` 并纳入聚合（含空队显示 0），PosterSquads 表格列由七项扩为八项（重伤插在助攻后，与小队分析表列序一致）并同步网格列宽；vue-tsc + vite build 通过 |
| 2026-09-20 | 高光榜单扩为六榜（用户要求：还要有建筑伤害榜、重伤榜、总分榜）：`MatchReportData` 增加 `buildingTop`/`deathsTop`/`scoreTop`，`buildReportData` 复用逐局 `computeScores` 结果按玩家保留最佳单局综合评分（与 MVP 口径一致）；PosterRankings 三列两行展示六榜 TOP3；vue-tsc + vite build 通过 |

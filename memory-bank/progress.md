# 项目进度与代码结构

## 代码目录结构

```
nsh-management/
├── backend/                   # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/               # API 路由（v1/ 路由注册 + deps 依赖注入）
│   │   ├── core/              # 配置、数据库、安全（JWT/密码）、客户端 IP 解析（client_ip）
│   │   ├── models/            # 11 张表 SQLAlchemy 模型（含 squad_adjustments/operation_logs）
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── services/          # 业务逻辑（account/auth/config/guild/lineup/lineup_attendance/log/match_data/match_data_aggregate/match_data_csv/match_data_stats/member/my_stats/recording/attendance/schedule/squad_adjustment）
│   │   ├── utils/             # 工具函数（attendance_import/excel_import/excel_export/image_export/constants/member_names）
│   │   ├── init_db.py         # 初始化默认帮会与账号（开发者/admin/member）
│   │   └── main.py            # 应用入口（CORS/异常处理/AuthError锁定秒数）
│   ├── alembic/               # 数据库迁移（13 个版本）
│   ├── data/                  # SQLite 数据库（nsh.db）
│   ├── docs/README.md         # 后端模块开发文档
│   ├── scripts/               # 工具脚本
│   │   ├── audit_weights_v4_20260907.py   # 贡献度权重审计（v4）
│   │   ├── derive_weights_v4_20260907.py  # 贡献度权重推导（v4）
│   │   ├── generate_import_template.py    # 生成成员导入模板
│   │   ├── selfcheck_indicators.py        # 衍生指标自检脚本
│   │   └── sim_contribution_v4_20260907.py # 贡献度模拟（v4）
│   ├── templates/             # Excel 模板
│   │   └── member_import_template.xlsx  # 成员导入模板
│   ├── Dockerfile             # 后端容器镜像（多阶段构建）
│   ├── .dockerignore
│   ├── entrypoint.sh          # 容器启动脚本
│   ├── requirements.txt
│   └── .venv/                 # 虚拟环境（Python 3.13）
├── frontend/                  # 前端项目（Vue3+TS+Vite）
│   ├── src/
│   │   ├── api/               # Axios 封装（http/auth/config/lineups/members/attendance/matchData/recording/schedules/squadAdjustments）
│   │   ├── components/        # 业务组件
│   │   │   ├── attendance/    # 出勤库（AttendanceTab+AttendanceStatsBar/AttendanceToolbar/AttendanceTablePanel/AttendanceMobileList/FillerDialog/ImportMemberDialog/LeaveImportDialog/SubstituteImportDialog）
│   │   │   ├── common/        # 通用组件（SkeletonTable）
│   │   │   ├── lineups/       # 排表（LineupEditor/LineupTab+LineupOverviewPanel/LineupOverviewGroup/ImportHistoryDialog/MatchConfirmDialog）
│   │   │   ├── match-data/    # 数据分析（MatchDataTab/OverviewTab/IndicatorsTab/RankingTab+rankingCharts/CampCompareTab/SquadAnalysisTab+SquadOverviewPanel/SquadCardsGrid/SquadDetailDialog/SquadMembersTabs/SquadCompareDialog/SquadAssignDialog/squadCharts/squadCompareCharts/ProfessionTab/ProfessionDetailTab+ProfessionMetricTables/ProfessionCompareTable/professionDetailCharts/ScoreTab/PlayerAnalysis+playerScatterCharts/playerAggregateCharts/playerRadar/CampCompare/MetricsGuideDialog/EChart/analysis.ts/chartTheme.ts）
│   │   │   ├── members/       # 常驻库（AttendanceRatePanel/MemberStatsBar/MemberToolbar/MemberTablePanel/MemberFormDialog/MemberImportDialog/ProfessionShortage）
│   │   │   ├── my-stats/      # 个人战绩（PlayerSearch/StatsOverview/StatsMatchTable/StatsRankingPosition/StatsTrendChart）
│   │   │   ├── recording/     # 录屏审核（RecordingTab+RecordingProgressBar/RecordingTablePanel/RecordingMobileList/recording-shared.css）
│   │   │   └── schedules/     # 联赛日程（ScheduleCalendar）
│   │   ├── composables/       # 组合式函数（lineupBoard/useAttendanceList/useRecordingList/useMemberList/useRouteProgress）
│   │   ├── layouts/           # 主布局（MainLayout + AppSidebar/AppHeader；深檀侧边栏208px+宣纸顶栏62px，支持折叠64px）
│   │   ├── router/            # 路由与守卫
│   │   ├── stores/            # Pinia（auth）
│   │   ├── styles/            # 浅色雅金风主题（theme.css 令牌 / element-plus.css 组件 / index.css 入口）
│   │   ├── types/             # TS 类型定义（attendance/auth/config/lineup/matchData/member/recording/schedule）
│   │   ├── utils/             # 工具函数（constants/scheduleSort）
│   │   └── views/             # 页面
│   │       ├── HomeView.vue           # 首页仪表盘（壳）+ home/ 卡片组件（HomeWelcome/HomeTodayBanner/HomeStatCards/HomeRecentSchedules/HomeProfessionOverview/HomeAttendanceRanking/HomeQuickActions + home-shared.css）
│   │       ├── LoginView.vue          # 登录页（含锁定倒计时）
│   │       ├── config/ConfigView.vue  # 系统配置壳（+ ConfigProfessionPanel/ConfigGuildPanel/ConfigAccountPanel/ConfigAccountGroup）
│   │       ├── logs/LogView.vue       # 系统日志壳（+ LogStatsCards/LogFilterBar/LogMobileList/LogTablePanel/LogDetailDialog/LogClearDialog/logLabels.ts）
│   │       ├── member/MyStatsView.vue # 个人战绩（帮众）
│   │       ├── members/MemberListView.vue  # 常驻库
│   │       └── schedules/             # 联赛日程
│   │           ├── ScheduleListView.vue      # 日程列表
│   │           ├── ScheduleDetailView.vue    # 赛程详情（管理员：出勤/排表/录屏/分析；帮众：录屏/分析）
│   │           └── LeagueOverviewView.vue    # 帮众联赛总览
│   ├── Dockerfile             # 前端容器镜像（多阶段构建）
│   ├── .dockerignore
│   ├── nginx.conf             # Nginx 配置（静态托管+API反代+SPA回退+HTTPS）
│   ├── docs/README.md         # 前端模块开发文档
│   └── package.json
├── memory-bank/                # 项目文档
│   ├── ai-context.md           # AI 项目完整上下文文档
│   ├── ai-checklist.md         # AI 操作检查清单（错误记录与联动规则）
│   ├── architecture.md         # 文档索引
│   ├── data-analysis-complete.md # 数据分析模块完整方案
│   ├── database-design.md      # 数据库设计文档（v1.8）
│   ├── design-document-v2.md   # 产品设计文档（当前主文档）
│   ├── implementation-plan.md  # 实施方案文档
│   ├── progress.md             # 本文档 - 代码结构与进度
│   ├── security-review.md      # 安全审查文档
│   ├── tech-stack.md           # 技术栈文档
│   ├── ui-polish-plan.md       # UI优化方案文档
│   └── ui-style-guide.md       # UI风格参考文档
├── .agent/                     # AI 规则与内部样例（rules 已入库）
│   ├── docs/                   # 内部样例（比赛 CSV 入库；Excel 分析表仅本地）
│   └── rules/                  # AI 编码规则（已入库）
│       ├── code_rule.md        # 项目规则
│       ├── file-length-rule.md # 文件行数限制
│       ├── function_rule.md    # 模块开发文档规则
│       └── git-commit-message.md # Git 提交信息规范
├── AGENTS.md                   # AI 开发指南：规范/文档维护/进度追踪（自动读取）
├── start.bat                   # 一键启动脚本（前后端+首次建库）
├── deploy.sh                   # Linux 部署脚本（Docker Compose 一键部署）
├── docker-compose.yml          # Docker Compose 编排（Nginx + FastAPI + SQLite 卷）
├── .env.example                # 部署环境变量模板（复制为 .env 填写）
├── DEPLOY.md                   # 部署文档（Docker Compose 全流程）
├── GIT-GUIDE.md                # Git 管理规范（分支/提交/发布/双远程）
├── .gitignore                  # Git忽略规则
└── README.md                   # 项目说明
```

---

## 代码模块说明

### 前端模块

| 模块 | 路径 | 作用 | 状态 |
|------|------|------|------|
| 基础框架 | frontend/ | Vue3+TS+Vite+Element Plus 骨架、浅金色主题 | ✅ 已完成 |
| 认证链路 | src/{api,stores,router} | Axios 封装、Pinia、路由守卫 | ✅ 已完成 |
| 布局与登录 | src/{layouts,views} | 主布局（可折叠侧边栏）、登录页（锁定倒计时）、首页仪表盘 | ✅ 已完成 |
| 常驻库页面 | src/views/members | 列表/筛选/弹窗/Excel导入/出勤率 | ✅ 已完成 |
| 联赛日程页面 | src/views/schedules | 日历/创建弹窗/详情Tab/联赛总览 | ✅ 已完成 |
| 出勤库页面 | src/components/attendance | 统计/导入成员/导入请假/替补/补人/状态/保存 | ✅ 已完成 |
| 排表页面 | src/components/lineups | 候选池/拖拽编排/总览/导出PNG/导入历史排表 | ✅ 已完成 |
| 录屏审核页面 | src/components/recording | 列表/提交/审核/进度/按姓名搜索/链接脱敏 | ✅ 已完成 |
| 数据分析页面 | src/components/match-data | CSV导入/8Tab可视化（总览/列表/排行榜/阵营对比/小队分析/职业分析/职业深度/综合评分）/16项衍生指标/指标说明/ECharts图表 | ✅ 已完成 |
| 系统配置页面 | src/views/config | 职业配置/账号管理/帮会管理（开发者） | ✅ 已完成 |
| 个人战绩页面 | src/views/member + src/components/my-stats | 玩家搜索/单局明细/概览（按游戏 ID 聚合） | ✅ 已完成 |
| 系统日志页面 | src/views/logs | 审计日志筛选/分页/清理（开发者） | ✅ 已完成 |
| 样式系统 | src/styles/ | 浅色雅金风主题（theme.css + element-plus.css + index.css） | ✅ 已完成 |

### 后端模块

| 模块 | 路径 | 作用 | 状态 |
|------|------|------|------|
| 基础框架 | app/core | 配置（JWT 10h）、异步数据库、JWT/密码 | ✅ 已完成 |
| 数据模型 | app/models | 11 张表 SQLAlchemy 模型 + 14 个 Alembic 迁移 | ✅ 已完成 |
| 认证模块 | app/api/v1/auth.py | 登录/登出/me + 登录限流（含未知账号锁定） | ✅ 已完成 |
| 常驻库 API | app/api/v1/members.py | CRUD/筛选/批量删/Excel导入/出勤率/职业统计 | ✅ 已完成 |
| 联赛日程 API | app/api/v1/schedules.py | CRUD/时间范围/级联创建删除 | ✅ 已完成 |
| 出勤库 API | app/api/v1/attendance.py | 导入成员/替补/补人/请假导入/状态/保存/职业切换 | ✅ 已完成 |
| 排表 API | app/api/v1/lineups.py | 候选池/读写/保存校验/规范化/导入历史/备注 | ✅ 已完成 |
| 录屏审核 API | app/api/v1/recording.py | 提交/审核/批量审核/进度 | ✅ 已完成 |
| 数据分析 API | app/api/v1/match_data.py | CSV导入/6榜排行/职业17项统计/16项衍生指标/阵营对比/小队分析 | ✅ 已完成 |
| 分析调整 API | app/api/v1/squad_adjustments.py | 小队分析内未排表成员→目标队伍的临时分配（仅作用于分析视图，不改正式排表） | ✅ 已完成 |
| 开发者 API | app/api/v1/developer.py | 开发者专属路由（帮会管理/账号管理等） | ✅ 已完成 |
| 系统配置 API | app/api/v1/config.py + accounts.py + guilds.py | 职业配置/账号管理/帮会管理（开发者）/删除帮会/删除账号（URL 前缀均为 /config） | ✅ 已完成 |
| 个人战绩 API | app/api/v1/my_stats.py | 玩家名搜索/按游戏 ID 聚合历史战绩 | ✅ 已完成 |
| 系统日志 API | app/api/v1/logs.py | 审计日志查询/统计/清理（开发者，审计中间件自动写入） | ✅ 已完成 |
| 部署 | Dockerfile/docker-compose/deploy.sh | Docker Compose 一键部署（Nginx+FastAPI+SQLite） | ✅ 已完成 |

---

## 开发进度

| 阶段 | 内容 | 状态 | 完成日期 |
|------|------|------|---------|
| 1 | 项目初始化、文档编写 | ✅ 已完成 | 2026-08-03 |
| 2 | 前后端项目搭建（基础框架+认证） | ✅ 已完成 | 2026-08-06 |
| 3 | 核心功能开发（常驻库/联赛日程/出勤库） | ✅ 已完成 | 2026-08-11 |
| 4 | 高级功能开发（排表/录屏审核） | ✅ 已完成 | 2026-08-17 |
| 5 | 高级功能开发（数据分析） | ✅ 已完成 | 2026-08-17 |
| 6 | 系统配置开发 | ✅ 已完成 | 2026-08-17 |
| 7 | 功能增强与部署（开发者角色/出勤增强/排表历史/数据分析可视化/Docker部署） | ✅ 已完成 | 2026-08-18 |
| 8 | 测试与优化 | ⏳ 待开始 | - |

---

## 更新记录

| 日期 | 更新内容 | 关联模块 |
|------|---------|---------|
| 2026-08-03 | 初始化进度文档 | - |
| 2026-08-05 | 更新代码目录结构，反映当前实际文档布局 | - |
| 2026-08-06 | 新增前后端模块开发文档，backend/frontend 目录待初始化 | 基础框架 |
| 2026-08-06 | 阶段一完成：前后端骨架、9 表迁移、认证模块、布局与登录页，冒烟测试通过 | 基础框架 |
| 2026-08-07 | 常驻库模块完成（后端 CRUD/Excel导入/出勤率 + 前端列表/弹窗/面板），测试与构建通过 | 常驻库 |
| 2026-08-11 | 联赛日程模块完成（后端级联创建/删除 + 前端日历/弹窗/详情Tab），测试与构建通过 | 联赛日程 |
| 2026-08-11 | 出勤库模块完成（导入/补人/状态/保存 + 前端 Tab），术语“客人”改“补人” | 出勤库 |
| 2026-08-11 | 排表模块完成（候选池/拖拽编排/备注/总览/导出PNG），测试与构建通过 | 排表 |
| 2026-08-17 | 录屏审核模块完成（列表/提交/审核/批量审核/进度统计），测试通过 | 录屏审核 |
| 2026-08-17 | 数据分析模块完成（CSV导入/排行榜/职业统计/HTML报告导出），测试通过 | 数据分析 |
| 2026-08-17 | 系统配置模块完成（职业配置/账号管理/帮会管理），测试通过 | 系统配置 |
| 2026-08-17 | 全局 UI 优化完成：确定「浅色雅金风」风格（宣纸鎏金），重写设计令牌（theme.css）+ Element Plus 深度主题（element-plus.css），逐一优化全部 20 个页面组件（深檀侧边栏/水墨登录页/鎏金卡片/职业色标签/攻防分区排表/金银铜排行徽章），类型检查与生产构建通过 | 全模块 UI |
| 2026-08-17 | 系统更名为「轻衫都会用的帮会联赛管理系统」：登录页删除 Logo/副标题/底部导航并改主标题，浏览器标题（index.html/router）、侧边栏品牌（MainLayout）、后端 APP_NAME 统一更新 | 登录页、全站品牌 |
| 2026-08-17 | 侧边栏优化：删除「令」字 Logo，品牌区动态显示当前账号归属帮会名（后端 /me 增加 guild_name），开发者隐藏首页菜单；系统配置页账号分组卡片支持点击折叠 | 布局、系统配置 |
| 2026-08-17 | 新增帮众专属「联赛总览」页面：全量赛程由新到旧列表，点击直达录屏上传 Tab；后端赛程 list/get 放开帮众查看权限；帮众登录后默认进入联赛总览 | 联赛总览、权限 |
| 2026-08-17 | 帮众视角收敛：隐藏「联赛日程」菜单（仅管理员可见），赛程详情页隐藏出勤库/排表 Tab（仅录屏+数据分析）；排查录屏加载（后端链路并发测试正常，RecordingTab 增加 catch 兜底）；确认库中 admin/member 实际密码为 111111（非文档默认） | 权限、UI |
| 2026-08-17 | 修复「返回后页面卡死」Bug：el-progress color 函数误返回对象导致渲染崩溃、组件树损坏、卸载中断；改为返回渐变字符串，浏览器验证 9/9 通过；返回按钮改为来源感知（from=overview 显式回总览） | 录屏审核、排表返回 |
| 2026-08-17 | 录屏/总览 UI 优化：联赛总览删除地点列、emoji 换 Element Plus 图标；详情页删除地点项、⚔️ 换图标；录屏列表新增职业列（后端 RecordingOut 增加 profession 快照）+ 表头排序 + 默认按职业排序 + 点击局数进度条筛选 | 录屏审核、联赛总览 |
| 2026-08-17 | 录屏进度条优化：删除「驳回」数字；「待审」改为仅统计已填写链接且未审核的人数（未填链接占位不计入） | 录屏审核 |
| 2026-08-17 | 修复 admin 登录后首页弹「请求参数校验失败」：根因是首页职业分布请求 page_size=999 超出后端上限 100；新增后端聚合接口 GET /members/profession-stats（GROUP BY 职业），首页改用该接口，浏览器验证两次登录零报错 | 首页、常驻库 |
| 2026-08-17 | 首页仪表盘修复：emoji 图标全部换成 Element Plus 图标（统计卡/卡片头/快捷操作）；职业色映射修正为 ui-style-guide 标准色（铁衣 #ffc800 等）；修复出勤率显示错误（后端返回小数 0~1，首页误直接显示为 1%，现统一 ×100 转百分数） | 首页 |
| 2026-08-17 | 系统配置优化：账号管理 Tab 仅开发者可见（admin 隐藏）；职业配置「说明」列改为可编辑输入框（默认空），数据库 profession_configs 新增 remark 字段（Alembic 迁移 a1b2c3d4e5f6），保存时随目标人数一并提交 | 系统配置、数据库 |
| 2026-08-17 | 联赛日程与出勤/排表优化：联赛日程页图标换 el-icon、删地点列；日历 UI 全面美化（金色今天按钮/导航箭头/胶囊事件标签/今日高亮/赛程圆点）；保存考勤按钮实心化、出勤开关金色化；修复排表人数统计 Bug（空槽误计为已排，现按 member_name 过滤）与导出 PNG 静默失败（增加 catch 提示与滚动容器完整导出） | 联赛日程、出勤、排表 |
| 2026-08-17 | 参考 E:\code\@Cjy\B 重构排表：候选池按职业分组（职业色标签+人数）并剔除已排成员；槽位卡片增强（职业色点/职业描边标签/清除按钮）；排表总览重写为分组卡片式（进攻/防守四组、每队一列+填充计数 6/6、职业分布胶囊条+合计）；后端排表读取时按出勤库填充槽位职业快照；日历今天数字改浅金色、今天按钮改轮廓风 | 排表、联赛日程 |
| 2026-08-17 | 出勤库增强：新增职业缺口分析条（配置目标 vs 当前出勤，缺N/已满胶囊）；新增「导入请假」功能（纯文本名单按行首关键词匹配成员 → 确认后批量请假）；修复补人不进候选池（el-tabs 切换不重挂载，排表 Tab 激活时自动刷新候选池与总览） | 出勤库、排表 |
| 2026-08-17 | 出勤/排表微调：职业缺口条去掉职业彩色统一雅金风（缺口金色/已满灰）；修复补人拖入槽位后候选池不消失（候选池分组列表是派生数组，vuedraggable 增删不同步源数据，现手动同步）；排表新增自动保存（变更防抖 3 秒保存 + 待保存/保存中/已保存状态指示，保存后自动刷新总览）；导入请假支持「1.姓名 原因」序号格式 | 出勤库、排表 |
| 2026-08-17 | 排表布局按组分行（进攻1/进攻2 每行 3 队、防守1/防守2 每行 2 队）；导入请假识别结果默认全选、点击可取消/恢复（取消的不纳入请假，带删除线样式） | 排表、出勤库 |
| 2026-08-17 | 修复「详情页打不开」：LineupEditor.vue 样式区被写入异常损坏（`</style>` 提前关闭 + 残留重复片段导致 Vite 编译 500、详情页白屏），删除残留后恢复，浏览器验证排表编辑器正常 | 排表 |
| 2026-08-17 | 出勤库职业支持主/副切换：后端出勤列表返回可选职业列表（主+副去重）、新增 PUT attendance/{id}/profession 接口（校验可选范围、补人不可改）；前端职业列多选项渲染为下拉（管理员可切），单选项保持纯文本；替补导入弹窗加载失败增加兜底提示 | 出勤库 |
| 2026-08-17 | 出勤库职业缺口条修复：缺口统计改为仅计算正常出勤（请假视为缺口），切换请假状态后缺口条实时联动 | 出勤库 |
| 2026-08-17 | 修复「导入替补」弹窗恒为空：根因是数据加载写在 computed setter 里，父组件更新 prop 时 setter 不执行导致请求从未发出；改为 defineModel + watch 触发加载，浏览器验证候选列表正常显示 | 出勤库 |
| 2026-08-17 | 修复排表候选池成员「拖上去再拖下来显示补」：拖拽往返转换（toSlotItem/toCandidateItem）丢失 member_status 导致兜底误标 filler；SlotItem 增加 member_status 字段并在转换中保留 | 排表 |
| 2026-08-17 | 排表导出 PNG 重构：导出按钮移至「排表总览」卡片 header，导出内容改为总览区域（四组阵容+职业分布）；修复组件 ref 误传组件实例导致 html2canvas 报「Element is not attached to a Document」（外层包裹原生 div 承载 ref）；清理 lineupBoard 中已迁移的导出死代码 | 排表 |
| 2026-08-17 | Docker Compose 部署文件就绪：backend/frontend Dockerfile（多阶段构建）、frontend/nginx.conf（静态托管+API 反代+SPA 回退+20m 上传限制）、docker-compose.yml（SQLite 数据卷+健康检查+80 端口）、.env.example；本机验证前端生产构建与后端迁移/初始化命令链通过 | 部署 |
| 2026-08-18 | 修复联赛日程日历「日期与星期对不上」：根因 dayjs 默认以周日为一周起点，`startOf('week').subtract(1,'day')` 实际得到周六起始；改为显式计算周一 `monthStart.subtract((day()+6)%7,'day')`，浏览器验证对齐 | 联赛日程 |
| 2026-08-18 | 侧边栏折叠/展开功能（MainLayout.vue）：顶栏左侧新增鎏金折叠按钮，折叠后侧边栏 208px→64px 仅留图标（el-menu collapse，hover 显示原生 title 菜单名），Logo 区切换为「令」字印章，顶栏布局同步配合；折叠状态 localStorage 持久化 | 布局 |
| 2026-08-18 | 折叠 Logo 调整：展开保持原状（帮会名），折叠显示帮会名首字（模板内联三元，移除中间计算属性） | 布局 |
| 2026-08-18 | 录屏链接脱敏（RecordingTab.vue）：帮众账号下录屏链接不显示明文，仅显示「已提交」胶囊状态；点「修改」时输入框空白不回显原链接，提交后再次进入脱敏态；管理员账号可查看完整链接审核；后端仍存明文（前端展示层脱敏） | 录屏审核 |
| 2026-08-18 | 录屏 Tab 新增按姓名搜索（帮众/管理员均可见，与局数/状态筛选叠加）；全部页面表格「姓名」列标题改为「ID」（常驻库/出勤/录屏/替补导入/出勤率 5 处，表单输入标签保持「姓名」） | 录屏审核、全站 UI |
| 2026-08-18 | 「姓名→ID」全局文案统一：表单标签/占位符/校验提示/搜索框/排表说明全部改为 ID（成员表单、补人表单、常驻库搜索、录屏搜索、排表总览、请假导入提示）；Excel 导入表头提示保留「姓名」（后端解析依赖该列名），补人按姓名匹配的代码注释保留 | 全站 UI |
| 2026-08-18 | 删除功能：后端新增 DELETE /config/guilds/{id}（仅开发者，级联删除帮会全部关联数据：账号/成员/赛程/出勤/排表/录屏/分析/职业配置）与 DELETE /config/accounts/{id}（不能删自己/开发者账号）；前端帮会管理表格新增「删除」列、账号操作列新增「删除」按钮，均带危险二次确认 | 系统配置 |
| 2026-08-18 | 修复折叠侧边栏菜单项内部偏移：折叠态强制隐藏菜单文字（span display:none）并使图标居中，避免 Element Plus 默认 collapse 样式失效导致图标+文字混合偏移 | 布局 |
| 2026-08-18 | 修复开发者创建账号逻辑不可用：根因是后端 create_account 只取 current_user.guild_id（开发者恒为 None 被拒），前端传的 guildId 未被 schema 接收；现 AccountCreate 增加 guild_id 字段，API 用 body.guild_id or current_user.guild_id 定位目标帮会，前端提交时转 snake_case 传 guild_id，后端语法检查通过 | 系统配置 |
| 2026-08-18 | 系统配置账号表格响应式优化：操作列取消 fixed 固定（280px→min-width 170px），全列改弹性 min-width，页面缩小时表格随容器自适应压缩，不再出现固定列撑宽溢出 | 系统配置、响应式 |
| 2026-08-18 | 全站表格响应式统一：常驻库/录屏/出勤/出勤率/替补导入/数据分析（数据列表+排行榜+职业统计）/赛程列表/联赛总览/配置页全部表格列 width→min-width、取消所有 fixed 固定列（selection/# 窄列保留固定），页面缩小时表格弹性压缩 | 全站 UI、响应式 |
| 2026-08-18 | 联赛日程列表支持「本月/全部」切换（el-radio-group 雅金风按钮组，全部时无时间参数查全量）；出勤表职业下拉去掉 small 尺寸统一 14px 字体；数据分析工具栏新增「按ID搜索」过滤玩家（与阵营筛选叠加） | 联赛日程、出勤、数据分析 |
| 2026-08-18 | 登录错误提示与锁定机制完善：后端 auth_service 失败提示带剩余次数、达阈值立即返回锁定提示（含解锁时长）、锁定期提示剩余分钟；前端 http.ts 登录请求 401 不再误走全局 Token 过期分支（交由登录页展示），非登录接口 401 清除本地 Token + SPA 跳转登录页 + 弹出「登录已过期，请重新登录」；登录页新增 el-alert 错误提示区（凭证错误/锁定/网络异常），输入时自动清除；vue-tsc 类型检查通过 | 认证、登录页 |
| 2026-08-18 | JWT 有效期调整为 10 小时：config.py 默认值 7 天（10080 分钟）改为 600 分钟，backend/.env.example 部署模板同步改为 600 | 认证 |
| 2026-08-18 | 账号不存在也锁定：auth_service 新增进程内存记录（_unknown_login_failures），不存在账号连续失败同样计数/锁定（阈值与提示文案与 users 表一致），登录成功时清理同名残留记录；服务重启后内存计数清零，无数据库迁移 | 认证 |
| 2026-08-18 | 锁定期间禁止输入：AuthError 携带 remaining_seconds（锁定剩余秒数，users 表与内存记录共用），main.py 认证异常处理器将其写入响应 data；登录页解析后启动倒计时，锁定期间禁用用户名/密码输入框与登录按钮，倒计时归零自动恢复，提示条实时显示「账号已锁定，请 X 分 X 秒后重试」 | 认证、登录页 |
| 2026-08-18 | 录屏审核修复（浏览器验证）：① 请假人员不再出现在录屏列表（后端 list_recordings 过滤 AttendanceRecord.status==leave，请假无需提交录屏，进度统计同步排除）；② 切换到「录屏审核」Tab 自动刷新（RecordingTab 新增 defineExpose reload，ScheduleDetailView onTabChange 对 recording 调用 reload，与排表 Tab 同模式） | 录屏审核 |
| 2026-08-18 | 排表请假联动修复（浏览器复现用户流程验证）：出勤库成员置为请假后，切回排表时该成员自动从槽位移出——lineup_service 新增 _purge_leave_members，get_lineup 读取时按出勤库 leave 状态清空槽位（正式按 member_id、补人按姓名匹配，JSON 列整体替换触发变更检测）并落库，覆盖排表编辑器/总览/自动保存全链路，与候选池过滤逻辑一致 | 排表、出勤库 |
| 2026-08-18 | 新增「一键导入历史排表」功能：① 后端 GET /schedules/{id}/lineup/history 列出本帮会有排表的其他赛程（含完整排表数据）；POST /schedules/{id}/lineup/import 按选中小队导入——仅当前候选池（出勤正常）中出现的成员按原位置排入（正式按 member_id、补人按姓名），未出现的槽位留空，仅覆盖选中小队，槽位备注一并导入；② 前端 LineupEditor 工具栏新增「导入历史排表」按钮 + ImportHistoryDialog 弹窗（选赛程 → 按组多选小队，雅金风风格），导入成功自动刷新编辑器与总览；vue-tsc 类型检查通过 | 排表 |
| 2026-08-18 | 数据分析模块可视化大升级（参考 E:\code\@Cjy\B 的 MatchAnalysis，ECharts 可视化，浏览器 5 tab 全验证）：安装 echarts 依赖；新增 EChart.vue 通用封装（ResizeObserver 自适应 + 浅色雅金风 chartTheme.ts）、analysis.ts 计算工具（阵营/职业聚合、KDA、综合评分）；MatchDataTab 重构为 5 tab：①数据总览（统计卡+击杀占比条+阵营职业分布卡、阵营对比雷达图、关键数据柱状图+占比分析表、击杀vs伤害散点图、职业×指标热力图、阵营职业伤害/治疗堆叠柱状图）②数据列表（保留）③排行榜（KDA 双轴折线图、伤害折线图[玩家/建筑切换]、治疗/承伤折线图[切换] + 四榜）④职业分析（职业人数/伤害占比饼图、伤害/建筑水平柱状图、职业明细表[人均击杀/占比/治疗占比]）⑤综合评分（TOP10 评分雷达图、输出vs生存散点图、评分排名表[输出/建筑/治疗/生存/特殊/KDA]）；所有图表前端基于 getMatchData 现有字段计算，无需后端改动；vue-tsc 类型检查通过 | 数据分析、图表 |
| 2026-08-18 | 开发者角色完善：users 表新增 plain_password 字段（Alembic 迁移 e5f6a7b8c9d0）、role 新增 developer（不绑定帮会）；init_db.py 仅空库时初始化、admin/member 密码改为可选；后端 config_service 新增帮会 CRUD（创建/删除）、账号删除；前端系统配置新增帮会管理 Tab（开发者专属）、账号表格显示帮会名与明文密码 | 认证、系统配置 |
| 2026-08-18 | 出勤库批量导入成员：后端 attendance_import 新增 import_members（从常驻库选人批量加入出勤表）、all_member_candidates（过滤已导入成员返回候选列表）；前端 AttendanceTab 新增「导入成员」按钮 + ImportMemberDialog 弹窗（候选列表勾选导入） | 出勤库 |
| 2026-08-18 | 排表备注增强：lineups 表新增 title_remark（标题备注）、groups_remark（各组备注 JSON）字段（Alembic 迁移 dbb752d924fe）；后端排表读写适配新字段；前端 LineupEditor 支持标题备注与组备注编辑（el-input + ElMessageBox.prompt），导出 PNG 包含备注 | 排表、数据库 |
| 2026-08-18 | 首页仪表盘重写（HomeView.vue +859 行）：统计卡片、职业分布、最近赛程、快捷操作、出勤率排行、录屏进度等模块全面重构 | 首页 |
| 2026-08-18 | 登录页重写（LoginView.vue +264 行）：锁定倒计时、错误提示区、输入时自动清除、水墨风格背景 | 登录页 |
| 2026-08-18 | 全站样式系统完善：element-plus.css（+496 行）深度定制 Element Plus 组件主题；theme.css（+138 行）设计令牌扩展；index.css（+106 行）全局样式重构 | 样式系统 |
| 2026-08-18 | 后端测试脚本清理：删除 7 个硬编码测试脚本（smoke_test/attendance_test/config_test/import_test/lineup_test/match_data_test/recording_test），新增 generate_import_template.py（生成成员导入 Excel 模板） | 后端脚本 |
| 2026-08-18 | deploy.sh 新增：Linux 一键部署脚本（Docker Compose 构建+启动+健康检查） | 部署 |
| 2026-08-26 | 数据分析模块文档对齐：8 Tab（新增阵营对比/小队分析/职业深度/指标说明）、后端 7 接口（衍生指标/阵营对比/小队分析）、16 项衍生指标；移除 HTML 报告导出描述；data-analysis-complete.md 移入 memory-bank | 数据分析 |
| 2026-08-26 | 新增分析调整模块（squad_adjustments）：后端 model/schema/service/api + 前端类型/API；小队分析内支持手动分配未排表成员到目标队伍，仅作用于分析视图不改正式排表 | 分析调整 |
| 2026-08-26 | 文档全面对齐：progress.md 代码目录结构与模块说明同步实际代码（修复 Alembic 迁移数 12→9、补全 services/api/utils 文件列表、新增分析调整/开发者 API 模块）；architecture.md 补全文档索引；design-document-v2.md 修正布局尺寸、补充开发者角色与分析调整；tech-stack.md 修正 ECharts 版本 5→6、FastAPI 版本、补全文件列表；backend/frontend docs 补全 developer 角色与分析调整模块 | 全文档 |
| 2026-08-26 | 文档命名统一：DATA_ANALYSIS_COMPLETE.md → data-analysis-complete.md、SECURITY-REVIEW.md → security-review.md，memory-bank 全部文件统一为小写 kebab-case | 全文档 |
| 2026-08-26 | 新增 AI 入门文档：根目录 CLAUDE.md（精简版，AI 自动读取）+ memory-bank/ai-context.md（完整扩展版），涵盖项目概述、技术栈、编码规范、Git 工作流、文档体系、安全要点 | CLAUDE.md, ai-context.md |
| 2026-08-26 | 目录树补全：补充 CLAUDE.md、GIT-GUIDE.md、.claude/rules/ 入库条目；database-design 版本号 v1.5→v1.6 | progress.md |
| 2026-08-26 | 新增 AI 操作检查清单（ai-checklist.md），记录易错模式与自检流程；CLAUDE.md 新增"操作前必读"提示 | ai-checklist.md, CLAUDE.md |
| 2026-08-26 | 文档瘦身与单一权威源：design-document-v2 删除内嵌 UI 规范改为引用；CLAUDE.md/ai-context 技术栈/Git/安全改为引用；修复 README 9 表、backend/docs v1.5、UI 主色矛盾 | 全部文档 |
| 2026-08-26 | 新增 UI 优化方案文档（ui-polish-plan.md）：4 优先级 11 项优化清单、动画族规范、卡片层级规范、验收标准；ui-style-guide.md 新增 §10 优化补充规范 | ui-polish-plan.md, ui-style-guide.md |
| 2026-09-11 | 联赛总览（录屏上传）页移动端专项优化：≤768px 表格改为整卡可点的场次卡片列表（日期/时间/局数/结果 + 对手名 + 箭头，按下变浅金），筛选改为等宽 44px 三段时间筛选条，窄屏短提示「点击场次进入录屏上传」，空态用 el-empty；桌面端表格与全局样式不变；vue-tsc 类型检查与生产构建通过 | 联赛总览、移动端 |
| 2026-09-11 | 赛程详情页移动端优化（帮众：录屏审核 + 数据分析）：≤768px 录屏表格改为行列表（ID/职业/局数/状态 + 提交/修改/通过/驳回 44px 按钮 + 行内全宽编辑 + 备注行，管理员支持移动端勾选批量审核），页面按钮/局筛选/局切换加大触控区，卡片内边距收紧；桌面端不变；vue-tsc 类型检查与生产构建通过 | 赛程详情、录屏、数据分析 |
| 2026-09-11 | 录屏备注功能 + 行内按钮重做：recordings 表新增 note 列（Alembic 迁移 l6m7n8o9p0q1）；后端新增 PUT /recordings/{id}/note（自由内容、不影响审核状态、空值校验）；前端移动端行列表按钮去 primary+plain（主题渐变叠加显浑浊）改鎏金/墨色描边，「提交链接/修改链接」与「备注/修改备注」并列，备注行内编辑全宽 textarea；桌面端新增「备注」列；帮众对备注与链接一样仅见状态（已备注/修改），提交后不回显内容，管理员可见全文；vue-tsc 类型检查与生产构建通过，迁移已应用到开发库 | 录屏、赛程详情、数据库 |
| 2026-09-11 | 移动端录屏行列表提交反馈强化：恢复「已提交/已备注」金色状态胶囊（描边 pill，置于对应按钮前），操作行支持 flex-wrap（窄屏自动折行不溢出）；构建通过 | 录屏、移动端 |
| 2026-09-11 | 移动端录屏行列表信息层级调整：「已提交/已备注」胶囊移至 ID 旁，职业·局数下沉到次行（主行：ID + 胶囊 + 审核标签，375/320px 均不挤压名字，次行「职业 · 局数」小字）；构建通过 | 录屏、移动端 |
| 2026-09-11 | 性能优化专项（后端+前端+构建部署三层面审查后全部修复）：①SQLite 开 WAL/synchronous=NORMAL/busy_timeout=30s；②审计中间件复用 request.state.user（省 JWT 解码+查库）、日志清理改 24h 定时循环；③bcrypt/openpyxl/PIL/CSV 解析全部移入 asyncio.to_thread（长图导出加 800 人上限）；④GET 不再写库（排表/调整副本/职业配置内存返回、录屏占位 INSERT OR IGNORE）；⑤个人战绩 N+1→3 查询、排行榜/日志统计下推 SQL；⑥复合索引迁移 m7n8o9p0q1r2 已应用；⑦前端 el-tab-pane 全部 lazy、搜索防抖 250ms、请求序号防竞态、录屏分页、computeScores/aggregateCamps WeakMap 缓存、fetchMe 5s 去重、html2canvas 动态导入；⑧Element Plus JS 按需（unplugin-vue-components，样式保留全量保证主题覆盖顺序）、ECharts 按需注册（1.1MB→634KB 独立 chunk）、manualChunks 拆分；⑨nginx gzip + /assets/ immutable 缓存 + index.html no-cache，Docker 构建跳过 vue-tsc（build:only）。首屏 JS 降至 273KB（gzip 103KB）；冒烟自检、vue-tsc 与生产构建通过 | 性能、数据库、构建部署 |
| 2026-09-11 | 发版后旧版本页面自动更新机制（main.ts 两重防御）：①vite:preloadError——部署后旧页面懒加载新文件名 chunk 失败时自动刷新一次恢复（sessionStorage 防循环，挂载成功清除标记），仍失败提示 Ctrl+F5 强刷；②发版自动检测——打开 3 秒后/切回窗口/每 10 分钟对比服务器最新构建入口（fetch no-store），发现新版本自动刷新（正在输入时不打断、同标签页只自动刷一次，已是最新版时清除标记）；实测线上部署瞬间旧页面请求已下线的 MemberListView/ConfigView chunk 返回 404（后端全程 200 无异常），刷新即恢复；vue-tsc 与生产构建通过 | 前端、部署体验 |
| 2026-09-11 | 微信端旧页面缓存问题修复：排查确认服务器 index.html 已是最新构建（引用 index-BUpqpB32.js），旧页面来自微信内置浏览器（X5/XWeb）磁盘缓存——仅 `Cache-Control: no-cache` 时 X5 不重新验证直接使用缓存。修复：nginx `location = /index.html` 由 `expires -1` 改为 add_header 输出 `no-cache, no-store, must-revalidate` + `Pragma: no-cache` + `Expires: 0`（nginx.conf 与 nginx.conf.example 同步，服务器侧需手动同步并重建 frontend 镜像）；`frontend/index.html` 内嵌同款 meta 缓存标签（X5 读取 HTML meta，双保险）；构建验证 dist/index.html 含 meta。已缓存旧页面的用户仍需手动刷新一次（服务器无法远程清除微信缓存） | 前端、部署、微信兼容 |
| 2026-09-11 | 成员列表页操作区移动端优化：≤768px 五个操作按钮由竖排全宽堆叠改为两列网格（添加成员满宽 + 其余 2×2），44px 触控高度、8px 间距，删除旧 ≤480 竖排规则；桌面端不变 | 常驻库、移动端 |
| 2026-09-11 | 成员列表页表格移动端优化：≤768px el-table 改为成员行列表（勾选 + ID + 状态标签主行 / 职业色标签次行 / 备注行 / 编辑·删除 44px 描边按钮；勾选复用 selectedIds 支撑批量删除，刷新与断点切换自动清空），卡片内边距收紧 14px，空态 el-empty；桌面端表格不变；vue-tsc 类型检查与生产构建通过 | 常驻库、移动端 |
| 2026-09-11 | 成员列表移动端行列表微调（用户反馈迭代）：编辑/删除由 44px 满宽改 32px 紧凑右对齐描边按钮；职业标签组（主+副）移至动作行最左，与编辑/删除同行；主行精简为 勾选 + ID + 状态标签 | 常驻库、移动端 |
| 2026-09-11 | 联赛日程页赛程表格移动端适配（参照帮众侧联赛总览卡片信息层级）：≤768px el-table 换为行列表（时间/局数/结果标签主行 + vs 对手次行 + 详情·删除 32px 紧凑描边按钮右对齐），表格卡片内边距收紧 14px，空态 el-empty；桌面端表格不变；vue-tsc 类型检查与生产构建通过 | 联赛日程、移动端 |
| 2026-09-11 | 出勤表移动端专项优化：≤768px el-table 换为行列表（勾选 + ID + 类型标签 + 状态开关主行 / 职业选择器或彩色职业名 + 移除 32px 紧凑按钮次行），勾选复用 selectedIds 支撑批量请假/正常（刷新与断点切换自动清空），删除失效的表格压缩规则；桌面端表格不变；vue-tsc 类型检查与生产构建通过 | 出勤、移动端 |
| 2026-09-11 | 赛程详情页头按钮移动端紧凑化（用户反馈「按钮太大」）：返回/编辑/删除赛程 由 44px 满宽三等分改为 32px 内容宽度右对齐 | 赛程详情、移动端 |
| 2026-09-11 | 排表候选池显示常驻库备注：后端 GET /schedules/{id}/lineup/candidates 带出 Member.remark（member_remark，随已有 join 查询）；前端候选池成员项在姓名后以单行省略显示备注（hover 提示完整内容），仅候选池展示、拖入槽位即消失（不随槽位流转）；vue-tsc 类型检查与生产构建、后端 py_compile 通过 | 排表、候选池 |
| 2026-09-11 | 出勤库备注完整链路（用户指正候选池备注来源）：①attendance_records 新增 remark 列（Alembic 迁移 n8o9p0q1r2s3 已应用开发库）；②三个导入入口（一键导入正式/导入成员/导入替补）导入时带出常驻库备注；③新增 PUT /schedules/{id}/attendance/{record_id}/remark（仅管理员，留空清除），列表接口带 remark；④AttendanceTab 桌面表格新增「备注」列、移动端行列表新增备注行与编辑笔（弹窗编辑，仅管理员）；⑤排表候选池改读出勤库备注（字段更名 attendance_remark），拖入槽位即消失；存量记录不回填（用户确认仅新导入生效）；vue-tsc 与生产构建、后端 py_compile、迁移应用全部通过 | 出勤、排表、候选池 |
| 2026-09-11 | 移动端三处适配：①排表编辑器工具栏（≤768px 三行布局：统计满宽 + 进度条 flex 自适应 + 标题备注/保存态/模式切换一行 + 导入/保存按钮整行均分，删除冗余 ≤480 按钮规则）；②录屏页进度条（≤768px 改纵向整行列表，每局一行，chip 36/行 40 紧凑高度，删除冗余 ≤480 规则）；③录屏行列表（管理员行：职业行与「未提交」行左缩进 28px 与 ID 对齐）；vue-tsc 类型检查与生产构建通过 | 排表、录屏、移动端 |
| 2026-09-11 | 移动端五处适配：①首页统计卡 ≤480 单列改两列（仅顶部四卡，间距/内边距收紧）；②成员编辑弹窗表单排版美化（标签 13px 加粗、字段间距收紧）；③出勤率统计面板移动端专属行列表（ID+职业+出勤率% / 进度条+正常·请假，替换表格，卡片内边距 14px）；④系统配置-职业配置表格换行列表（职业+数字步进器一行 / 说明整行）；⑤数据分析工具栏移动端布局（导入+阵营筛选均分、搜索占满+指标说明贴右）；vue-tsc 类型检查与生产构建通过 | 首页、常驻库、系统配置、数据分析、移动端 |
| 2026-09-11 | 数据分析模块图表卡全面移动端适配审查与修复：审查确认所有图表 grid 均已折叠（10 文件）；两处补齐——①EChart.vue 封装组件统一做响应式高度（≤768px 数值高度 300~360px 收敛至 280px，ResizeObserver 自适应当前图，分析模块 8 处图表+个人战绩 2 处图表统一受益）；②9 个文件 chart-card 内边距收紧 14/16→12px（释放窄屏约 8px 宽度）；桌面端不变；vue-tsc 类型检查与生产构建通过 | 数据分析、移动端 |
| 2026-09-11 | 修复出勤率统计面板移动端排序丢失（行列表替换表格后表头 sortable 无入口）：面板标题栏右侧新增「升序/降序」分段控件（仅移动端渲染，32px 紧凑高度），默认升序与接口默认一致（出勤率升序、无记录始终排最后）；桌面端仍用表格表头排序不变；vue-tsc 类型检查与生产构建通过 | 常驻库、出勤率、移动端 |
| 2026-09-15 | 补人姓名规范化修复（用户反馈：出勤库添加补人后排表偶发不显示职业，移除重导才恢复）：根因为姓名规范化不一致——添加补人时原样保存（可带首尾空白）、保存排表时 strip，出勤姓名与槽位姓名精确匹配失败导致职业为空。修复：①新增 utils/member_names.py（normalize_member_name）与 services/lineup_attendance.py（get_profession_map/candidate_pool 抽出；职业映射/候选池统一按「去首尾空白」匹配，规范化后重名或空名显式报 409 而非静默覆盖）；②FillerCreate 模型 field_validator(mode=before) 先清理再校验长度，add_filler 清理姓名并与本场全部出勤姓名（含常驻成员）查重；③排表读取响应按规范化键填充槽位职业（仅响应规范化，不改写历史数据），save_lineup/import_lineup/请假清理统一 normalize_member_name，前端 FillerDialog 提交前 trim；④验证：后端 py_compile 通过、vue-tsc 通过、真实库 4 赛程 181 个已填槽位规范化后 100% 关联出勤职业、无重名冲突——存量异常数据无需删除重导即可恢复 | 出勤、排表 |
| 2026-09-15 | 文档全面优化（依据实际代码核实）：修正出勤率公式/术语（客人→补人）/失效引用（保存考勤、verify_e2e）；权限矩阵与帮众端页面按代码校正（出勤/排表 Tab 仅管理员）；补全个人战绩/系统日志模块链路（目录树/模块表/页面树）；tech-stack 去重（目录树与依赖清单改引用权威源）并修正部署卷/健康检查/包管理/工具链失实项；ai-context 引用化；data-analysis 瘦身 768→610 行并修复 25 个代码块围栏与残缺字符；implementation-plan、ui-polish-plan 归档标注；ai-checklist 编号修复 + 新增「多处复制」遗漏模式 | 全部文档 |
| 2026-09-15 | 工具目录改名同步（.claude/ → .agent/）：目录树、规则与样例文档路径引用（`.agent/rules/`、`.agent/docs/`）全量同步，deploy.sh 打包排除项由 `.claude` 改为 `.agent` | 全部文档、部署 |
| 2026-09-15 | 根目录 `CLAUDE.md` 更名为 `AGENTS.md` 并扩充为 AI 开发指南：项目规范 + 权威源映射表（自 ai-checklist 迁入）+ 各文档维护时机 + 文档同步与进度追踪流程（完成后自检清单）+ AI 行为约定；ai-checklist/ai-context/architecture/.agent/rules 引用同步 | 文档体系 |
| 2026-09-15 | 文档失实项修正（实测：11 张表/14 个迁移/head n8o9p0q1r2s3）：表数 10→11、迁移数 13→14、database-design 引用 v1.6→v1.8（含目录树条目）；补记 operation_logs 表；backend/frontend docs 帮众场景与权限按代码校正、补个人战绩/系统日志模块、移除 xlsx/保存考勤失实表述；DEPLOY.md 迁移 head 同步 | 文档体系 |
| 2026-09-15 | 文件行数超限必要性评估与豁免标记：28 个超限文件逐一评估——15 个判定拆分（后端 3：match_data_service/config_service/api config；match-data 4：SquadAnalysisTab/PlayerAnalysis/RankingTab/ProfessionDetailTab；排表·出勤·录屏 3：LineupTab/AttendanceTab/RecordingTab；视图布局 5：HomeView/ConfigView/LogView/MemberListView/MainLayout），13 个判定为连续逻辑豁免并打「行数豁免」标记（LineupEditor、lineupBoard、MatchDataTab、LoginView、StatsMatchTable、ScoreTab、LeagueOverviewView、ScheduleListView、ScheduleCalendar、ImportHistoryDialog、OverviewTab、members.py、attendance.py）；file-length-rule.md 新增豁免机制与豁免清单，ai-context §3.1/§8.1 同步 | 代码规范、文档 |
| 2026-09-15 | 阶段 1 拆分行数超限后端文件（match_data_service 581→4 文件：match_data_csv/match_data_stats/match_data_aggregate + 主服务 ~250；config_service 370→account_service/guild_service/config_service；api config.py 212→config/accounts/guilds 三路由，URL 不变）；同步 import 方（api match_data/developer、my_stats_service、main.py、selfcheck_indicators 脚本）；compileall + 导入冒烟 + 63 条路由健全性 + 指标自检通过 | 后端、代码拆分 |
| 2026-09-15 | 阶段 2 拆分行数超限 match-data 前端文件（SquadAnalysisTab 1295→主 ~230 + 6 子组件 + squadCharts/squadCompareCharts；PlayerAnalysis 637→ ~230 + playerScatterCharts/playerAggregateCharts/playerRadar；RankingTab 477→ ~270 + rankingCharts；ProfessionDetailTab 476→ ~180 + ProfessionMetricTables/ProfessionCompareTable/professionDetailCharts）；保持 route.query（squadTab/metricSub）持久化与全部样式令牌/类名不变；npm run build（vue-tsc + vite）通过 | 数据分析、代码拆分 |
| 2026-09-15 | 阶段 3 拆分行数超限排表·出勤·录屏文件（AttendanceTab 898→ ~230 + AttendanceStatsBar/Toolbar/TablePanel/MobileList/useAttendanceList；RecordingTab 867→ ~170 + RecordingProgressBar/TablePanel/MobileList/useRecordingList + recording-shared.css（scoped src 共享样式）；LineupTab 497→ ~40 + LineupOverviewPanel/LineupOverviewGroup（PNG 导出与落盘逻辑随迁））；勾选/行内编辑/数组占位数据形态与样式令牌不变；npm run build（vue-tsc + vite）通过 | 出勤、录屏、排表、代码拆分 |
| 2026-09-15 | 阶段 4 拆分行数超限视图/布局文件（HomeView 1065→主 ~220 + views/home/ 7 卡片组件 + home-shared.css；ConfigView 774→ ~130 + ConfigProfession/Guild/AccountPanel/AccountGroup；LogView 662→ ~210 + LogStatsCards/FilterBar/MobileList/TablePanel/DetailDialog/ClearDialog + logLabels.ts；MemberListView 594→ ~170 + MemberStatsBar/Toolbar/TablePanel + useMemberList；MainLayout 551→ ~130 + AppSidebar/AppHeader + useRouteProgress）；route.query tab 持久化、折叠态 localStorage、移动端抽屉/断点行为与全部样式令牌不变；npm run build（vue-tsc + vite）通过 | 首页、配置、日志、常驻库、布局、代码拆分 |
| 2026-09-15 | 阶段 5 拆分收尾复测：15 个待拆分文件及其新建子文件全部 ≤300 行（最大 RecordingMobileList 299）；13 个豁免文件「行数豁免」标记齐全（grep 13/13）；全量扫描无新增超限文件 | 代码规范、代码拆分 |
| 2026-09-15 | 生产部署改「单层 TLS」（消除双层 nginx + 双层 TLS）：边缘 nginx-proxy 独占 TLS/证书/限流/安全响应头/HTTP→HTTPS 跳转，反代改 `http://…:80` 并启用 upstream keepalive(32)；frontend 容器退化为「静态资源 + /api 反代」（明文 80、无宿主端口映射、无证书挂载），新增 `set_real_ip_from` 与 IP 头透传。配套修复：①内层 `limit_req` 以 `$remote_addr`（=边缘容器 IP）为键，导致限流退化为全站共享桶（登录全站 5 次/分、API 全站 20r/s）②安全响应头在 /assets 与 /api 上重复下发 ③登录审计 IP 记为前端容器 IP（新增 `core/client_ip.py` 的 `get_client_ip`，auth.py/main.py 复用）。验证：四域名入口 200、响应头计数均为 1、限流按真实 IP（外部第 5 次 429 且另一源 IP 正常）、内层 443 已关闭、30 次请求仅 2 条 upstream 连接 | 部署、安全、后端 |
| 2026-09-15 | 部署收尾两项：①`/assets/` 响应头去重——删除 `expires 1y`（该指令会额外生成一个 `Cache-Control: max-age=31536000` 与显式 immutable 并存成重复头），仅保留 `add_header Cache-Control`，与 `index.html` 既有约定一致；②边缘层 XFF 由追加改为覆盖（`$proxy_add_x_forwarded_for` → `$remote_addr`，3 处），防客户端自带 XFF 伪造审计 IP。验证：`/`、`/assets/`、`/api/` 三处响应头重复种数均为 0，gzip 与 index.html no-store 未受影响，携带伪造 `X-Forwarded-For: 1.2.3.4` 的登录探测审计仍记录真实 IP；重建前端容器期间 90 次探测 89×200 + 1×502 | 部署、安全、后端 |
| 2026-09-15 | 仓库收录策略调整：`.agent/rules/*.md` 4 份 AI 编码规则入库（.gitignore 以 `!.agent/rules/` 例外于 `rules/` 忽略，保证 AGENTS.md 权威源可追溯）；`.agent/docs/` 仅文本 CSV 入库，24MB `联赛数据表Plus3.0.xlsm` 保持本地忽略（本地文件不删，仅不收录历史） | 文档体系、仓库 |
| 2026-09-15 | 发布 v1.1.0（tag `v1.1.0`，双远端同步）：自 v1.0.0 起累计 38 个提交——新增个人战绩与系统日志模块、UI 优化与移动端适配、出勤备注与性能优化，以及超限文件拆分、补人姓名规范化修复、单层 TLS 部署改造 | 版本发布、双远程 |

---

## 使用说明

1. **代码变更后**：必须更新本文档的"代码模块说明"部分
2. **新增模块**：在对应表格中添加模块信息
3. **完成阶段**：更新"开发进度"状态

# 项目进度与代码结构

## 代码目录结构

```
nsh-management/
├── backend/                   # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/               # API 路由（v1/ 路由注册 + deps 依赖注入）
│   │   ├── core/              # 配置、数据库、安全（JWT/密码）、客户端 IP 解析（client_ip）
│   │   ├── models/            # 12 张表 SQLAlchemy 模型（含 squad_adjustments/operation_logs/member_game_id_requests）
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── services/          # 业务逻辑（account/auth/config/guild/game_id_request/game_id_request_lifecycle/lineup/lineup_attendance/log/match_data/match_data_aggregate/match_data_csv/match_data_stats/member/my_stats/player_identity/recording/attendance/schedule/squad_adjustment）
│   │   ├── utils/             # 工具函数（attendance_import/excel_import/excel_export/image_export/constants/member_names）
│   │   ├── init_db.py         # 初始化默认帮会与账号（开发者/admin/member）
│   │   └── main.py            # 应用入口（CORS/异常处理/AuthError锁定秒数）
│   ├── alembic/               # 数据库迁移（15 个版本）
│   ├── data/                  # SQLite 数据库（nsh.db）
│   ├── docs/README.md         # 后端模块开发文档
│   ├── scripts/               # 工具脚本
│   │   ├── audit_weights_v4_20260907.py   # 贡献度权重审计（v4）
│   │   ├── derive_weights_v4_20260907.py  # 贡献度权重推导（v4）
│   │   ├── generate_import_template.py    # 生成成员导入模板
│   │   ├── selfcheck_game_id_requests.py          # 改名申请回归（真实 JWT + ASGI，内存库）
│   │   ├── selfcheck_game_id_requests_concurrency.py # 改名申请并发回归（隔离文件库 + 独立连接）
│   │   ├── selfcheck_indicators.py        # 衍生指标自检脚本
│   │   ├── selfcheck_member_exports.py    # 出勤隔离 + Excel 回导回归（内存库）
│   │   ├── selfcheck_migration_game_id.py # 改名表迁移隔离验证（临时库升级/回退）
│   │   ├── selfcheck_my_stats_aliases.py  # 新旧 ID 战绩关联回归（真实 JWT + ASGI，内存库）
│   │   ├── selfcheck_security_fixes.py    # 用户隔离回归（真实 JWT + ASGI 路由，内存库）
│   │   └── sim_contribution_v4_20260907.py # 贡献度模拟（v4）
│   ├── templates/             # Excel 模板
│   │   └── member_import_template.xlsx  # 成员导入模板
│   ├── Dockerfile             # 后端容器镜像（多阶段构建）
│   ├── .dockerignore
│   ├── entrypoint.sh          # 容器启动脚本
│   ├── requirements.txt
│   ├── requirements-dev.txt    # 开发/CI 依赖（ruff、pytest、httpx；含 PEP 263 编码声明）
│   ├── pytest.ini             # pytest 配置（新用例 + 既有 selfcheck_*.py，内存库）
│   ├── ruff.toml              # 后端静态检查配置（E4/E7/E9/F）
│   ├── tests/                 # pytest 用例（conftest/support + 安全工具、弱密钥门禁、权限矩阵、姓名规范化）
│   └── .venv/                 # 虚拟环境（本地目录，不入库）
├── frontend/                  # 前端项目（Vue3+TS+Vite）
│   ├── src/
│   │   ├── api/               # Axios 封装（http/auth/config/lineups/members/attendance/matchData/recording/schedules/squadAdjustments）
│   │   ├── components/        # 业务组件
│   │   │   ├── attendance/    # 出勤库（AttendanceTab+AttendanceStatsBar/AttendanceToolbar/AttendanceTablePanel/AttendanceMobileList/FillerDialog/ImportMemberDialog/LeaveImportDialog/SubstituteImportDialog）
│   │   │   ├── common/        # 通用组件（SkeletonTable/EmptyState）
│   │   │   ├── lineups/       # 排表（LineupEditor/LineupTab+LineupOverviewPanel/LineupOverviewGroup/ImportHistoryDialog/MatchConfirmDialog）
│   │   │   ├── match-data/    # 数据分析（MatchDataTab/OverviewTab/IndicatorsTab/RankingTab+rankingCharts/paretoChart/CampCompareTab/SquadAnalysisTab+SquadOverviewPanel/SquadCardsGrid/SquadDetailDialog/SquadMembersTabs/SquadCompareDialog/SquadAssignDialog/squadCharts/squadCompareCharts/ProfessionTab/ProfessionDetailTab+ProfessionMetricTables/ProfessionCompareTable/professionDetailCharts/ScoreTab/PlayerAnalysis+playerScatterCharts/kdaScatterCharts/playerAggregateCharts/playerRadar/CampCompare/MetricsGuideDialog/MatchReportDialog/reportData.ts/report（MatchReportPoster/PosterHeader/PosterOverview/PosterMvpKings/PosterRankings/PosterRounds/PosterSquads）/EChart/analysis.ts/chartTheme.ts）
│   │   │   ├── members/       # 常驻库（AttendanceRatePanel/MemberStatsBar/MemberToolbar/MemberTablePanel/MemberFormDialog/MemberImportDialog/MemberDetailHeader/ProfessionShortage/GameIdRequestForm/GameIdRequestHistory/GameIdReviewPanel/GameIdReviewDialog + game-id-shared.css）
│   │   │   ├── my-stats/      # 个人战绩（PlayerSearch/StatsOverview/StatsMatchTable/StatsRankingPosition/StatsTrendChart/StatsIdentityNotice）
│   │   │   ├── recording/     # 录屏审核（RecordingTab+RecordingProgressBar/RecordingTablePanel/RecordingMobileList/recording-shared.css）
│   │   │   └── schedules/     # 联赛日程（ScheduleCalendar）
│   │   ├── composables/       # 组合式函数（lineupBoard/useAttendanceList/useRecordingList/useMemberList/useRouteProgress/useTableDensity）
│   │   ├── layouts/           # 主布局（MainLayout + AppSidebar/AppHeader；深檀侧边栏208px+宣纸顶栏62px，支持折叠64px）
│   │   ├── router/            # 路由与守卫
│   │   ├── stores/            # Pinia（auth）
│   │   ├── styles/            # 浅色雅金风主题（theme.css 令牌 / element-plus.css 组件 / index.css 入口）
│   │   ├── types/             # TS 类型定义（attendance/auth/config/lineup/matchData/member/recording/schedule）
│   │   ├── utils/             # 工具函数（constants/profession/scheduleSort/attendance，含同名 *.spec.ts 单测）
│   │   └── views/             # 页面
│   │       ├── HomeView.vue           # 首页仪表盘（壳）+ home/ 卡片组件（HomeWelcome/HomeTodayBanner/HomeStatCards/HomeRecentSchedules/HomeProfessionOverview/HomeAttendanceRanking/HomeQuickActions + home-shared.css）
│   │       ├── LoginView.vue          # 登录页（含锁定倒计时）
│   │       ├── config/ConfigView.vue  # 系统配置壳（+ ConfigProfessionPanel/ConfigGuildPanel/ConfigAccountPanel/ConfigAccountGroup）
│   │       ├── logs/LogView.vue       # 系统日志壳（+ LogStatsCards/LogFilterBar/LogMobileList/LogTablePanel/LogDetailDialog/LogClearDialog/logLabels.ts）
│   │       ├── member-home/           # 帮众首页（MemberHomeView + GuildStatCards/RecentMatchesCard/DataHighlightCard/RecordingTodoStrip/MemberQuickActions + stats/highlight/types + card-shared.css）
│   │       ├── member/MyStatsView.vue # 个人战绩（帮众/管理员；支持合并新旧 ID 与冲突退路）
│   │       ├── member/GameIdChangeView.vue # 修改游戏 ID（帮众：提交改名申请 + 查看记录）
│   │       ├── members/MemberListView.vue  # 常驻库
│   │       ├── members/MemberDetailView.vue # 成员详情（管理员：信息卡+出勤率+历史战绩，复用 my-stats 组件）
│   │       └── schedules/             # 联赛日程
│   │           ├── ScheduleListView.vue      # 日程列表
│   │           ├── ScheduleDetailView.vue    # 赛程详情（管理员：出勤/排表/录屏/分析；帮众：录屏/分析）
│   │           └── LeagueOverviewView.vue    # 帮众联赛总览
│   ├── Dockerfile             # 前端容器镜像（多阶段构建）
│   ├── .dockerignore
│   ├── nginx.conf             # 内层反代配置（容器构建输入，占位符版；2026-10-02 起入库）
│   ├── nginx.conf.example     # 边界层（边缘 Nginx：静态托管+HTTPS+限流）配置模板
│   ├── docs/README.md         # 前端模块开发文档
│   ├── eslint.config.js       # ESLint 扁平配置（vue flat/essential + typescript-eslint）
│   ├── .prettierrc.json       # Prettier 约定（semi=false / singleQuote / printWidth 120）
│   ├── vitest.config.ts       # Vitest 配置（jsdom，src/**/*.spec.ts）
│   └── package.json
├── memory-bank/                # 项目文档
│   ├── ai-context.md           # AI 项目完整上下文文档
│   ├── ai-checklist.md         # AI 操作检查清单（错误记录与联动规则）
│   ├── architecture.md         # 文档索引
│   ├── code-ui-audit-2026-09.md # 2026-09 代码审查与 UI 评估结论快照
│   ├── data-analysis-complete.md # 数据分析模块完整方案
│   ├── database-design.md      # 数据库设计文档（v1.9）
│   ├── design-document-v2.md   # 产品设计文档（当前主文档）
│   ├── design-game-id-change.md # 游戏 ID 改名申请与战绩关联设计（已实施，待浏览器验收）
│   ├── implementation-plan.md  # 实施方案文档
│   ├── progress.md             # 本文档 - 代码结构与进度
│   ├── security-review.md      # 安全审查文档
│   ├── stats-report-plan.md    # 成员战绩与战报实施方案（已实施，2026-09-17）
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
├── .editorconfig               # 编辑器统一约定（换行/缩进/编码）
├── .gitattributes              # 换行策略与二进制标记（text=auto eol=lf，脚本与批处理为 crlf）
├── .githooks/                  # 版本化 Git 钩子（commit-msg 提交消息校验，需 install_git_hooks.sh 启用）
├── .github/                    # GitHub 平台配置（workflows/ci.yml、dependabot.yml、commit-msg-baseline）
├── scripts/                    # 仓库级脚本（check_file_length / check_commit_msg / install_git_hooks）
├── AGENTS.md                   # AI 开发指南：规范/文档维护/进度追踪（自动读取）
├── start.bat                   # 一键启动脚本（前后端+首次建库）
├── deploy.sh.example           # Linux 部署脚本模板（复制为 deploy.sh 填写域名；deploy.sh 已被 .gitignore 忽略）
├── docker-compose.yml          # Docker Compose 编排（Nginx + FastAPI + SQLite 卷）
├── .env.example                # 部署环境变量模板（复制为 .env 填写）
├── DEPLOY.md                   # 部署文档（Docker Compose 全流程）
├── GIT-GUIDE.md                # Git 管理规范（分支/提交/发布/双远程）
├── CHANGELOG.md                # 更新日志（Keep a Changelog 1.1.0）
├── CODE_OF_CONDUCT.md          # 行为准则（Contributor Covenant 2.1 官方中文译本）
├── CONTRIBUTING.md             # 贡献指南（摘要 + 权威源链接 + 本地门禁命令）
├── SECURITY.md                 # 安全政策（报告渠道 / 支持版本 / 处理时限）
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
| 帮众首页 | src/views/member-home | 战绩看板（统计卡/最近比赛/数据亮点（MVP/数据之王））+ 录屏待办状态条 + 快捷入口；帮众登录默认落点 | ✅ 已完成 |
| 常驻库页面 | src/views/members | 列表/筛选/弹窗/Excel导入/出勤率/成员详情战绩页（复用 my-stats 组件）/改名审核 Tab（严格管理员） | ✅ 已完成 |
| 联赛日程页面 | src/views/schedules | 日历/创建弹窗/详情Tab/联赛总览 | ✅ 已完成 |
| 出勤库页面 | src/components/attendance | 统计/导入成员/导入请假/替补/补人/状态/保存 | ✅ 已完成 |
| 排表页面 | src/components/lineups | 候选池/拖拽编排/总览/导出PNG/导入历史排表/串行保存与重载防覆盖 | ✅ 已完成（F04 交互待验收） |
| 录屏审核页面 | src/components/recording | 列表/提交/审核/进度/按姓名搜索/链接脱敏 | ✅ 已完成 |
| 数据分析页面 | src/components/match-data | CSV导入/8Tab可视化（总览/列表/排行榜/阵营对比/小队分析/职业分析/职业深度/综合评分）/16项衍生指标/指标说明/单场图文战报（PNG 导出）/ECharts图表（HTML tooltip 输出转义） | ✅ 已完成（F01 交互待验收） |
| 系统配置页面 | src/views/config | 职业配置/账号管理/帮会管理（开发者） | ✅ 已完成 |
| 个人战绩页面 | src/views/member + src/components/my-stats | 玩家搜索/单局明细/概览（按游戏 ID 聚合，支持合并经审核确认的新旧 ID；冲突时仅查此 ID）；管理员菜单入口开放，同组件复用于成员详情页 | ✅ 已完成 |
| 游戏 ID 改名页面 | src/views/member/GameIdChangeView + src/components/members（GameIdRequestForm/GameIdRequestHistory/GameIdReviewPanel/GameIdReviewDialog） | 帮众提交改名申请与查看记录；管理员在常驻库「改名审核」Tab 通过/驳回 | ✅ 已完成 |
| 系统日志页面 | src/views/logs | 审计日志筛选/分页/清理（开发者） | ✅ 已完成 |
| 样式系统 | src/styles/ | 浅色雅金风主题（theme.css + element-plus.css + index.css） | ✅ 已完成 |

### 后端模块

| 模块 | 路径 | 作用 | 状态 |
|------|------|------|------|
| 基础框架 | app/core | 配置（JWT 10h）、异步数据库、JWT/密码 | ✅ 已完成 |
| 数据模型 | app/models | 12 张表 SQLAlchemy 模型 + 15 个 Alembic 迁移 | ✅ 已完成 |
| 认证模块 | app/api/v1/auth.py | 登录/登出/me + 登录限流（含未知账号锁定） | ✅ 已完成 |
| 常驻库 API | app/api/v1/members.py | CRUD/筛选/批量删/Excel导入/出勤率/职业统计/单成员详情 | ✅ 已完成 |
| 联赛日程 API | app/api/v1/schedules.py | CRUD/时间范围/级联创建删除 | ✅ 已完成 |
| 出勤库 API | app/api/v1/attendance.py | 导入成员/替补/补人/请假导入/状态/保存/职业切换 | ✅ 已完成 |
| 排表 API | app/api/v1/lineups.py | 候选池/读写/保存校验/规范化/导入历史/备注 | ✅ 已完成 |
| 录屏审核 API | app/api/v1/recording.py | 提交/审核/批量审核/进度 | ✅ 已完成 |
| 数据分析 API | app/api/v1/match_data.py | CSV导入/6榜排行/职业17项统计/16项衍生指标/阵营对比/小队分析 | ✅ 已完成 |
| 分析调整 API | app/api/v1/squad_adjustments.py | 小队分析内未排表成员→目标队伍的临时分配（仅作用于分析视图，不改正式排表） | ✅ 已完成 |
| 开发者 API | app/api/v1/developer.py | 开发者专属路由（帮会管理/账号管理等） | ✅ 已完成 |
| 系统配置 API | app/api/v1/config.py + accounts.py + guilds.py | 职业配置/账号管理/帮会管理（开发者）/删除帮会/删除账号（URL 前缀均为 /config） | ✅ 已完成 |
| 个人战绩 API | app/api/v1/my_stats.py | 玩家名搜索/按游戏 ID 聚合历史战绩（支持经审核确认的新旧 ID 合并；冲突 409） | ✅ 已完成 |
| 游戏 ID 改名 API | app/api/v1/game_id_requests.py + services/game_id_request_service.py/game_id_request_lifecycle.py/player_identity_service.py | 候选检索/提交/成员历史/审核列表/原子审核；生命周期联动与战绩新旧 ID 关联 | ✅ 已完成 |
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
| 2026-09-17 | 新增成员战绩与战报实施方案（stats-report-plan.md，用户确认三项决策：独立成员详情页 / 管理员开放个人战绩菜单 / 战报先做单场）：成员详情战绩页（/members/:id）与单场图文战报（数据分析一键生成 PNG）；design-document 升至 v2.5、backend/frontend docs 登记待办 | 文档、成员详情、战报 |
| 2026-09-17 | 成员详情战绩页与单场图文战报实施完成：①后端新增 GET /members/{member_id}（require_admin，注册于全部具体路径之后防路由捕获）；②前端新增 MemberDetailView/MemberDetailHeader + /members/:id 路由 + 常驻库 ID/名字入口 + 管理员「个人战绩」菜单（AppSidebar）；③profTagStyle 抽取至 utils/profession（成员表同步复用）；④战报：MatchReportDialog + reportData.ts + report/ 海报 5 组件（960px 固定宽：头部/阵营对比双向条形/三榜 TOP3 金银铜徽章/职业分布），MatchDataTab 工具栏「生成战报」+ schedule props 透传，html2canvas 动态加载导出 PNG（独立 chunk）；vue-tsc + vite build 通过，待浏览器验收 | 常驻库、个人战绩、数据分析、后端 |
| 2026-09-17 | 战报 v2 重设计（用户反馈原版太简陋、无信息含量）：海报扩展为 8 区块——新增全场总览（四数字卡）、MVP 金卡+数据之王六格（击杀/伤害/建筑/治疗/承伤/焚骨）、逐局战况（每局结果+双营比分+该局 MVP/击杀王），阵营对比扩至 6 指标+差值、榜单按玩家去重取最佳单局、职业分布加伤害占比；数据层改为单接口（getIndicators 全场记录）+ 前端组装（复用 computeScores/aggregateProfessions）；vue-tsc + vite build 通过 | 数据分析、战报 |
| 2026-09-17 | 战报口径调整（用户要求：不要两个阵营、只要我方）：我方阵营判定复刻后端小队分析口径（排表成员命中数最多阵营，兜底首条记录阵营），全部区块仅统计我方记录；删除阵营对比区块（PosterCampCompare 移除）、总览扩为六卡（击杀/助攻/伤害/建筑/治疗/焚骨）、逐局改我方击杀/伤害/治疗；弹窗加载增加排表接口（失败降级）；vue-tsc + vite build 通过 | 数据分析、战报 |
| 2026-09-18 | 战报区块替换（用户要求：职业分布没必要）：移除职业分布（PosterProfessions 删除），新增「小队战况」（PosterSquads：按排表归属聚合我方各队击杀/对玩家伤害/治疗，未排表成员单列，无排表时区块自动隐藏，复用已加载排表零额外请求）；reportData 移除 professions/aggregateProfessions、新增 squads 聚合；vue-tsc + vite build 通过 | 数据分析、战报 |
| 2026-09-18 | 小队战况修复（用户反馈信息不完整、未对齐）：数据列由 3 项扩为 7 项（+助攻/对建筑伤害/承伤/焚骨）；已排表但无比赛记录的队伍改为显示 0（不再跳过，排表队伍完整呈现）；修正表头「小队」列被右对齐规则误伤导致的错位（对齐规则改为 :not(:first-child)，表头与数据逐列对齐）；vue-tsc + vite build 通过 | 数据分析、战报 |
| 2026-09-18 | 修复帮会图标字切换账号后"被清空"（用户浏览器批注排查）：根因为登录接口 `UserOut.model_validate(user)` 序列化时 User 模型仅有 guild_name property、缺 guild_icon，登录响应 guild_icon 恒为默认值 None（/me 为手动构造故正常）→ 切换账号后前端 auth.user.guild_icon 为空，配置页输入框与侧边栏图标回退；修复：User 模型补 guild_icon property（与 guild_name 对称），实证脚本修复前后对比 None→'帮'；数据未丢失（仅登录路径序列化缺陷） | 认证、系统配置、后端 |
| 2026-09-18 | UI 可选 3 项收尾（ui-polish-plan §2.1.3/§2.3.3/§2.4.4）：①表格密度切换（顶栏全局开关，标准 13.5px/10px ↔ 紧凑 12.5px/6px，localStorage 持久化，移动端隐藏；新增 composables/useTableDensity + element-plus.css 密度档规则）；②空状态 SVG 插画（新增 components/common/EmptyState：empty/search/chart/error 4 变体宣纸金线手绘风，替换全站 20 处 el-empty 默认插画）；③职业标签 hover 微光（.prof-tag 白色高光扫过 0.5s，hover:hover 门控）；vue-tsc + vite build 通过 | 全模块 UI |
| 2026-09-18 | 用户隔离与权限定向修复（security-review.md §十 F-1～F-5）：①账号创建跨帮会越权修复——accounts.py 按角色收紧 target_guild_id（管理员仅本帮会，跨帮会 403；开发者目标帮会需存在，400/404/422），account_service 写库前校验帮会存在，AccountCreate.guild_id 加 ge=1；②member_service.attendance_rate 出勤聚合关联 Schedule 限定 guild_id（防外帮会脏引用污染本帮会统计）；③未绑定帮会创建/导入成员提前 403（更正：Member.guild_id NOT NULL 本就存在，原为 500 风险）；④Excel 各 Sheet 首行加帮会来源标识 + 导出文件名含帮会名（服务端/客户端同步，非法字符清理），导入兼容新旧格式且归属只取认证帮会；⑤批量 ID 统一 schemas/common.py BatchIds（1～500 严格正整数：成员批量删/出勤导入与批量状态/录屏批量审核）；新增 scripts/selfcheck_security_fixes.py + selfcheck_member_exports.py 共 16 项回归全部通过；后端 compileall + 前端 vue-tsc/vite build 通过 | 认证、常驻库、出勤、录屏、系统配置、后端 |
| 2026-09-20 | 新增「游戏 ID 改名申请与战绩关联」设计（design-game-id-change.md，用户确认三项决策：共享账号代填 + 人工核实身份 / 通过后仅改写常驻库不改历史数据 / 个人战绩新旧 ID 合并查询且冲突时停止自动合并）；同步 database-design v1.9（新增 member_game_id_requests 表，表数 11→12）、design-document v2.6（权限矩阵/功能列表/页面结构）、data-analysis-complete 口径、stats-report-plan 引用；代码与迁移待实施 | 文档、常驻库、个人战绩 |
| 2026-09-20 | 「游戏 ID 改名申请与战绩关联」实施完成：①后端新增 member_game_id_requests 表（迁移 o9p0q1r2s3t4，含 CHECK、pending 部分唯一索引、approved 关联索引）与 model/schema/service/lifecycle/player_identity/route 六件套；②提交与审核均为单事务原子写（条件 UPDATE + 行数校验，通过与 members.name 同一事务提交，重放 409）；③权限新增 require_member / require_admin_strict / require_member_or_admin（developer 一律 403），归属只取认证上下文；④生命周期联动（成员直接改名/删除、账号删除、整帮会删除）由 game_id_request_lifecycle 统一维护且不自行 commit；⑤个人战绩按 approved 关系合并新旧 ID 查询最近 10 场（含连续改名与改回），可检测冲突（当前重名/他人批准记录/失效引用/同局多名称或阵营）返回 409 并保留 merge_aliases=false 精确退路，指标与排名口径不变；⑥前端新增帮众页 /game-id-change、常驻库「改名审核」Tab、个人战绩模式切换与冲突提示、成员详情冲突跳转；⑦验证：4 个新增 selfcheck（改名 13 项、并发 5 项、别名 9 项、迁移 1 项）与既有 16 项回归全部通过，后端 compileall、前端 vue-tsc/vite build 通过；未做浏览器验收 | 常驻库、个人战绩、后端、前端 |
| 2026-09-20 | 帮众改名页成员候选移除正式/替补标签及无用样式，保留游戏 ID 与职业；管理员侧与接口不变，同步专项设计和前端开发文档；vue-tsc + vite build 通过，未运行前端测试或浏览器验收 | 前端、游戏 ID 改名 |
| 2026-09-20 | 战报小队归属修复（用户反馈：小队分析内分配未排表成员后，生成战报的小队仍显示未分配）：根因为 reportData.buildReportData 仅按正式排表（lineup）聚合小队战况，未读取分析调整副本（squad_adjustments，该副本原仅在小队分析视图前端叠加生效）；修复：MatchReportDialog 并发加载 getSquadAdjustments（失败降级为 null，不阻断生成），buildReportData 增加 adjustments 参数，按目标队伍 key 校验后叠加覆盖成员小队归属（目标已不存在于排表时忽略，与小队分析视图口径一致）；我方阵营判定口径不变（仍按排表命中，与后端 squad-analysis 一致）；reportData.ts 按行数规则登记豁免（.agent/rules/file-length-rule.md）；stats-report-plan §3.2/§3.3 与 frontend docs 同步；vue-tsc + vite build 通过 | 数据分析、战报、前端 |
| 2026-09-20 | 战报逐局战况新增「重伤第一」（用户要求：每局的重伤第一也挂出来）：ReportRoundInfo 增加 deathKing（取该局我方重伤次数最多者，并列取首个最大值，与击杀王同口径），PosterRounds 副行显示「重伤第一 名字 N 次」并允许换行防长名溢出；未导入局不显示；口径同步 stats-report-plan §3.2 与 frontend docs；vue-tsc + vite build 通过 | 数据分析、战报、前端 |
| 2026-09-20 | 战报小队战况新增「重伤」列（用户要求：小队战况里面把重伤也加上）：ReportSquadItem 增加 deaths 并纳入聚合（含空队显示 0），PosterSquads 表格列由七项扩为八项（重伤插在助攻后，与小队分析表列序一致）并同步网格列宽；口径同步 stats-report-plan §3.2 与 frontend docs；vue-tsc + vite build 通过 | 数据分析、战报、前端 |
| 2026-09-20 | 战报高光榜单扩为六榜（用户要求：还要有建筑伤害榜、重伤榜、总分榜）：MatchReportData 增加 buildingTop/deathsTop/scoreTop；buildReportData 复用逐局 computeScores 结果，按玩家保留最佳单局综合评分生成总分榜（与 MVP 口径一致），重伤榜按重伤次数倒序、建筑伤害榜按对建筑伤害（均沿用去重取最佳单局）；PosterRankings 三列两行展示六榜 TOP3；口径同步 stats-report-plan §1.2/§3.2、design-document-v2 §4.5 与 frontend docs；vue-tsc + vite build 通过 | 数据分析、战报、前端 |
| 2026-09-20 | 管理员直接改名自动记录历史 ID 关联（用户确认新增支持）：原设计“直接改名不追溯别名”导致直接改名后无法合并查询；现 `PUT /members/{id}` 改名时同一事务失效待审申请并写入一条 approved 关联（`game_id_request_lifecycle.record_admin_rename`，提交/审核人=操作管理员快照，`review_remark` 标注“管理员直接在常驻库改名（自动记录，无提交申请）”），个人战绩即时支持新旧合并；`member_service.update_member` 增加 operator 参数（路由与并发 selfcheck 同步）；测试：game_id_requests 扩展自动记录断言、my_stats_aliases 新增直接改名合并用例（13/5/10/1 项 + 既有 16 项全部通过）；文档同步 design-game-id-change §1/§5/§6、database-design §2.12（v1.9 补充）、design-document-v2 §4.1、security-review §十一、backend docs | 常驻库、个人战绩、后端 |
| 2026-09-20 | 暂存代码审查修复（Warning）：帮众改名页「常驻成员」远程搜索补请求序号守卫（GameIdRequestForm.searchMembers）——快速连续输入时旧响应可能覆盖新结果、先完成的请求会把 loading 提前复位；按同批组件 GameIdRequestHistory/GameIdReviewPanel 既有 loadSeq 惯例新增 searchSeq：过期响应直接丢弃，loading 仅在最新请求 finally 复位；vue-tsc 通过，未运行前端测试与浏览器验收 | 前端、游戏 ID 改名 |
| 2026-09-20 | 并发回归断言修正（selfcheck_game_id_requests_concurrency.py）：原「审核 approved ⇒ 成员名必等于新 ID」假设单一写者，未覆盖「审核通过 → 管理员再次直接改名」这一合法交错（实测 4 次 1 次失败），与 security-review §十一「5 项全部通过」表述不符；改为按写者顺序断言——写入者未知时允许任一合法结果，仅在无后续写入者时要求名称等于新 ID，并新增「直接改名必留已确认关联记录」「invalidated ⇒ 名称必为直接改名结果」两条确定性断言；连续 10 次运行通过；security-review §十一 验证范围与 ai-checklist #17 同步 | 代码规范、改名申请 |
| 2026-09-24 | 全项目审查 F01/F04 定向修复：F01 图表自定义 HTML tooltip 统一输出转义（含评分、小队同类路径），按 200 行工具上限抽出 kdaScatterCharts/paretoChart 并保留原导出；安全边界见 security-review §十二。F04 排表保存统一串行、编辑版本与请求序号防覆盖、失败保留待保存状态，历史导入与路由离开/参数切换先保存；保存约定与人工用例见 frontend/docs。类型检查与 Vite 非清理构建通过（存在依赖注释、动态/静态导入及大 chunk 警告）；未运行前端测试或浏览器验收。保留原 CRLF，按 cr-at-eol 口径检查差异空白；未修改其他审查项、后端、依赖或数据库 | 前端、排表、数据分析、安全 |
| 2026-09-24 | 新增帮众专属首页（/member-home，登录默认落点）：①路由与守卫——新增 member-home（memberOnly），帮众登录跳转、adminOnly/developerOnly 回退、登录页已登录跳转三处落点由 league-overview 改为 member-home，侧边栏新增帮众「首页」菜单；②比赛焦点卡（MatchFocusCard）按优先级四态——今日未开赛（鎏金高亮，多场显示「另有 N 场」）> 录屏待办（最近一场已结束且 ≤7 天、存在未提交或被驳回，按局进度=已通过+待审、驳回单独标注，进度条驳回报赭黄/交齐报黛绿）> 下一场 > 最近一场（结果 + 各局结果）；今日比赛存在更早场次待办时以提示行保留独立入口；③快捷操作宫格（录屏上传/个人战绩/修改游戏 ID/联赛日程，2×2，触控 ≥44px）；④赛程详情 goBack 支持 from=home 回跳；⑤样式外置 focus-card.css（行数规则），finesse 静态检查 0 P0；vue-tsc 与 vite build:only 通过，未运行前端测试与浏览器验收 | 帮众首页、路由、布局、赛程详情 |
| 2026-09-24 | 帮众首页重设计（用户反馈「录屏待办块太大、展示内容没深度」）：弃双栏改全宽纵排——①焦点卡全宽重做：左日期块（今天/24 金底）+ 中比赛信息（对手/时间/局数/地点，最近一场含各局结果）+ 右操作按钮，底部 3px 鎏金条（与统计卡同语言）；②录屏待办改版：粗进度条（el-progress）改为紧凑逐局胶囊（已交=已通过+待审；驳回赭黄/交齐黛绿）+ 未交齐名单（前 5 名，悬停查看完整名单）+ 驳回人数，去除大块进度条；③快捷操作改整行四格、图标统一浅金底（去四色）并横向排布；④欢迎行衬线标题 + 日期右对齐；vue-tsc 与 vite build:only 通过，finesse 0 P0，未运行前端测试与浏览器验收 | 帮众首页、UI |
| 2026-09-24 | 帮众首页内容重设计（用户确认新方向「帮会战绩看板」）：以数据为主线重做内容——①战绩统计卡 4 张（已赛场次/近5场战绩/局胜率/录屏完成，与管理员首页统计卡同语言：浅金图标底+渐变数字+底部金条+数字滚动）；②最近比赛结果列表（近 5 场，含各局比分，点击进详情）；③数据亮点卡（最近一场 MVP + 数据之王六格，复用战报同源 buildReportData，reportData/analysis 成为共享分包；最多尝试最近 3 场有数据场次、失败静默降级）；④录屏待办收敛为一行状态条（未交齐/驳回人数 + 悬停完整名单 + 去处理）；⑤删除比赛焦点卡（MatchFocusCard/focus-card.css），新增 GuildStatCards/RecentMatchesCard/DataHighlightCard/RecordingTodoStrip/stats.ts/highlight.ts/card-shared.css；vue-tsc 与 vite build:only 通过，finesse 0 P0（渐变数字为 ui-style-guide §5.3 锁定规范），未运行前端测试与浏览器验收 | 帮众首页、UI |
| 2026-09-28 | 小队分析模块新增单成员「取消分配」功能：后端 DELETE /schedules/{id}/squad-adjustments/{player_name} 端点 + 前端成员表操作列；修复「重置调整」按钮缺少 isAdmin 权限门控 | 数据分析 / 小队分析 |
| 2026-09-28 | 新增代码审查与 UI 评估报告 memory-bank/code-ui-audit-2026-09.md | 文档/全栈审查 |
| 2026-09-28 | 三个严重问题修复（code-ui-audit-2026-09.md C-1～C-3）：①accounts 响应统一脱敏——新增辅助函数 _build_account_out(account, current_user)，list/create/update/update_status 四条响应路径全部对非 developer 角色置空 plain_password（developer 仍可见，明文列按既定决策保留）；②config 生产弱密钥启动门禁——APP_ENV 主判据 + 容器特征兜底 + 弱片段/年份黑名单 + 64 位 hex 豁免，开发环境 fail-open 仅 WARNING；docker-compose backend 固定 APP_ENV=production；deploy.sh 健康检查失败改非零退出并打印容器日志；根与 backend .env.example、DEPLOY.md、README 补门禁与核对说明；security-review.md 同步（C-1 关闭 + C-2 门禁专节）；③element-plus 主按钮对比度与禁用态——实心主按钮文字改墨色 --ink-900（对比度达 AAA），:not(.is-plain):not(.is-text):not(.is-link) 收敛作用域，新增可辨禁用态；ui-style-guide.md §4.1 同步 | 系统配置 / 安全 / 部署 / UI |
| 2026-09-28 | 清理误创建的 backend/nul 垃圾文件：非 cmd shell（Git Bash / Node 子进程等）中 `> nul` 重定向按普通文件名处理，把一次后端启动的 SECRET_KEY FATAL 报错写入了真实文件 backend/nul；删除该文件并在 .gitignore 增加 Windows 保留设备名 nul 忽略规则；ai-checklist §五 补充第 20 条 | 仓库配置、文档 |
| 2026-09-28 | C-3 主按钮深色文字方案按用户美观偏好回退为白字+浅金渐变，对比度作为已知接受项；element-plus.css 恢复原样（移除 --ink-900 文字色与自定义禁用态），ui-style-guide §4.1 与审查报告同步 | UI / 文档 |
| 2026-10-02 | 发布 v1.2.0（附注标签 `v1.2.0`，标签对象 `78b3abf` → 提交 `e8d33ba`（初版对象 `3b9f0fd` 的 tagger 为本机身份，已删除重建为 `jiayu.chen <2226937684@qq.com>` 与 v1.0.0/v1.1.0 统一，指向提交不变），说明「release: v1.2.0 新增游戏 ID 改名审批与战绩关联、成员战绩页与单场图文战报，收紧跨帮会数据隔离」）：自 v1.1.0 起累计 24 个提交——新增游戏 ID 改名审批与身份关联、成员详情战绩页、单场图文战报（逐局重伤王与六榜）与帮众专属首页，跨帮会数据隔离与账号响应脱敏收紧、UI 优化收尾；发布前工作区干净且与 origin/main 同步，标签推送后经 `git ls-remote` 核对远端标签对象与指向提交均与本机一致；发布记录文档以提交 `04b4cfa`（docs(release)）推送 main，标签仍固定在发布提交 `e8d33ba`（main 领先标签一个提交）；本次仅推送 origin（本地检出未配置 gitee 远端，见 GIT-GUIDE §1 备注） | 版本发布、Git 规范 |
| 2026-10-02 | 新增项目合规化与工程完善计划（`.agent/plans/compliance-remediation-plan.md`，登记为 `architecture.md` §21 并同步目录树与 AGENTS.md 文档索引）：以行业权威规范（SemVer 2.0.0、Conventional Commits 1.0.0、Keep a Changelog 1.1.0、OWASP ASVS 5.0.0、OWASP Top 10:2025、SLSA v1.2、12-Factor、CIS Docker Benchmark）为基准的全仓静态审查结论与整改路线——42 项差距证据清单（3 项 P0 交付阻断：`frontend/Dockerfile:11` 依赖未入库的 `nginx.conf`、`deploy.sh` 未入库、生产配置漂移无检测）、Wave 0～4 共 31 项任务（含逐项验收命令、风险回滚、估算）、6 项待确认决策；本轮仅新增计划文档与索引登记，未改动任何代码、配置或依赖 | 文档、工程效能 |
| 2026-10-02 | Wave 0 文档一致性批次 1（合规化计划 `.agent/plans/compliance-remediation-plan.md` 的 W0-3/4/5/7）：①`memory-bank/architecture.md` 19 处 + `.agent/rules/code_rule.md` 2 处陈旧绝对路径 `e:\code\@Cjy\...`（本仓库旧位置）改为仓库相对路径（脚本替换后逐行复核 diff）；②`memory-bank/SECURITY-REVIEW.md` → `security-review.md` 实际落地（两步 `git mv`，Windows 大小写不敏感规避；历史记录中的旧名属时间戳证据保留）；③`README.md` 删除复制的代码目录树副本，改为引用 `progress.md`/`architecture.md`（消除目录树多源漂移）；④`backend/.dockerignore`、`frontend/.dockerignore` 的旧目录名 `.claude` → `.agent`；⑤`backend/scripts/audit_weights_v4_20260907.py`、`derive_weights_v4_20260907.py`、`sim_contribution_v4_20260907.py` 移除 4 处硬编码绝对路径（DB 快照与 analysis.ts），改由环境变量 `NSH_DB_PATH` / `NSH_ANALYSIS_TS` 覆盖、默认回落到 backend/data 快照；⑥`frontend/src/components/match-data/analysis.ts` 计分口径注释引用 v3 → v4（v3 脚本不存在，属笔误）。验证：`python -m py_compile` 三脚本 exit 0；全仓 `-CaseSensitive` grep `e:\code\@Cjy` 仅剩计划文档自身证据行；未改业务逻辑、依赖与数据库 | 仓库配置、文档、脚本、前端注释 |
| 2026-10-02 | Wave 0 批次 2（合规化计划 W0-6/W0-8）：①`memory-bank/tech-stack.md` §部署方案 按权威源 `DEPLOY.md` 重写——删除「前端容器端口 80/443（HTTPS）」「后端容器多阶段构建」「启动脚本 deploy.sh（Linux 一键部署）」等失实描述，替换为单层 TLS 架构摘要（nginx-proxy 独占 TLS/限流/安全头；frontend 无宿主端口、不挂证书；backend 内网 :8000 非 root 运行）+ 权威源引用；`docker-compose.yml` 顶部新增注释，明确仓库内该文件为「本地/单机演示拓扑」、生产版本单独维护；②`.qoder/plans/` 3 份外部 AI 工具规划草案登记入 `architecture.md`（目录树 + §22 文档说明 + 更新记录），明确标注「非项目权威文档、仅存档」，对应功能在 progress 已有记录。验证：`grep -n '多阶段' tech-stack.md` 仅剩前端一处（后端已改单阶段，与 `backend/Dockerfile` 一致）；未改运行配置与依赖 | 文档、部署、配置注释 |
| 2026-10-02 | Wave 0 批次 3（合规化计划 W0-2）：新增 `.gitattributes`（`* text=auto eol=lf`；`*.bat`/`*.cmd`/`*.ps1` 保持 CRLF；png/jpg/jpeg/gif/ico/woff/woff2/xlsm/xlsx/db 标 `binary`）与 `.editorconfig`（UTF-8、LF、末行换行、裁剪行尾空白、py/sh 缩进 4、Markdown 保留行尾空白）；随后 `git add --renormalize .` 归一存量换行（改造前 `git ls-files --eol` = i/crlf 260 / i/lf 75；改造后复核见提交说明）。本次变更**不改变任何文件内容语义**，仅统一行尾，独立成提交以便回溯；用户本地 `core.autocrlf=true` 未改动 | 仓库配置、换行策略 |
| 2026-10-02 | Wave 0 批次 3 收尾（合规化计划 W0-2 配套）：补齐 8 个文本文件缺失的**末行换行**，与新引入的 `.editorconfig`（`insert_final_newline = true`）保持一致——`.agent/plans/compliance-remediation-plan.md`、`.agent/rules/function_rule.md`、`.qoder/plans/UI_polish_phase_audit_fixes_4f80f074.md`、`.qoder/plans/帮众游戏_ID_改名审批设计_e1d99897.md`、`backend/app/schemas/match_data.py`、`frontend/src/components/attendance/ImportMemberDialog.vue`、`frontend/src/components/match-data/ScoreTab.vue`、`frontend/src/components/match-data/analysis.ts`；仅追加换行符，无内容语义变化。验证：`git -c core.quotepath=false ls-files` 全量 325 个文本文件逐个读字节复检，缺末行换行 = 0（首次复检因 git 默认对非 ASCII 文件名加引号而漏检 1 个，改用 `core.quotepath=false` 后补齐） | 仓库配置、代码格式 |
| 2026-10-02 | Wave 1 批次 1（合规化计划 W1-1/W1-2/W1-6，**P0 交付链路可复现**）：①修复「全新克隆无法构建前端镜像」——`frontend/nginx.conf`（49 行，占位符版）入库并解除 `.gitignore` 忽略（此前 `frontend/Dockerfile:11` 的 `COPY nginx.conf` 因文件不在仓库而必然失败），`frontend/nginx.conf.example` 同步收窄为**边缘层（B 段）模板**，内层 A 段以 `nginx.conf` 为唯一副本，消除同一配置两处漂移；②新增 `deploy.sh.example`（92 行：占位符 + 路径锚定排除清单 + `healthy` 轮询 + 域名入口 200 校验 + 失败非零退出并打印容器日志），`DEPLOY.md §三` 补「复制为 deploy.sh」与配置归属说明；③`README.md` 新增「数据源模式（`DB_MODE`）」小节（默认 prod 快照、缺失自动回退 dev、快照 `.db` 不入库）与 Docker 部署段的构建前置提示。验证：`bash -n deploy.sh.example`（Git for Windows bash）exit 0；两个 Dockerfile 的 `COPY` 上下文源逐个存在性核对通过；`git check-ignore frontend/nginx.conf` 未命中。**未验证**：本机 Docker 守护进程未运行（`docker info` 无输出、命名管道不可用），镜像实构建与 `nginx -t` 未执行，留待 CI（W2-1）覆盖 | 部署、构建、仓库配置、文档 |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 21、22（均来自本轮整改的自我纠错）：①**静默命令必须判退出码**——`[bool](git check-ignore -q path)` / `if(git check-ignore -q path)` 在 PowerShell 中取的是 stdout（`-q` 恒空），恒为 False；本次据此误报「`deploy.sh` 不再被忽略」，实际仍由 `.gitignore:98` 忽略，正确写法为 `$LASTEXITCODE -eq 0`；②**计数类结论必须记录匹配范围与大小写选项**——合规化计划 F-37 首次记「23 处」系只 grep `*.md` 且 `Select-String` 默认不区分大小写所致（漏计 3 个脚本 4 处、误计另一项目 2 处），实为活引用 25 处 + 历史 2 处 | 文档、检查清单 |
| 2026-10-02 | Wave 2 批次 1（合规化计划 W2-1/W2-5/W2-7，**质量门禁**）：①新增 `.github/workflows/ci.yml` 四个 job——backend（`compileall` + 空库 `alembic upgrade head` + `import app.main` 验证启动门禁不误杀）、frontend（`npm ci` + `npm run build`，即 vue-tsc 类型检查 + vite 构建）、repo-hygiene（行数规则脚本 + `-F` 拦截陈旧绝对路径 + `i/crlf` 计数须为 0）、docker-build（双镜像构建，正是 F-08 `COPY nginx.conf` 的回归护栏）；②新增 `scripts/check_file_length.py`：超限文件须**同时**满足「行内 `行数豁免` 标记 + 豁免清单登记」，并校验清单悬空与登记行数增长 ≥20% 的复核提醒；③`.agent/rules/file-length-rule.md` 新增「前端 TS（composable / 组件内逻辑）300 行」类别（原规则未覆盖 `.ts`，`lineupBoard.ts` 484 行等既不受限也不在豁免清单内，度量失真）与「自动检查（CI 门禁）」小节；④新增 `.github/dependabot.yml`（pip/npm 周更分组各限 5、docker 双目录周更、github-actions 月更）。验证：本地 `python scripts/check_file_length.py` exit 0（211 文件 / 14 条登记）；`npm ci` exit 0、`vue-tsc` 无类型错误、`vite build` 成功（12.27s，2620 模块，仅 chunk 体积告警）；`python -m compileall -q backend/app backend/scripts backend/alembic` exit 0；⑤ai-checklist §五 新增遗漏模式 23（门禁的检测模式串会被自身 workflow 与描述该门禁的文档命中 → 模式串须拆开拼接、文档引用统一用省略号形式，且上线前须双向验证「通过 + 能报错」）。**未验证**：CI 工作流尚未在 GitHub 上运行（需 push 后观察）；本机 vite 构建需将 `TEMP` 指向工作区（系统 TEMP 下 esbuild 删除临时文件报 Access denied，属本机环境问题而非代码缺陷） | CI、代码规范、依赖自动化、检查清单 |
| 2026-10-02 | Wave 2 批次 2（合规化计划 W2-3 后端部分，**静态检查门禁**）：①新增 `backend/ruff.toml`——规则集 `E4/E7/E9/F`、`target-version=py311`、`line-length=120`，`alembic/versions/*`（autogenerate 产物）与 3 个一次性权重分析脚本按文件豁免（实测 E701/E702 共 41 项**全部集中在这 3 个脚本**，产品代码为 0，故按文件豁免而非全局忽略）；②新增 `backend/requirements-dev.txt`（`-r requirements.txt` + `ruff==0.12.0`），CI backend job 改为安装 dev 依赖并新增 `ruff check .` 步骤；③修复告警 9 处——`app/models/user.py` 的 `F821 Undefined name 'Guild'`：字符串注解 `Mapped["Guild | None"]` 由 SQLAlchemy 注册表解析、运行时不报错，但类型检查无法解析，改为 `if TYPE_CHECKING: from app.models.guild import Guild`（不引入运行时循环导入）；其余 8 处为安全自动修复（`init_db.py` 与 `selfcheck_migration_game_id.py` 的 f-string 无占位符、`schemas/match_data.py` 未使用的 `Field`、`selfcheck_indicators.py` 未使用的 `MATCH_DURATION_SECONDS`、3 个分析脚本多重导入拆行并去掉未使用的 `json`）；④`tech-stack.md` 开发工具表与依赖权威源同步（明确标注 ESLint/Prettier 仍未配置）。验证：backend 内 `ruff check .` → **All checks passed!** 且无弃用告警（已改用 `[lint]` 新 schema）；`python -m compileall -q backend/app backend/scripts backend/alembic` exit 0。**未验证**：ruff 在 CI 上的实际运行（需 push）；前端 ESLint/Prettier 与 mypy 未做 | 代码规范、CI、依赖 |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 24（提交消息的两个工具链陷阱）：①`git commit -m` 传多行且含引号的正文时，PowerShell 原生传参会拆参——技术说明里的类型注解写法中的 `\|` 被 git 当作 pathspec，报 `pathspec '\|' did not match` 并**提交失败**；②改用 `git commit -F <文件>` 后，因文件首行直接写正文，git 把整段正文取为 subject，导致该提交不符合 `<type>(<scope>): <中文摘要>`（实测后以 `--amend -F` 重写为 `ci(lint): 接入 ruff 静态检查并修复其告警`，树内容未变）。约定：多行消息一律写 `.git/` 下临时文件后 `-F`（首行主题、空行后正文、用完删除），提交后立即 `git log -1 --format='%s'` 复核；另注意管道到 `Select-Object` 会吞退出码（显示 -1），判定成败应以 `git log` 为准 | 文档、提交规范 |
| 2026-10-02 | Wave 2 批次 3（合规化计划 W2-4，**提交消息门禁**）：①`scripts/check_commit_msg.py`——校验 `<type>(<scope>): <中文摘要>`（类型白名单含 `merge`、scope 必填且允许 `Data-analysis` 类历史写法、摘要 ≤50 字符且至少一个中文字符、禁用「根据 diff」「AI 生成」），放行 `Merge …`/`Revert …`/`fixup!`/`squash!` 与纯注释消息，对 UTF-8 BOM 容错；`--self-test` 内置 15 条用例；②`.githooks/commit-msg`（版本化钩子，git 传入消息文件路径）+ `scripts/install_git_hooks.sh`（`git config core.hooksPath .githooks`，零依赖、可一键卸载）；③`.github/commit-msg-baseline` 记录基线 SHA `2a2b081`，CI 新增 `commit-msg` job 校验 `基线..HEAD`（`--no-merges`，`fetch-depth: 0` 保证基线可达），**基线之前的历史提交不追溯**；④`.agent/rules/git-commit-message.md` 补 `merge` 类型与「自动校验」小节（含 `-F` 多行消息与提交后复核约定）。验证：`--self-test` 15/15 通过；用 Git bash 原样模拟 CI 流程——真实范围 10 个提交**违规=0**，注入 `update(auth): 类型非法` 与纯英文摘要两个反例均 exit 1（双向验证）；钩子正例 exit 0 / 反例 exit 1；两个 shell 脚本 `bash -n` exit 0。**未验证**：CI job 在 GitHub 上的实际运行（需 push）；本机未启用 `core.hooksPath`（未改动用户 git 配置，启用方式已文档化） | 提交规范、CI、钩子 |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 25（PowerShell 向原生程序传文本的三重陷阱）：①管道注入 UTF-8 BOM（因 `[Console]::OutputEncoding` 被设为**带 BOM** 的 `[System.Text.Encoding]::UTF8`）并重编码中文；②`WriteAllText($f, $msg)` 收到字符串数组时 PowerShell 用空格把多行拼成一行（造成「摘要 283 字符」误报）；③参数需要字符串时不能依赖数组隐式转换。本轮实测后果：用 `--stdin` 模拟 CI 时 10 个**完全合规**的提交全被判违规；改用文件方式后违规 0。处置：传文本优先走文件、管道场景显式设无 BOM 编码、需要字符串时 `-join`、校验器容错 BOM（提交消息校验器已加 `\ufeff` 剥离），并牢记「验证失败先怀疑传递链路」 | 文档、检查清单、工具链 |
| 2026-10-02 | Wave 2 批次 4（合规化计划 W2-2 后端部分 + **一处真实修复**）：①修复入门阻断——`backend/requirements.txt` 与 `requirements-dev.txt` 补 `# -*- coding: utf-8 -*-` 编码声明：两文件含中文注释，而 pip 读 requirements 时按 PEP 263 cookie → BOM → 本地 locale 判定编码，中文 Windows（cp936）下 README 第一步的 `pip install -r requirements.txt` 会因 gbk 解码失败中断（本轮实测 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x8e`；Linux/容器 locale 为 UTF-8 故 CI 与镜像构建从不暴露）；②建立后端测试体系——`backend/pytest.ini`（`python_files` 同时匹配 `test_*.py`/`selfcheck_*.py`，使既有 6 个 selfcheck **无需改写**即被 pytest 收集；模块级断言脚本 `selfcheck_indicators.py` 暂 `--ignore`）、`backend/tests/`（`conftest.py` 引导路径 + `support.py` 内存库基类与角色矩阵种子 + 4 个新模块：`test_core_security`（bcrypt 哈希/JWT 篡改与过期）、`test_config_gate`（弱密钥判定与生产判定）、`test_permissions`（令牌链路 6 分支 + 6 个角色依赖矩阵）、`test_member_names`（姓名规范化含全角空格））；`requirements-dev.txt` 增 `pytest==9.1.1`/`httpx==0.28.1`；CI backend job 增 `python -m pytest`（`DATABASE_URL=sqlite+aiosqlite:///:memory:`）；README 增「后端测试与静态检查」与 pip 排错提示；`tech-stack.md` 开发工具表增 pytest。验证（Python 3.12 隔离 venv；本机默认 3.14 因 `pydantic-core` 无 cp314 wheel 不可用）：`python -m pytest` → **78 passed + 57 subtests passed in 24.23s**（含 6 个既有 selfcheck）。**附带实证（F-15 依据）**：`fastapi>=0.115.0` 未锁定，本次解析到 **0.142.2**（starlette 1.7.0），虽 selfcheck 全绿但版本漂移风险已具体化。**未验证**：CI 上的 pytest 运行（需 push）；前端 Vitest 未做 | 测试、依赖、CI、文档 |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 27（`git add -A` 吞入工具临时目录）：W2-2 安装依赖期间 pip 在**仓库根目录**生成 `pip-metadata-*/`、`pip-unpack-*/`（含二进制 `.whl`）与临时 venv `.tmp-venv312/`，`git add -A` 一并提交，使该提交由 17 个文件膨胀到 55 个（452 行 → 5758 行 + 二进制）；且路径命中 `.gitignore` 后 `git add -A` 不会为「已跟踪但已删除」的文件暂存删除，残留项须显式 `git rm -r --cached` 才清除。处置：提交前核对 `git diff --staged --name-only`；`.gitignore` 增补 `.tmp-*/`、`pip-metadata-*/`、`pip-unpack-*/`（随本提交落地）；因提交未推送，已用 `git rm -r --cached` + `git commit --amend --no-edit` 修正为 17 个文件的干净提交 | 文档、检查清单、仓库卫生 |
| 2026-10-02 | Wave 2 批次 5（合规化计划 W2-3 前端部分 + README 版本说明）：①新增 `frontend/eslint.config.js`——`eslint-plugin-vue` 用 `flat/essential`（**刻意不用 `flat/recommended`**：后者含 `max-attributes-per-line`/`html-indent` 等排版规则，对既有代码会产生数百条格式化告警）+ `@vue/eslint-config-typescript`（不做类型感知以保速度）+ `skipFormatting`；`vue/no-mutating-props` 过渡期降为 **warn**；②新增 `frontend/.prettierrc.json`（semi:false / singleQuote / printWidth 120 / trailingComma all，与既有代码风格一致）；`package.json` 增 `lint`/`lint:fix`/`format`/`format:check` 脚本与 5 个 devDependencies（eslint 10.11、eslint-plugin-vue 10.11、@vue/eslint-config-typescript 14.9、@vue/eslint-config-prettier 10.2、prettier 3.9；lockfile 已同步，CI 用 `npm ci` 可复现）；CI frontend job 增 `npm run lint`；③**修复 4 处 `any`**：`src/composables/lineupBoard.ts` 新增导出类型 `SlotDragEvent`（vuedraggable 事件对象的最小结构声明：`item.dataset.key`、`added.element`、`removed.element`），3 个拖拽处理函数与 `LineupEditor.vue` 的包装函数同步改类型；其余 10 处 props 变更属行为改动，按「不做未经验证的行为改动」原则降级为 warn 并登记为计划 W2-8；④`README.md` 补「Python 版本（3.11–3.13；3.14 因 `pydantic-core` 无 cp314 wheel 装不上）」实测说明。验证：**`npm run lint` → 0 error / 10 warning（exit 0）**；**`npm run build`（vue-tsc + vite）exit 0**，证明类型改动安全；ESLint 基线由 14 errors 降至 0。**未验证**：10 处 props 变更的修复（需浏览器验收，见 W2-8）；mypy 未引入 | 前端、代码规范、CI、文档 |
| 2026-10-02 | Wave 2 批次 6（合规化计划 W2-2 前端部分，**前端测试体系**）：①新增 `frontend/vitest.config.ts`（jsdom 环境、`src/**/*.spec.ts`、与 `vite.config.ts` 分离以免测试配置进入生产构建）；②新增 4 个 spec、共 **38 个用例**——`utils/constants.spec.ts`（常量取值完整性 + resultLabel 未知值原样返回 + resultType 分支）、`utils/profession.spec.ts`（职业色回退主色、深浅底字色、色表覆盖 11 职业）、`utils/scheduleSort.spec.ts`（以「相对今天」构造用例使跨天稳定：绝对距离升序、同距离未来优先、同侧时间序、不改入参、空数组安全）、`match-data/analysis.spec.ts`（fmtNum 万位折算、pctStr 除零、calcKDA 辅助折算含铁衣恒辅助与零死亡分母下限、resolveArchetype 含潮光/鸿音分路与破塔 0.7 折算、computeScores 不变量：单条记录且同组死亡均值相同→85 分、**无死亡 deathMult=0 不扣分**、全零指标→0 分、权重按 wsum 归一为 1、total 降序、入参不被修改、同引用命中 WeakMap 缓存）；③`package.json` 增 `test`/`test:watch` 与 `vitest@^3.2.7`+`jsdom` devDependencies；CI frontend job 增 `npm run test`；`tech-stack.md` 开发工具表同步。验证：**`npm run test` → 38 passed（4 文件，1.73s）exit 0**；`npm run lint` 仍 0 error / 10 warning；`npm run build`（vue-tsc）通过。**过程发现**：①vitest 5.x 的 peer 要求 `vite ^6.4/^7/^8` 而项目固定 vite 5.4 → npm ERESOLVE，改用 vitest 3.2.7（依赖版本对齐的现实证据）；②首轮 4 条用例失败**全部是我自己的假设错误**——工厂默认 `profession:'铁衣'` 属辅助型、且实现为「无死亡则 deathMult=0 不扣分」（比 `analysis.ts` 文档注释更合理），故修正用例而非改代码。**未验证**：CI 上的运行（需 push）；`selfcheck_indicators.py` 未改造；组件级/接口级用例未写（httpx 已装待用） | 前端、测试、CI、文档 |
| 2026-10-02 | Wave 2 批次 7（合规化计划 W2-6 部分，**出勤率口径收敛 + F-03 复核更正**）：①复核结论——出勤率**公式无重复实现**：唯一实现为 `backend/app/services/member_service.py:241`（`round(正常/(正常+请假), 4)`，无记录为 `null`，按出勤率升序且无记录排最后），前端 27 处 `attendance_rate` 命中全部是类型声明 / 读取 / 排序 / 展示，**并不重算**，原审计「口径散落 10 个文件」表述过重，已在计划 F-03 行更正并降级 P1→P2；②真实问题与修复——低出勤阈值 `0.5` 硬编码 4 处（`AttendanceRatePanel.vue` ×3、`MemberDetailHeader.vue` ×1）、百分比格式化 3 处且存在两种口径（`toFixed(1)` 与 `Math.round`）、另有组件内本地 `ratePercent()`；新增 `frontend/src/utils/attendance.ts`（`ATTENDANCE_LOW_THRESHOLD` / `isLowAttendance` / `attendanceProgressColor` / `formatRatePercent(rate, digits, fallback)`）作为前端唯一来源，**两种展示口径作为显式参数保留**（列表与详情 1 位小数、首页排行取整——属场景差异而非缺陷，已在模块注释与 spec 中写明并由用例守护）；③新增 `attendance.spec.ts` 6 用例（阈值边界 0.5 本身不告警、无记录不告警/回退文案、两种小数位、颜色分支）；④替换用脚本执行且**对每处替换断言期望命中次数**（4 / 3 / 1 全部匹配，避免静默失配），替换后逐行复核 diff。验证：**`npm run test` → 44 passed（5 文件，1.89s）exit 0**；`npm run lint` 0 error / 10 warning；`npm run build`（vue-tsc）exit 0。**未完成**：F-04（`config.py` 导入期副作用）待处理；展示口径改动未做浏览器验收（数值语义不变） | 前端、单一权威源、文档 |
| 2026-10-02 | Wave 2 批次 8（合规化计划 W2-6 收尾，**F-04 修复**）：弱密钥启动门禁由 `app/core/config.py` **导入期**移至**应用启动期**。改造前的危害：`config.py` 模块级调用 `_validate_secret_key()`，而 `alembic/env.py`、测试收集、一次性脚本等非服务场景都会导入 config → 生产环境下仅 import 配置就被 `sys.exit(1)` 终止，且门禁本身无法被测试（既有用例只能覆盖纯判定函数）。改造后：`config.py` 新增 `InsecureSecretKeyError` 与文案常量（`FATAL_SECRET_KEY_MESSAGE` **原文逐字保留**、`WEAK_SECRET_KEY_WARNING`）、`validate_secret_key()`（生产弱密钥抛异常、开发仅告警、通过返回 None）、`enforce_secret_key()`（打印 FATAL + `sys.exit(1)`），并移除模块级调用；`app/main.py` 新增 `startup_checks()` 并在 `on_startup` 首要位置调用（先过门禁，再起审计日志清理任务）。目录创建（`DATA_DIR` / `LOG_DIR`）**刻意保留在导入期**——幂等、不中止进程，且被 `logging_config` 与 SQLite 路径在导入期依赖，理由写在 `config.py` 末尾。`backend/tests/test_config_gate.py` 由 9 → **15 用例**：子进程回归 2 条（生产弱密钥下**仅导入 config → exit 0 且无 FATAL**；调用 `enforce_secret_key()` → 非零退出 + FATAL 文案）、校验函数 4 条（生产弱密钥抛 `InsecureSecretKeyError` 且含 FATAL / 生产强密钥放行 / 开发弱密钥仅 WARNING / `enforce` 退出码为 1）、启动接线 2 条（需 FastAPI，本地缺依赖自动 skip，CI 执行）。**同时修掉一处将导致 CI 变红的既有问题**：`tests/test_permissions.py` 未使用的 `unittest` 导入（`ruff check .` 报 F401；第 7 轮「先跑 ruff、后写测试」的顺序导致当时未暴露），教训记入 ai-checklist 第 28 条。验证：`python -m ruff check .` → **All checks passed!**；`python -m compileall -q app scripts alembic` exit 0；`python -m pytest tests/test_config_gate.py tests/test_member_names.py` → **20 passed + 2 skipped**。**未验证**：需 FastAPI 的启动接线用例与全量后端套件（本地 3.14 装不了 pydantic-core；由 CI 3.11 覆盖）；uvicorn lifespan 路径下的具体退出码（推断为非零，未实跑容器） | 后端、安全、可测试性、CI |
| 2026-10-02 | Wave 3 批次 1（合规化计划 W3-4 部分 / W4-4）**新增 4 份根文档**：`CHANGELOG.md`（Keep a Changelog 1.1.0；`[未发布]` 汇总本轮改动，v1.0.0/v1.1.0/v1.2.0 由 `git log` 归并并标注依据，比较链接用真实仓库 URL，记录 `package.json` 版本不一致待 D-4）、`CONTRIBUTING.md`（摘要 + 权威源链接 + 与 CI 对应的本地门禁命令）、`SECURITY.md`（支持版本 / GitHub 私有安全公告渠道 / 处理时限目标 / 已知接受风险引用权威源）、`CODE_OF_CONDUCT.md`（Contributor Covenant 2.1 官方中文译本）；`AGENTS.md` §2.2、`architecture.md`（§23 + 目录树 + 更新记录）与 `README.md` 同步登记。**同时修正本文件代码目录树的滞后**（AGENTS.md §3.3 第 3 条要求两个目录树都检查）：补 `.editorconfig`、`.gitattributes`、`.githooks/`、`.github/`、`scripts/`、`backend/{pytest.ini,ruff.toml,requirements-dev.txt,tests/}`、`frontend/{eslint.config.js,.prettierrc.json,vitest.config.ts,nginx.conf.example}`；更正 `deploy.sh` → `deploy.sh.example`（可执行脚本已被忽略）、`nginx.conf`（内层反代，非边界层）、`utils/`（补 profession/attendance 与单测）三处失实说明 | CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, AGENTS.md, README.md, architecture.md, progress.md |

---

## 使用说明

1. **代码变更后**：必须更新本文档的"代码模块说明"部分
2. **新增模块**：在对应表格中添加模块信息
3. **完成阶段**：更新"开发进度"状态

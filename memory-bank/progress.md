# 项目进度与代码结构

## 代码目录结构

```
nsh-management/
├── backend/                   # 后端项目（FastAPI）
│   ├── app/
│   │   ├── api/               # API 路由（v1/ 路由注册 + deps 依赖注入）
│   │   ├── core/              # 配置、数据库、安全（JWT/密码）
│   │   ├── models/            # 10 张表 SQLAlchemy 模型（含 squad_adjustments）
│   │   ├── schemas/           # Pydantic 数据模型
│   │   ├── services/          # 业务逻辑（auth/config/lineup/member/recording/attendance/match_data/schedule/squad_adjustment）
│   │   ├── utils/             # 工具函数（attendance_import/excel_import/constants）
│   │   ├── init_db.py         # 初始化默认帮会与账号（开发者/admin/member）
│   │   └── main.py            # 应用入口（CORS/异常处理/AuthError锁定秒数）
│   ├── alembic/               # 数据库迁移（9 个版本）
│   ├── data/                  # SQLite 数据库（nsh.db）
│   ├── docs/README.md         # 后端模块开发文档
│   ├── scripts/               # 工具脚本
│   │   ├── generate_import_template.py  # 生成成员导入模板
│   │   └── selfcheck_indicators.py      # 衍生指标自检脚本
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
│   │   │   ├── attendance/    # 出勤库（AttendanceTab/FillerDialog/ImportMemberDialog/LeaveImportDialog/SubstituteImportDialog）
│   │   │   ├── lineups/       # 排表（LineupEditor/LineupTab/ImportHistoryDialog/MatchConfirmDialog）
│   │   │   ├── match-data/    # 数据分析（MatchDataTab/OverviewTab/IndicatorsTab/RankingTab/CampCompareTab/SquadAnalysisTab/ProfessionTab/ProfessionDetailTab/ScoreTab/CampCompare/PlayerAnalysis/MetricsGuideDialog/EChart/analysis.ts/chartTheme.ts）
│   │   │   ├── members/       # 常驻库（AttendanceRatePanel/MemberFormDialog/MemberImportDialog/ProfessionShortage）
│   │   │   ├── recording/     # 录屏审核（RecordingTab）
│   │   │   └── schedules/     # 联赛日程（ScheduleCalendar）
│   │   ├── composables/       # 组合式函数（lineupBoard）
│   │   ├── layouts/           # 主布局（深檀侧边栏208px+宣纸顶栏62px，支持折叠64px）
│   │   ├── router/            # 路由与守卫
│   │   ├── stores/            # Pinia（auth）
│   │   ├── styles/            # 浅色雅金风主题（theme.css 令牌 / element-plus.css 组件 / index.css 入口）
│   │   ├── types/             # TS 类型定义（attendance/auth/config/lineup/matchData/member/recording/schedule）
│   │   ├── utils/             # 工具函数（constants/scheduleSort）
│   │   └── views/             # 页面
│   │       ├── HomeView.vue           # 首页仪表盘
│   │       ├── LoginView.vue          # 登录页（含锁定倒计时）
│   │       ├── config/ConfigView.vue  # 系统配置（职业/账号/帮会管理）
│   │       ├── members/MemberListView.vue  # 常驻库
│   │       └── schedules/             # 联赛日程
│   │           ├── ScheduleListView.vue      # 日程列表
│   │           ├── ScheduleDetailView.vue    # 赛程详情（出勤/排表/录屏/分析 Tab）
│   │           └── LeagueOverviewView.vue    # 帮众联赛总览
│   ├── Dockerfile             # 前端容器镜像（多阶段构建）
│   ├── .dockerignore
│   ├── nginx.conf             # Nginx 配置（静态托管+API反代+SPA回退+HTTPS）
│   ├── docs/README.md         # 前端模块开发文档
│   └── package.json
├── memory-bank/                # 项目文档
│   ├── architecture.md         # 文档索引
│   ├── data-analysis-complete.md # 数据分析模块完整方案
│   ├── database-design.md      # 数据库设计文档（v1.5）
│   ├── design-document-v2.md   # 产品设计文档（当前主文档）
│   ├── implementation-plan.md  # 实施方案文档
│   ├── progress.md             # 本文档 - 代码结构与进度
│   ├── security-review.md      # 安全审查文档
│   ├── tech-stack.md           # 技术栈文档
│   └── ui-style-guide.md       # UI风格参考文档
├── start.bat                   # 一键启动脚本（前后端+首次建库）
├── deploy.sh                   # Linux 部署脚本（Docker Compose 一键部署）
├── docker-compose.yml          # Docker Compose 编排（Nginx + FastAPI + SQLite 卷）
├── .env.example                # 部署环境变量模板（复制为 .env 填写）
├── DEPLOY.md                   # 部署文档（Docker Compose 全流程）
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
| 样式系统 | src/styles/ | 浅色雅金风主题（theme.css + element-plus.css + index.css） | ✅ 已完成 |

### 后端模块

| 模块 | 路径 | 作用 | 状态 |
|------|------|------|------|
| 基础框架 | app/core | 配置（JWT 10h）、异步数据库、JWT/密码 | ✅ 已完成 |
| 数据模型 | app/models | 10 张表 SQLAlchemy 模型 + 9 个 Alembic 迁移 | ✅ 已完成 |
| 认证模块 | app/api/v1/auth.py | 登录/登出/me + 登录限流（含未知账号锁定） | ✅ 已完成 |
| 常驻库 API | app/api/v1/members.py | CRUD/筛选/批量删/Excel导入/出勤率/职业统计 | ✅ 已完成 |
| 联赛日程 API | app/api/v1/schedules.py | CRUD/时间范围/级联创建删除 | ✅ 已完成 |
| 出勤库 API | app/api/v1/attendance.py | 导入成员/替补/补人/请假导入/状态/保存/职业切换 | ✅ 已完成 |
| 排表 API | app/api/v1/lineups.py | 候选池/读写/保存校验/规范化/导入历史/备注 | ✅ 已完成 |
| 录屏审核 API | app/api/v1/recording.py | 提交/审核/批量审核/进度 | ✅ 已完成 |
| 数据分析 API | app/api/v1/match_data.py | CSV导入/6榜排行/职业17项统计/16项衍生指标/阵营对比/小队分析 | ✅ 已完成 |
| 分析调整 API | app/api/v1/squad_adjustments.py | 小队分析内未排表成员→目标队伍的临时分配（仅作用于分析视图，不改正式排表） | ✅ 已完成 |
| 开发者 API | app/api/v1/developer.py | 开发者专属路由（帮会管理/账号管理等） | ✅ 已完成 |
| 系统配置 API | app/api/v1/config.py | 职业配置/账号管理/帮会管理（开发者）/删除帮会/删除账号 | ✅ 已完成 |
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

---

## 使用说明

1. **代码变更后**：必须更新本文档的"代码模块说明"部分
2. **新增模块**：在对应表格中添加模块信息
3. **完成阶段**：更新"开发进度"状态

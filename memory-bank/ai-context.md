# AI 项目完整上下文文档

> 本文件是项目根目录 `AGENTS.md` 的完整扩展版，供 AI 助手深入了解项目全貌。
> 根目录 `AGENTS.md` 提供规范、文档维护与流程速查，本文档提供完整上下文。

---

## 1. 项目概述

**轻衫都会用的帮会联赛管理系统** — 专为逆水寒游戏帮会管理人员设计的一体化管理工具。

### 1.1 产品定位
涵盖成员管理、出勤考核、联赛排表、录屏审核和比赛数据分析等核心功能。目标用户为游戏帮会的管理团队。

### 1.2 功能模块（全部已完成 ✅）

| 模块 | 核心功能 | 后端入口 | 前端入口 |
|------|---------|---------|---------|
| 常驻库 | 成员 CRUD、Excel 批量导入、职业/状态筛选、出勤率统计 | `api/v1/members.py` | `views/members/MemberListView.vue` |
| 出勤库 | 一键导入正式成员、批量导入请假、替补/补人管理、职业缺口分析 | `api/v1/attendance.py` | `components/attendance/AttendanceTab.vue` |
| 联赛排表 | 拖拽编排 10 队 × 6 人、候选池按职业分组、导入历史排表、自动保存、导出 PNG | `api/v1/lineups.py` | `components/lineups/LineupEditor.vue` |
| 录屏审核 | 多局链接提交、审核/批量审核、进度统计、链接脱敏 | `api/v1/recording.py` | `components/recording/RecordingTab.vue` |
| 数据分析 | CSV 导入、ECharts 8 Tab 可视化、16 项衍生指标 | `api/v1/match_data.py` | `components/match-data/MatchDataTab.vue` |
| 分析调整 | 小队分析内手动分配未排表成员到目标队伍 | `api/v1/squad_adjustments.py` | `components/match-data/SquadAnalysisTab.vue` |
| 系统配置 | 职业配置、账号管理、帮会管理（开发者专属） | `api/v1/config.py` | `views/config/ConfigView.vue` |
| 联赛日程 | 日历视图、赛程 CRUD、级联创建/删除、帮众联赛总览 | `api/v1/schedules.py` | `views/schedules/ScheduleListView.vue` |
| 个人战绩 | 按游戏 ID 聚合历史比赛数据（单局指标与排名、个人概览） | `api/v1/my_stats.py` | `views/member/MyStatsView.vue` |
| 游戏 ID 改名 | 帮众提交改名申请、管理员审核（通过即同事务同步常驻库并建立新旧 ID 关联） | `api/v1/game_id_requests.py` | `views/member/GameIdChangeView.vue` |
| 系统日志 | 操作审计日志查询/统计/清理（仅开发者） | `api/v1/logs.py` | `views/logs/LogView.vue` |

### 1.3 三级角色权限

```
developer（开发者）→ 不绑定帮会，全局管理
    ├── 创建/删除帮会
    ├── 创建/删除账号（全局）
    ├── 职业配置
    └── 系统日志（操作审计）

admin（管理员）→ 绑定帮会，帮会内全部权限
    ├── 成员 CRUD、出勤管理、排表编辑
    ├── 录屏审核、CSV 导入分析
    ├── 分析调整
    └── 本帮会账号管理

member（帮众）→ 绑定帮会，只读 + 有限操作
    ├── 提交录屏链接（录屏上传 / 联赛总览）
    ├── 查看个人战绩
    ├── 查看联赛日程（列表 + 详情：录屏/数据分析只读）
    └── 出勤库、排表仅管理员可见
```

### 1.4 数据模型（13 张表）

> **权威源**：`database-design.md` §1.2（表清单与关联关系）、§2（字段级设计）。核心结构：`guilds` 下挂 users / profession_configs / members / schedules；`schedules` 1:N 关联 attendance_records / recordings / match_data，1:1 关联 lineups / squad_adjustments；operation_logs 独立记录全局操作审计（guild_id 可空）；professions 为全局职业目录（无 guild_id，开发者维护）。

---

## 2. 技术栈

> **权威源**：`tech-stack.md`（含完整版本表、requirements.txt、项目结构、部署方案）
>
> 本节仅列出关键信息摘要，详细版本号和依赖列表请查阅权威源。

- 前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts 6 + Pinia + vuedraggable + html2canvas
- 后端：Python 3.11（生产基座/CI）+ FastAPI 0.142.2（锁定） + SQLAlchemy 2.0.36 + SQLite + Pydantic 2.11.4 + Alembic 1.13.1
- 部署：Docker Compose 编排（前端 Nginx:80 + 后端 FastAPI:8000），SQLite 数据卷持久化，Nginx 反向代理 + SPA 回退 + HTTPS

---

## 3. 编码规范

> **权威源**：`.agent/rules/file-length-rule.md`（行数限制）、`ui-style-guide.md`（UI 规范）

### 3.1 文件行数限制

**强制上限**：Vue 组件 300 行 / Python 服务 300 行 / 工具函数 200 行 / 路由 150 行；超限必须拆分（子组件、composable、拆服务），连续逻辑文件可按规则文件的「行数豁免」机制标记保留。

> **权威源**：`.agent/rules/file-length-rule.md`（建议行数、触发条件、拆分策略）。

### 3.2 前端代码规范

> **权威源**：`progress.md`（完整代码目录树）。

- `api/`：每个业务模块一个 API 文件（`http.ts` 为基础封装）
- `components/`：按功能模块分子目录（attendance / lineups / match-data / members / my-stats / recording / schedules / common）
- `views/`：页面级组件（HomeView / LoginView + config / logs / member / members / schedules 子目录）
- `composables/`、`stores/`、`types/`、`utils/`：组合式函数 / Pinia / 类型 / 通用工具（如 `profession.ts` 职业色、`constants.ts` 结果映射）
- `styles/`：`theme.css`（设计令牌）+ `element-plus.css`（组件深度定制）+ `index.css`（全局入口）

**UI 风格**：浅色雅金风（宣纸鎏金）
- 页面背景：`#F7F3EA`（宣纸米白）
- 主色：鎏金渐变 `#F2DFA0 → #D9B64A → #C9A13B`
- 侧边栏：深檀色
- 职业色映射：每个职业有独立配色（见 `ui-style-guide.md`）

### 3.3 后端代码规范

> **权威源**：`progress.md`（完整代码目录树）。

- `api/v1/`：薄路由层（`router.py` 注册汇总、`deps.py` 依赖注入，各模块路由只做参数校验与调用 service）
- `core/`：`config.py` 环境配置 / `database.py` 异步连接 / `security.py` JWT 与密码 / `logging_config.py` 日志
- `models/`、`schemas/`：SQLAlchemy 表模型（13 张表）与 Pydantic 请求/响应模型
- `services/`：业务逻辑核心（含 log / my_stats / lineup_attendance 等）
- `utils/`：Excel/出勤导入、图片与 Excel 导出、常量、姓名规范化
- `init_db.py` / `main.py`：默认账号初始化与应用入口（CORS、审计中间件、异常处理）

**分层原则**：
- `api/v1/` → 薄路由层，参数校验 + 调用 service + 返回响应
- `services/` → 业务逻辑核心，数据库操作
- `models/` → 表结构定义
- `schemas/` → 请求/响应数据结构

### 3.4 数据库规范

- SQLite 单文件存储（`backend/data/nsh.db`）
- SQLAlchemy 异步模式（`aiosqlite` 驱动）
- Alembic 管理迁移（`backend/alembic/versions/`，当前 16 个版本，head `p0q1r2s3t4u5`）
- 多帮会隔离：核心表通过 `guild_id` 字段隔离数据
- JSON 字段：排表（60 槽位）、局数结果、比赛数据扩展列、分析调整

---

## 4. Git 工作流

> **权威源**：`GIT-GUIDE.md`（完整分支策略、提交规范、版本发布、镜像远端同步（可选））

- 分支：`main`（始终可发布）+ `feature/<功能名>` + `hotfix/<描述>`
- 提交：`<type>(<scope>): <中文摘要>`，scope 必填
- 合并：`--no-ff`
- 远端：`origin`（GitHub）为唯一权威远端；镜像（如 Gitee）可选

---

## 5. 文档体系

> **权威源**：`AGENTS.md` §2–§3（文档维护规范、同步与进度追踪流程）、`architecture.md`（完整文档索引 + 目录树 + 更新记录）

所有项目文档在 `memory-bank/` 目录下，统一小写 kebab-case 命名。文档更新流程（改代码 → progress、改文档 → architecture、新增 → 索引）以 `AGENTS.md` §3 为准。

---

## 6. 安全要点

> **权威源**：`security-review.md`（完整审查结论与改进项）

**已实施**：JWT + 角色权限、登录限流 5 次/5 分钟、bcrypt、Excel 5MB 限制、Nginx 速率限制、DEBUG 控制异常输出、Token 版本控制

**已知接受风险**：`users.plain_password` 明文存储（API 层限制）、localStorage Token、共享帮众账号、进程内存锁定

---

## 7. 开发环境启动

> **详见**：`README.md` §快速开始

```bash
# 后端：cd backend → python -m venv .venv → pip install → alembic upgrade head
# 前端：cd frontend → npm install
# 一键：start.bat（Windows，自动迁移+初始化+启动）
```

---

## 8. 已知待优化项

### 8.1 代码行数超标（2026-09-15 已完成拆分治理）
- 原 28 个超限文件：**15 个已拆分**（全部达标，2026-09-15 复测最大文件 299 行）、**13 个连续逻辑豁免**（文件头「行数豁免」标记 + `.agent/rules/file-length-rule.md` 豁免清单登记）
- 拆分手法：子组件 / composable / 图表 option 模块外移；样式随组件迁移，跨组件共享样式经 `<style scoped src>` 复用
- 后续新增代码再超限时，按规则文件的「拆分 / 豁免」机制处理（豁免必须打标记并登记）

### 8.2 安全加固（2026-09-28 起陆续落地；2026-10-09 复核）
- 生产弱密钥启动门禁**已实施**（`config.py` 启动期校验：弱密钥拒绝启动、低熵 hex 亦拒绝；`DEPLOY.md` §六 含部署前核对命令）——原「`SECRET_KEY` 默认值应改为未设置时报错退出」由该门禁承接
- 生产 `.env` 强随机密钥：部署文档已强制要求（`openssl rand -hex 32`），服务器当前密钥已按此执行
- `deploy.sh.example`（入库模板）使用 `ssh/scp -i` 密钥方式，**不含** `StrictHostKeyChecking=no`；本地 `deploy.sh`（不入库）由部署者自行维护

### 8.3 UI 优化（2026-09-18 全部完成；数字滚动、表格密度切换 2026-10-09 取消）
> **权威源**：`ui-polish-plan.md`（已全部完成归档）；最终规范见 `ui-style-guide.md` §10。

已完成：卡片层级、按钮扫光加宽、菜单 hover 过渡、动画族（stat-pop/card-slide）、奖牌微光、弹窗金线、滚动条配色、槽位放入反馈、保存成功动效、路由过渡、职业色与结果类型统一、空状态 SVG 插画（EmptyState 4 变体）、职业标签 hover 微光。原「数字滚动」项已按用户要求取消（2026-10-09：全站移除数字滚动动画，统计卡改为直接显示数值，useCountUp 已删除）；原「表格密度切换」项同为按用户要求取消（2026-10-09：顶栏密度按钮、useTableDensity.ts 与 element-plus.css 紧凑档规则已删除）。

### 8.4 出勤库 60 人上限漏洞（2026-09-15 用户决策：暂不修复，遗留记录在案）
- 现象：`update_status` / `batch_update_status`（请假 → 正常）不校验上限，正常人数可超过 60；已用内存库复现（60 正常 + 请假起步：单条切换变 61、批量切换变 63）
- 触发路径：先给成员请假腾名额 → 添加补人/导入至 60 → 再把请假成员切回正常（行内开关或「批量正常」）
- 已正确拦截的路径（对照）：添加补人、一键导入正式、导入成员、导入替补均调用 `check_normal_capacity`
- 位置：`backend/app/services/attendance_service.py` 的 `update_status`、`batch_update_status`
- 已定修复方案（待实施）：目标为 normal 且原状态非 normal 时调用 `check_normal_capacity`（批量按「原状态非正常且目标为正常」的增量计算）；切换失败时前端刷新数据回滚开关视觉状态
- 残余风险：两个标签页并发操作存在先读后写窗口，彻底解决需事务级串行化

### 8.5 近期新增功能（2026-09-17 已实施）

- 成员详情战绩页（管理员从常驻库进入 `/members/:id`：基本信息 + 出勤率 + 历史战绩；管理员开放「个人战绩」菜单）
- 单场图文战报（数据分析页一键生成 PNG 供群内分享；周报/汇总报告为二期）
- 方案与决策记录见 `stats-report-plan.md`


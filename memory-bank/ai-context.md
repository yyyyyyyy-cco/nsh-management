# AI 项目完整上下文文档

> 本文件是项目根目录 `CLAUDE.md` 的完整扩展版，供 AI 助手深入了解项目全貌。
> 根目录 `CLAUDE.md` 提供精简速查，本文档提供完整上下文。

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

### 1.3 三级角色权限

```
developer（开发者）→ 不绑定帮会，全局管理
    ├── 创建/删除帮会
    ├── 创建/删除账号（全局）
    └── 职业配置

admin（管理员）→ 绑定帮会，帮会内全部权限
    ├── 成员 CRUD、出勤管理、排表编辑
    ├── 录屏审核、CSV 导入分析
    ├── 分析调整
    └── 本帮会账号管理

member（帮众）→ 绑定帮会，只读 + 有限操作
    ├── 查看出勤/排表总览/录屏/数据分析
    ├── 切换自己出勤状态（正常/请假）
    └── 提交录屏链接
```

### 1.4 数据模型（10 张表）

```
guilds（帮会）
 ├── users（账号）                    guild_id
 ├── profession_configs（职业配置）    guild_id
 ├── members（常驻库成员）            guild_id
 └── schedules（赛程）               guild_id
     ├── attendance_records（出勤）   schedule_id, member_id
     ├── lineups（排表 JSON）         schedule_id（1:1）
     ├── recordings（录屏）           schedule_id, member_id
     ├── match_data（比赛数据）       schedule_id
     └── squad_adjustments（分析调整） schedule_id（1:1）
```

---

## 2. 技术栈

> **权威源**：`tech-stack.md`（含完整版本表、requirements.txt、项目结构、部署方案）
>
> 本节仅列出关键信息摘要，详细版本号和依赖列表请查阅权威源。

- 前端：Vue 3 + TypeScript + Vite + Element Plus + ECharts 6 + Pinia + vuedraggable + html2canvas
- 后端：Python 3.13 + FastAPI 0.115+ + SQLAlchemy 2.0.36 + SQLite + Pydantic 2.11.4 + Alembic 1.13.1
- 部署：Docker Compose 编排（前端 Nginx:80 + 后端 FastAPI:8000），SQLite 数据卷持久化，Nginx 反向代理 + SPA 回退 + HTTPS

---

## 3. 编码规范

> **权威源**：`.claude/rules/file-length-rule.md`（行数限制）、`ui-style-guide.md`（UI 规范）

### 3.1 文件行数限制

| 文件类型 | 建议行数 | 强制上限 | 说明 |
|---------|---------|---------|------|
| Vue 组件 (.vue) | 100-200 | **300** | 超限必须拆分为子组件或 composable |
| Python 服务 (services/*.py) | 100-200 | **300** | 超限必须拆分为多个服务或工具模块 |
| 工具函数 (utils/*.py/ts) | 50-150 | **200** | 按功能模块拆分 |
| 路由文件 (router/*.ts) | 50-100 | **150** | — |

**拆分触发条件**：
- 行数超过强制上限
- 包含 3 个以上不相关的功能
- 出现多个独立的业务逻辑块

### 3.2 前端代码规范

```
frontend/src/
├── api/              # 每个业务模块一个 API 文件（http.ts 为基础封装）
├── components/       # 按功能模块分子目录（attendance/lineups/match-data/members/recording/schedules）
│   └── match-data/   # 每个 Tab 独立组件 + 共享工具（analysis.ts/chartTheme.ts/EChart.vue）
├── views/            # 页面级组件（HomeView/LoginView + 按模块分子目录）
├── composables/      # 组合式函数（可复用逻辑）
├── stores/           # Pinia store（按领域拆分）
├── types/            # TypeScript 类型定义（按模块拆分）
├── styles/           # 主题系统
│   ├── theme.css     # 设计令牌（CSS 变量）
│   ├── element-plus.css  # Element Plus 深度定制
│   └── index.css     # 全局样式入口
└── utils/            # 通用工具函数
```

**UI 风格**：浅色雅金风（宣纸鎏金）
- 页面背景：`#F7F3EA`（宣纸米白）
- 主色：鎏金渐变 `#F2DFA0 → #D9B64A → #C9A13B`
- 侧边栏：深檀色
- 职业色映射：每个职业有独立配色（见 `ui-style-guide.md`）

### 3.3 后端代码规范

```
backend/app/
├── api/v1/           # 路由层（薄层，只做参数校验和调用 service）
│   ├── router.py     # 路由注册汇总
│   ├── deps.py       # 依赖注入（get_current_user, require_admin）
│   └── [模块].py     # 各模块路由
├── core/             # 基础设施
│   ├── config.py     # 环境变量配置（Settings 类）
│   ├── database.py   # 异步数据库连接
│   └── security.py   # JWT + 密码加密
├── models/           # SQLAlchemy 模型（10 张表）
├── schemas/          # Pydantic Schema（请求/响应模型）
├── services/         # 业务逻辑层（核心代码）
├── utils/            # 工具函数（Excel 导入、出勤导入、常量）
├── init_db.py        # 初始化默认账号（仅空库时执行）
└── main.py           # 应用入口（CORS、异常处理）
```

**分层原则**：
- `api/v1/` → 薄路由层，参数校验 + 调用 service + 返回响应
- `services/` → 业务逻辑核心，数据库操作
- `models/` → 表结构定义
- `schemas/` → 请求/响应数据结构

### 3.4 数据库规范

- SQLite 单文件存储（`backend/data/nsh.db`）
- SQLAlchemy 异步模式（`aiosqlite` 驱动）
- Alembic 管理迁移（`backend/alembic/versions/`，当前 9 个版本）
- 多帮会隔离：核心表通过 `guild_id` 字段隔离数据
- JSON 字段：排表（60 槽位）、局数结果、比赛数据扩展列、分析调整

---

## 4. Git 工作流

> **权威源**：`GIT-GUIDE.md`（完整分支策略、提交规范、版本发布、双远程同步）

- 分支：`main`（始终可发布）+ `feature/<功能名>` + `hotfix/<描述>`
- 提交：`<type>(<scope>): <中文摘要>`，scope 必填
- 合并：`--no-ff`
- 双远程：`origin`（GitHub）+ `gitee`（Gitee）同步推送

---

## 5. 文档体系

> **权威源**：`architecture.md`（完整文档索引 + 目录树 + 更新记录）

所有项目文档在 `memory-bank/` 目录下，统一小写 kebab-case 命名。

**更新铁律**：
1. 改代码 → 更新 `progress.md`
2. 改文档 → 更新 `architecture.md`
3. 新增文档 → 在 `architecture.md` 添加索引

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

### 8.1 代码行数超标（21 个文件超硬限制）
- 热点区域：`frontend/src/components/match-data/`（8 个超限组件）
- 最大文件：`SquadAnalysisTab.vue`（1270 行）、`HomeView.vue`（1017 行）、`LineupEditor.vue`（968 行）
- 后端最大：`match_data_service.py`（577 行）
- 建议在"阶段 8：测试与优化"中逐步拆分

### 8.2 安全加固待办
- `config.py` 的 `SECRET_KEY` 默认值应改为未设置时报错退出
- 生产 `.env` 应使用强随机密钥（`openssl rand -hex 32`）
- `deploy.sh` 中 `StrictHostKeyChecking=no` 应移除

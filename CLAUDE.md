# CLAUDE.md — AI 项目入门指南

> 本文件为 AI 助手提供项目上下文。首次接触本项目时请完整阅读。

## 项目简介

**轻衫都会用的帮会联赛管理系统** — 专为逆水寒游戏帮会管理人员设计的一体化管理工具。

核心功能：常驻库、出勤库、联赛排表（拖拽 10 队 × 6 人）、录屏审核、数据分析（ECharts 8 Tab）、分析调整、系统配置、联赛日程。

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vue 3 + TypeScript + Vite + Element Plus + ECharts 6 + Pinia |
| 后端 | Python 3.13 + FastAPI + SQLAlchemy + SQLite + Alembic |
| 部署 | Docker Compose + Nginx |

## 三级角色

| 角色 | 说明 |
|------|------|
| developer | 不绑定帮会，全局管理（创建帮会/派发账号/删除帮会） |
| admin | 绑定帮会，帮会内全部功能权限 |
| member | 绑定帮会，查看数据 + 提交录屏 |

## 关键约定

### 开发前必读
1. **产品设计**：`memory-bank/design-document-v2.md`（功能定义、权限矩阵、页面结构）
2. **数据库设计**：`memory-bank/database-design.md`（10 张表、v1.6）
3. **技术栈**：`memory-bank/tech-stack.md`（依赖版本、项目结构）
4. **UI 规范**：`memory-bank/ui-style-guide.md`（浅色雅金风 / 宣纸鎏金主题）

### 代码规范
- **Vue 组件**：建议 100-200 行，硬限 300 行
- **Python 服务**：建议 100-200 行，硬限 300 行
- **工具函数**：建议 50-150 行，硬限 200 行
- 超限时必须拆分，按功能模块组织

### Git 提交规范
- 格式：`<type>(<scope>): <中文摘要>`
- 类型：`feat` / `fix` / `docs` / `style` / `refactor` / `perf` / `test` / `chore` / `ci`
- 摘要必须中文，50 字以内
- 范围（scope）必填，根据变更路径推断

### 文档更新规则
- 更新代码后必须同步 `memory-bank/progress.md`
- 更新文档后必须同步 `memory-bank/architecture.md`（文档索引）

### 分支策略
- `main` 始终可发布，不在 main 上直接开发
- 功能分支：`feature/<功能名>`，修复分支：`hotfix/<描述>`
- 合并使用 `--no-ff`
- 双远程同步：`origin`（GitHub）+ `gitee`（Gitee）

## 项目结构速览

```
nsh-management/
├── backend/                    # FastAPI 后端
│   └── app/
│       ├── api/v1/             # 路由（auth/members/schedules/attendance/lineups/recording/match_data/squad_adjustments/config/developer）
│       ├── core/               # 配置/数据库/安全
│       ├── models/             # 10 张表 SQLAlchemy 模型
│       ├── schemas/            # Pydantic Schema
│       ├── services/           # 业务逻辑（9 个服务）
│       └── utils/              # 工具函数
├── frontend/                   # Vue 3 前端
│   └── src/
│       ├── api/                # Axios 封装（10 个模块）
│       ├── components/         # 业务组件（6 个子目录）
│       ├── views/              # 页面
│       ├── stores/             # Pinia 状态
│       ├── styles/             # 浅色雅金风主题（theme.css / element-plus.css / index.css）
│       └── types/              # TypeScript 类型
├── memory-bank/                # 项目文档（9 个 .md）
├── .claude/rules/              # AI 编码规则
└── docker-compose.yml          # Docker 部署编排
```

## 详细文档索引

完整文档结构与说明见 `memory-bank/architecture.md`。
本文档的完整扩展版见 `memory-bank/ai-context.md`（含数据模型、编码规范细节、安全要点、待优化项）。

| 文档 | 路径 | 一句话说明 |
|------|------|-----------|
| 产品设计 | `memory-bank/design-document-v2.md` | 功能定义、权限、页面结构、API 接口 |
| 数据库设计 | `memory-bank/database-design.md` | 10 张表结构、字段约束、业务规则 |
| 技术栈 | `memory-bank/tech-stack.md` | 依赖版本、项目结构、部署方案 |
| UI 规范 | `memory-bank/ui-style-guide.md` | 浅色雅金风色彩/字体/组件/布局规范 |
| 实施方案 | `memory-bank/implementation-plan.md` | 任务分解、模块依赖、阶段规划 |
| 项目进度 | `memory-bank/progress.md` | 代码目录结构、模块状态、变更记录 |
| 数据分析方案 | `memory-bank/data-analysis-complete.md` | CSV 结构、16 项衍生指标、ECharts 图表 |
| 安全审查 | `memory-bank/security-review.md` | 安全审查结论与改进项 |
| 部署文档 | `DEPLOY.md` | Docker Compose 部署全流程 |
| Git 规范 | `GIT-GUIDE.md` | 分支/提交/发布/tag/双远程同步 |
| 后端开发文档 | `backend/docs/README.md` | 后端模块需求、开发计划、进度 |
| 前端开发文档 | `frontend/docs/README.md` | 前端模块需求、开发计划、进度 |

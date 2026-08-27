# CLAUDE.md — AI 项目入门指南

> 本文件为 AI 助手提供项目上下文。首次接触本项目时请完整阅读。

## 项目简介

**轻衫都会用的帮会联赛管理系统** — 专为逆水寒游戏帮会管理人员设计的一体化管理工具。

核心功能：常驻库、出勤库、联赛排表（拖拽 10 队 × 6 人）、录屏审核、数据分析（ECharts 8 Tab）、分析调整、系统配置、联赛日程。

技术栈：Vue 3 + TS + Vite + Element Plus + ECharts 6 + Pinia / Python 3.13 + FastAPI + SQLAlchemy + SQLite / Docker Compose + Nginx（详见 `memory-bank/tech-stack.md`）

角色：developer（全局管理）、admin（帮会全部权限）、member（查看+提交录屏）（详见 `memory-bank/design-document-v2.md` §3）

## 关键约定

### 操作前必读
> ⚠️ **每次修改文档或代码前，先读 `memory-bank/ai-checklist.md`** — 记录了所有犯过的错误和容易遗漏的联动点。

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
- 格式：`<type>(<scope>): <中文摘要>`，摘要中文 50 字以内，scope 必填
- 详见 `GIT-GUIDE.md`

### 文档更新规则
- 更新代码后必须同步 `memory-bank/progress.md`
- 更新文档后必须同步 `memory-bank/architecture.md`（文档索引）
- 完整文档结构与目录树见 `memory-bank/architecture.md`（文档视角）和 `memory-bank/progress.md`（代码视角）

### 分支策略
- `main` 始终可发布，不在 main 上直接开发
- 功能分支：`feature/<功能名>`，修复分支：`hotfix/<描述>`
- 合并使用 `--no-ff`
- 双远程同步：`origin`（GitHub）+ `gitee`（Gitee）

## 文档索引

> 完整文档结构与说明见 `memory-bank/architecture.md`。
> 完整扩展版（含数据模型、安全要点、待优化项）见 `memory-bank/ai-context.md`。

| 文档 | 路径 | 一句话说明 |
|------|------|-----------|
| 产品设计 | `memory-bank/design-document-v2.md` | 功能定义、权限、页面结构 |
| 数据库设计 | `memory-bank/database-design.md` | 10 张表、字段约束、业务规则 |
| 技术栈 | `memory-bank/tech-stack.md` | 依赖版本、项目结构、部署方案 |
| UI 规范 | `memory-bank/ui-style-guide.md` | 浅色雅金风完整规范 |
| 实施方案 | `memory-bank/implementation-plan.md` | 任务分解、模块依赖 |
| 项目进度 | `memory-bank/progress.md` | 代码目录、模块状态、变更记录 |
| 数据分析方案 | `memory-bank/data-analysis-complete.md` | CSV 结构、衍生指标、图表 |
| 安全审查 | `memory-bank/security-review.md` | 安全审查结论 |
| AI 检查清单 | `memory-bank/ai-checklist.md` | 错误记录、联动规则、自检流程 |
| 部署文档 | `DEPLOY.md` | Docker Compose 部署全流程 |
| Git 规范 | `GIT-GUIDE.md` | 分支/提交/发布/双远程 |
| 后端开发文档 | `backend/docs/README.md` | 后端需求、进度 |
| 前端开发文档 | `frontend/docs/README.md` | 前端需求、进度 |

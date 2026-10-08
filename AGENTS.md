# AGENTS.md — AI 开发指南（规范 · 文档维护 · 进度追踪）

> 本文件是 AI 助手（任意编码工具）在本仓库的**入口文件，每次开发前必读**。
> 原 `CLAUDE.md`，2026-09-15 更名并扩充：开发规范、各文档的维护职责、文档同步与进度追踪流程。
> 配套：`memory-bank/ai-context.md`（项目全貌速查）、`memory-bank/ai-checklist.md`（历史教训与易错点）。

## 1. 项目简介

**轻衫都会用的帮会联赛管理系统** — 逆水寒游戏帮会一体化管理工具。

- 核心功能：常驻库、出勤库、联赛排表（10 队 × 6 人拖拽）、录屏审核、数据分析（ECharts 8 Tab）、分析调整、系统配置、联赛日程、个人战绩、系统日志
- 技术栈：Vue 3 + TS + Vite + Element Plus + ECharts 6 + Pinia / Python 3.11（生产镜像基座 `python:3.11-slim` 与 CI；本地 3.11–3.13 可用，3.14 暂不可用） + FastAPI + SQLAlchemy + SQLite / Docker Compose + Nginx（权威源 `memory-bank/tech-stack.md`）
- 角色：developer（全局管理 + 系统日志）、admin（帮会全部权限）、member（录屏上传 / 个人战绩 / 联赛日程，赛程详情仅录屏与数据分析只读）（权威源 `design-document-v2.md` §3）
- 启动命令与默认账号：见 `README.md`（其他文档只引用，不复制）

## 2. 文档维护规范（核心）

### 2.1 权威源映射（同一主题只有一个权威源）

| 主题 | 权威源 | 其他文档的写法 |
|------|--------|---------------|
| 产品设计 / 角色权限 / 功能清单 | `design-document-v2.md` | 一句话 + 链接 |
| 数据库表结构 / 字段 / 业务规则 | `database-design.md` | 引用，不复制表结构 |
| 技术栈版本 | `tech-stack.md` + `backend/requirements.txt` | 摘要 + "详见 tech-stack.md" |
| UI 规范（最终视觉规范） | `ui-style-guide.md`（§10 优化补充规范） | 引用，不复制令牌 |
| UI 优化方案 | `ui-polish-plan.md`（已全部完成归档） | 引用 |
| 代码目录树 | `progress.md` | 不复制，引用 progress.md |
| 文档索引 / 文档目录树 | `architecture.md` | 不复制，引用 architecture.md |
| 文件行数规范 | `.agent/rules/file-length-rule.md` | 摘要 + 链接 |
| 模块开发文档规范 | `.agent/rules/function_rule.md` | 摘要 + 链接 |
| Git / 分支规范 | `GIT-GUIDE.md` | 3 行摘要 + 链接 |
| 安全要点 | `security-review.md` | 要点摘要 + 链接 |
| 默认账号 / 启动命令 | `README.md` | 引用 README.md |
| 数据分析规格（CSV/指标/口径） | `data-analysis-complete.md` | 引用 |
| 进度与变更记录 | `progress.md`（唯一进度权威） | 不复制进度表 |
| AI 历史教训 / 易错点 | `ai-checklist.md` | 引用 |

**铁律**：任何值/事实只允许在权威源维护；其他位置一律「摘要 + 引用」，禁止复制完整内容。
历史教训：曾出现出勤率公式两版、目录树三份、requirements 失配（见 `ai-checklist.md` §五 第 10 条）。

### 2.2 文档索引与维护时机

| 文档 | 路径 | 定位 | 何时必须更新 |
|------|------|------|-------------|
| AGENTS.md（本文件） | 根目录 | AI 入口：规范 + 文档维护 + 同步流程 | 项目结构、规范或维护流程变更 |
| 产品设计 | `memory-bank/design-document-v2.md` | 功能定义、权限矩阵、页面结构 | 需求 / 功能 / 权限调整 |
| 数据库设计 | `memory-bank/database-design.md` | 12 张表、字段约束、业务规则落表 | 表结构变更 / Alembic 迁移 |
| 技术栈 | `memory-bank/tech-stack.md` | 依赖版本、部署方案 | 依赖 / 构建 / 部署调整 |
| UI 规范 | `memory-bank/ui-style-guide.md` | 浅色雅金风最终规范 | UI 规范调整 |
| UI 优化方案 | `memory-bank/ui-polish-plan.md` | 已完成归档（全部完成） | 方案调整时 |
| 成员战绩与战报方案 | `memory-bank/stats-report-plan.md` | 已实施完成（2026-09-17） | 方案调整时 |
| 游戏 ID 改名与战绩关联设计 | `memory-bank/design-game-id-change.md` | 专项设计（2026-09-20 已实施，待验收） | 功能调整或实施完成时 |
| 实施方案 | `memory-bank/implementation-plan.md` | 历史规划存档（已完工） | 不维护 |
| 项目进度 | `memory-bank/progress.md` | 代码目录树 + 模块状态 + 变更记录（**进度唯一权威**） | **每次代码变更后** |
| 文档索引 | `memory-bank/architecture.md` | 文档结构、说明、更新记录（**文档索引唯一权威**） | **每次新增 / 改名 / 职责变更文档后** |
| 数据分析规格 | `memory-bank/data-analysis-complete.md` | CSV 结构、指标公式、实施记录 | 分析模块功能调整 |
| 安全审查 | `memory-bank/security-review.md` | 审查结论、修复决策记录 | 安全相关变更 |
| AI 上下文 | `memory-bank/ai-context.md` | 项目全貌速查（本文件扩展版） | 架构 / 规范重大变更 |
| AI 检查清单 | `memory-bank/ai-checklist.md` | 历史教训、易漏点、专项检查 | 发现新易错模式时 |
| 后端 / 前端开发文档 | `backend/docs/README.md`、`frontend/docs/README.md` | 各端功能清单与**功能点勾选清单**（阶段完成度 / 模块状态以 `progress.md` 为准，见 §3.4） | 各端功能点完成 |
| 代码 / 提交流程规则 | `.agent/rules/*.md` | 行数限制、模块文档、提交信息、项目规则 | 规范调整 |
| 合规化整改计划 | `.agent/plans/compliance-remediation-plan.md` | 全仓合规差距清单（F 编号持续追加）与分波次整改路线、验收命令、授权边界 | 每完成一项整改任务 / 波次结束 / 决策变更 |
| 部署文档 | `DEPLOY.md` | Docker Compose 部署全流程 | 部署配置变更 |
| 更新日志 | `CHANGELOG.md` | 面向使用者的版本变更（Keep a Changelog 1.1.0） | 每次发布前 / 有使用者可见变更时 |
| 贡献指南 | `CONTRIBUTING.md` | 协作约定摘要与权威源入口（环境、分支、门禁、PR） | 协作流程或 CI 门禁变化时 |
| 安全政策 | `SECURITY.md` | 漏洞报告渠道、支持版本、处理时限（安全结论权威源仍为 security-review.md） | 报告渠道或支持策略变化时 |
| 行为准则 | `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1（官方中文译本） | 升级版本或调整举报渠道时 |
| 代码审查与 UI 评估快照 | `memory-bank/code-ui-audit-2026-09.md` | 2026-09 代码审查与 UI 评估结论快照（**非权威源**；结论以 `security-review.md` / `ui-style-guide.md` 为准） | 不维护（快照存档） |

注：memory-bank 文档统一小写 kebab-case 命名；新增文档必须登记到 `architecture.md`（说明 + 目录树 + 更新记录）。

## 3. 文档同步与进度追踪流程（AI 必执行）

### 3.1 开发前

1. 通读本文件（AGENTS.md），按任务查阅对应权威源文档
2. 阅读 `memory-bank/ai-checklist.md`（易错点与历史教训）
3. UI 任务：必须遵循 finesse-ui skill 流程（用户明确要求）

### 3.2 开发中

- 遵循代码规范（§4）；发现文档与代码不一致时，**以实际代码为准修正文档**并在更新记录中说明

### 3.3 完成后自检清单（提交 / 交付前逐项确认）

1. **改代码 → `progress.md`**：① 代码目录树（新增 / 删除文件）② 模块说明表（新模块 / 状态）③ 更新记录（`| 日期 | 更新内容 | 关联模块 |`）
2. **新增 / 改名 / 职责变更文档 → `architecture.md`**：① 文档说明 ② 目录树 ③ 更新记录（三项都要）
3. **新增文件 → 两个目录树都检查**（architecture.md 文档视角 + progress.md 代码视角）
4. **受影响的权威源已同步**：改表结构 → database-design；改依赖 → tech-stack；改权限 → design-document
5. **版本号 / 数量一致性**：grep 旧值（如「9 表」「v1.5」「Python 3.12」）
6. **重命名文件**：grep 旧文件名（含 `deploy.sh` 排除列表、`.sh` / `.bat` 引用；历史变更记录中的旧名属时间戳证据，保留）
7. **配置文件联动**：改 `config.py` ↔ 检查 `.env.example`；改 `.gitignore` ↔ 用 `git status` 验证
8. **新易错模式**：补充 `ai-checklist.md` §五 高频遗漏表

### 3.4 进度追踪约定

- **唯一进度权威：`progress.md`**；阶段完成度、模块状态只在该文件维护，其他文档不复制进度
- 更新记录格式可检索：日期 + 简述 + 关联模块；历史条目保留原文不回改

## 4. 代码规范（摘要）

- 文件行数硬限：Vue 组件 300 行 / Python 服务 300 行 / 工具函数 200 行 / 路由 150 行；超限必须拆分（详见 `.agent/rules/file-length-rule.md`）
- 分层原则：`api/v1` 薄路由（参数校验 + 调用 service）→ `services` 业务逻辑 → `models` / `schemas`
- 其余规范（模块文档、提交信息、项目规则）见 `.agent/rules/`

## 5. Git 规范（摘要）

- 分支：`main`（始终可发布）+ `feature/<功能名>` + `hotfix/<描述>`；合并用 `--no-ff`；远端 `origin`（GitHub）为唯一权威远端，镜像（如 Gitee）可选（决策 D-2）
- 提交格式：`<type>(<scope>): <中文摘要>`，scope 必填（详见 `GIT-GUIDE.md`）
- **未经用户允许，禁止执行 git 提交或删除操作**

## 6. 安全要点（摘要）

> 权威源：`memory-bank/security-review.md`

- 已实施：JWT + 角色权限、登录限流（5 次 / 5 分钟）、bcrypt、上传限制、Nginx 限流、DEBUG 异常脱敏、Token 版本吊销
- 已知接受风险：`plain_password` 明文列（仅开发者可见）、localStorage Token、帮众共享账号

## 7. AI 行为约定（硬性）

1. 改动代码必须同步文档（§3.3 自检清单），禁止只改代码不更新文档
2. 禁止将权威源内容复制到其他文档（改为摘要 + 引用）
3. UI 优化任务必须严格遵循 finesse-ui skill（用户要求）
4. 浏览器操作仅在用户明确指示时执行
5. 发现文档与代码矛盾时：先核实代码事实，再修正文档并记录

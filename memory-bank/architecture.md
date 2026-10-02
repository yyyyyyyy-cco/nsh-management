# 项目文档索引

## 文档结构总览

```
nsh-management/
├── .agent/
│   ├── docs/                         # 内部样例（比赛 CSV 入库；Excel 分析表仅本地）
│   ├── plans/                        # 规划/整改类文档
│   │   └── compliance-remediation-plan.md   # 项目合规化与工程完善计划
│   └── rules/                        # AI 编码规则（已入库）
│       ├── code_rule.md              # 项目规则
│       ├── file-length-rule.md       # 代码文件长度规则
│       ├── function_rule.md          # 模块开发文档规则
│       └── git-commit-message.md     # Git 提交信息规范
├── memory-bank/
│   ├── ai-context.md           # AI 项目完整上下文文档（AGENTS.md 扩展版）
│   ├── ai-checklist.md         # AI 操作检查清单（错误记录与联动规则）
│   ├── architecture.md         # 本文档 - 项目文档索引
│   ├── data-analysis-complete.md # 数据分析模块完整方案
│   ├── database-design.md        # 数据库设计文档
│   ├── design-document-v2.md     # 产品设计文档（当前主文档）
│   ├── design-game-id-change.md  # 游戏 ID 改名申请与战绩关联设计
│   ├── implementation-plan.md    # 实施方案文档
│   ├── progress.md               # 项目进度文档
│   ├── security-review.md        # 安全审查文档
│   ├── stats-report-plan.md      # 成员战绩与战报实施方案
│   ├── tech-stack.md             # 技术栈文档
│   ├── code-ui-audit-2026-09.md  # 2026-09 代码审查与 UI 评估结论快照
│   ├── ui-polish-plan.md         # UI优化方案文档
│   └── ui-style-guide.md         # UI风格参考文档
├── backend/
│   └── docs/README.md            # 后端模块开发文档
├── frontend/
│   └── docs/README.md            # 前端模块开发文档（含排表保存约定与人工回归清单）
├── .qoder/
│   └── plans/                    # 外部 AI 工具（Qoder）规划草案，**非项目权威文档**（仅存档，见 §22）
├── AGENTS.md                     # AI 开发指南：规范/文档维护/进度追踪（自动读取）
├── CHANGELOG.md                  # 更新日志（Keep a Changelog 1.1.0）
├── CODE_OF_CONDUCT.md            # 行为准则（Contributor Covenant 2.1）
├── CONTRIBUTING.md               # 贡献指南（协作约定摘要 + 权威源链接）
├── DEPLOY.md                     # 部署文档（Docker Compose）
├── GIT-GUIDE.md                  # Git 管理规范
├── SECURITY.md                   # 安全政策（漏洞报告渠道、支持版本范围）
├── .gitignore                    # Git忽略规则
└── README.md                     # 项目说明
```

---

## 文档说明

### 1. 产品设计文档
- **路径**：`memory-bank/design-document-v2.md`
- **作用**：定义产品功能、用户角色（developer/admin/member）、权限、页面结构、API接口、数据库设计等，整合UI设计规范（浅色雅金风）
- **状态**：当前唯一有效版本，开发以本文档为准
- **更新时机**：需求变更、功能调整时更新

### 1.1 UI风格参考文档
- **路径**：`memory-bank/ui-style-guide.md`
- **作用**：定义「浅色雅金风（宣纸鎏金）」设计规范：色彩令牌、字体、组件规范、布局、动画、职业色映射；实现位置为 `frontend/src/styles/`（theme.css / element-plus.css / index.css）
- **更新时机**：UI 风格调整、设计令牌变更时更新

### 1.2 UI优化方案文档
- **路径**：`memory-bank/ui-polish-plan.md`
- **作用**：记录 UI 优化方案（P0-P3 共 11 项优化清单：视觉层次/交互反馈/细节打磨/微动效）、CSS 新增动画族规范、卡片层级规范、文件变更清单、验收标准（2026-09-18 全部完成：P0–P3 11 项 + §2.5 代码质量 2 项 + 3 项可选项——表格密度切换/空状态 SVG 插画/职业标签 hover 微光；最终规范见 ui-style-guide.md §10）
- **前置文档**：`ui-style-guide.md`（权威视觉规范，本文档仅补充优化增量）
- **更新时机**：优化项完成或方案调整时更新

### 2. 数据库设计文档
- **路径**：`memory-bank/database-design.md`
- **作用**：定义全部数据表结构（12 表，含 squad_adjustments、operation_logs、member_game_id_requests）、字段约束、索引、JSON存储结构及关键业务规则落表方案；当前版本 v1.9（含 developer 角色、plain_password、remark、title_remark、groups_remark、分析调整、操作审计、游戏 ID 修改申请）
- **更新时机**：表结构变更、业务规则调整时更新

### 3. 技术栈文档
- **路径**：`memory-bank/tech-stack.md`
- **作用**：记录前后端技术选型（含 echarts 图表库）、项目结构、Docker Compose 部署方案、依赖包等
- **更新时机**：技术栈变更、依赖升级时更新

### 4. 项目规则文档
- **路径**：`.agent/rules/code_rule.md`
- **作用**：定义强制前置要求、文档更新规则
- **更新时机**：项目规则调整时更新

### 5. 代码文件长度规则
- **路径**：`.agent/rules/file-length-rule.md`
- **作用**：定义文件行数限制、拆分触发条件、拆分策略
- **更新时机**：编码规范调整时更新

### 6. 模块开发文档规则
- **路径**：`.agent/rules/function_rule.md`
- **作用**：定义模块开发文档的要求、模板、更新规则
- **更新时机**：模块开发规范调整时更新

### 6.1 Git 提交信息规范
- **路径**：`.agent/rules/git-commit-message.md`
- **作用**：定义 Git 提交信息格式（Conventional Commits + 中文）、类型、范围、正文要求
- **更新时机**：提交规范调整时更新

### 7. 项目文档索引（本文档）
- **路径**：`memory-bank/architecture.md`
- **作用**：整理项目所有文档的作用和目录，方便快速查找
- **更新时机**：每次更新其他文档后必须同步更新本文档

### 8. 实施方案文档
- **路径**：`memory-bank/implementation-plan.md`
- **作用**：定义项目开发任务分解、模块依赖关系、开发阶段规划（2026-09-15 起转为历史规划存档，最新进度见 progress.md）
- **更新时机**：开发计划调整时更新

### 9. 项目进度文档
- **路径**：`memory-bank/progress.md`
- **作用**：记录代码模块结构、开发进度、代码变更记录；当前阶段 7 已完成（功能增强与部署）
- **更新时机**：每次更新代码后必须同步更新本文档

### 10. 后端模块开发文档
- **路径**：`backend/docs/README.md`
- **作用**：后端模块的需求说明、开发计划（全部 P0/P1/P2 已完成）、进度跟踪
- **更新时机**：后端每个功能点完成时更新

### 11. 前端模块开发文档
- **路径**：`frontend/docs/README.md`
- **作用**：前端模块的需求说明、功能清单、排表保存约定与人工回归清单；实际进度与验证结果以 progress.md 为准
- **更新时机**：前端每个功能点完成时更新

### 12. 部署文档
- **路径**：`DEPLOY.md`
- **作用**：Docker Compose 部署全流程：架构、环境变量、部署步骤、运维（日志/升级/备份/恢复）、常见问题
- **更新时机**：部署配置（Dockerfile / nginx.conf / docker-compose.yml / .env 变量）变更时更新

### 13. 数据分析模块完整方案
- **路径**：`memory-bank/data-analysis-complete.md`
- **作用**：数据分析模块规格与实施记录（2026-09-15 瘦身归档）：CSV 结构与字段映射、小队结构、16 项衍生指标公式、开发方案、ECharts 图表规划、实施记录与口径确认
- **更新时机**：数据分析模块功能调整时更新

### 14. 安全审查文档
- **路径**：`memory-bank/security-review.md`
- **作用**：项目安全审查记录，涵盖认证、权限、数据安全等方面的审查结论与改进项（§一～九为初次全量审查；§十为用户隔离定向修复；§十一为改名关联安全决策；§十二为全项目审查 F01 图表 HTML 输出边界及历史结论更正）
- **更新时机**：安全相关变更或审查时更新

### 15. AI 项目完整上下文文档
- **路径**：`memory-bank/ai-context.md`
- **作用**：根目录 `AGENTS.md` 的完整扩展版，为 AI 助手提供项目全貌：功能模块、技术栈详情、编码规范、Git 工作流、文档体系、安全要点、已知待优化项
- **更新时机**：项目架构、技术栈、规范发生重大变更时更新

### 16. AI 操作检查清单
- **路径**：`memory-bank/ai-checklist.md`
- **作用**：记录 AI 在本项目中犯过的错误和容易遗漏的联动点（版本号散落、文件重命名联动、目录树同步、.env 对齐等），每次修改前必读
- **更新时机**：发现新的遗漏模式时补充

### 17. AI 开发指南（入口文档）
- **路径**：`AGENTS.md`
- **作用**：AI 入口文档（原 `CLAUDE.md`，2026-09-15 更名扩充）：项目简介、权威源映射、各文档维护时机、文档同步与进度追踪流程（自检清单）、代码/Git/安全摘要、AI 行为约定
- **更新时机**：项目结构、规范或维护流程变更时更新

### 18. 成员战绩与战报实施方案
- **路径**：`memory-bank/stats-report-plan.md`
- **作用**：成员详情战绩页（管理员独立页）与单场图文战报的实施方案（2026-09-17 已实施完成，待浏览器验收）：决策记录、交互设计、技术方案、文件清单、验证方案、二期规划
- **更新时机**：方案调整或实施完成时更新

### 19. 游戏 ID 改名申请与战绩关联设计
- **路径**：`memory-bank/design-game-id-change.md`
- **作用**：帮众提交游戏 ID 修改申请、管理员审核、通过后同步常驻库，以及个人战绩/成员详情新旧 ID 合并查询专项设计（2026-09-20 设计确认并实施完成，待浏览器验收；实施与验证状态见 progress.md）：背景决策、业务流程、API 合同、关联算法与冲突边界、权限事务、前端交互、验证方案
- **更新时机**：功能调整或实施完成时更新

### 20. 代码审查与 UI 评估报告（2026-09）
- **路径**：`memory-bank/code-ui-audit-2026-09.md`
- **作用**：2026-09-28 全项目深度审查结论快照，覆盖后端代码质量/安全/性能与前端 UI/UX 两大维度（严重 3 / 高 19 / 中 34 / 低 12 + 8 处规范文档缺陷），含建议整改顺序与优秀实践保护清单
- **更新时机**：后续审查或整改验收时追加更新记录

### 21. 项目合规化与工程完善计划
- **路径**：`.agent/plans/compliance-remediation-plan.md`（仓库相对路径：该计划 W0-3 将统一清理其余条目的陈旧绝对路径，见其 F-37）
- **作用**：面向「全新克隆」的合规整改路线图：以行业权威规范为基准（SemVer 2.0.0 / Conventional Commits 1.0.0 / Keep a Changelog 1.1.0 / OWASP ASVS 5.0.0 / OWASP Top 10:2025 / SLSA v1.2 / 12-Factor / CIS Docker Benchmark 等），逐条列出 42 项差距（F-01～F-42，含文件行号级证据）、Wave 0～4 共 31 项任务（动作 / 验收命令 / 依赖 / 风险回滚 / 估算）、回归命令清单与需用户确认的 6 项决策（D-1～D-6）
- **更新时机**：每完成一项任务更新其 §7 进度表；波次结束、决策变更或验收结论变化时更新

### 22. 外部工具规划草案（Qoder）
- **路径**：`.qoder/plans/`（3 份：`UI_polish_phase_audit_fixes_4f80f074.md`、`帮众游戏_ID_改名审批设计_e1d99897.md`、`超限文件拆分计划_aa5182ef.md`）
- **作用**：外部 AI 工具生成的规划草案**存档**。**不是项目权威文档**——其对应的功能（UI 优化收尾、游戏 ID 改名审批、超限文件拆分）均已在 `progress.md` 记录并完成；此处登记仅为满足「入库文档必须登记到本索引」（`AGENTS.md` §2.2）
- **更新时机**：该目录新增或清理文件时更新；若不再使用该工具目录，可整体移出仓库（见合规化计划 F-36）

### 23. 社区与流程文档（2026-10-02 按公开仓库标准补齐）

- **路径**：`CHANGELOG.md`（仓库根目录）
- **作用**：更新日志，遵循 Keep a Changelog 1.1.0 与 SemVer 2.0.0；`[未发布]` 段记录待发布变更，
  历史版本段由 `git log` 归并（文件内标注归并依据）。**版本权威是 git 标签**，
  `frontend/package.json` 版本号不一致问题待决策 D-4 处理
- **更新时机**：每次发布前把 `[未发布]` 转为版本段；有面向使用者的变更时追加

- **路径**：`CONTRIBUTING.md`（仓库根目录）
- **作用**：贡献指南——协作约定与入口的**摘要 + 链接**（分支/提交/发布引用 `GIT-GUIDE.md`、
  提交消息引用 `.agent/rules/git-commit-message.md`、行数与模块文档引用 `.agent/rules/`、
  文档同步引用 `AGENTS.md` §3.3），并给出与 CI 对应的本地门禁命令
- **更新时机**：协作流程或 CI 门禁变化时更新（不得复制权威源内容）

- **路径**：`SECURITY.md`（仓库根目录）
- **作用**：安全政策——支持的版本范围、漏洞报告渠道（GitHub 私有安全公告为**首选**，
  备用邮箱为占位符待维护者填写）、处理时限目标、已知接受风险的**引用**（权威源 `memory-bank/security-review.md`）
- **更新时机**：报告渠道、支持策略或合规口径变化时更新

- **路径**：`CODE_OF_CONDUCT.md`（仓库根目录）
- **作用**：行为准则，**逐字采用 Contributor Covenant 2.1 官方简体中文译本**
  （CC BY-SA 4.0，随原文保留署名与链接；仅填写了举报联系方式）；原文最新为 3.0，升级列为后续可选项
- **更新时机**：升级版本或调整举报渠道时更新

---

## 更新记录

| 日期 | 更新内容 | 关联文档 |
|------|---------|---------|
| 2026-08-03 | 初始化文档索引 | architecture.md |
| 2026-08-03 | 添加文档更新规则 | code_rule.md |
| 2026-08-03 | 拆分规则文档，新增文件长度规则 | code_rule.md, file-length-rule.md |
| 2026-08-03 | 新增模块开发文档规则 | code_rule.md, function_rule.md |
| 2026-08-03 | 新增实施方案文档 | implementation-plan.md |
| 2026-08-03 | 新增UI风格参考文档 | ui-style-guide.md |
| 2026-08-03 | 添加职业颜色映射 | ui-style-guide.md |
| 2026-08-03 | 更新职业颜色（铁衣、玄机、龙吟） | ui-style-guide.md |
| 2026-08-05 | 删除 v1 设计文档，确认 v2 为唯一设计文档 | design-document-v2.md, architecture.md |
| 2026-08-05 | 更新进度文档代码目录结构 | progress.md |
| 2026-08-05 | 新增数据库设计文档 | database-design.md, architecture.md |
| 2026-08-05 | 数据库设计 v1.1：多帮会隔离、出勤率公式修正、match_data 按真实 CSV 样例重设计 | database-design.md |
| 2026-08-05 | 数据库设计 v1.2：击败数=击败+清泉合计 | database-design.md |
| 2026-08-05 | 数据库设计 v1.3：确认重伤=死亡数、复活/清泉单值、焚骨独立榜单 | database-design.md |
| 2026-08-06 | 新增前后端模块开发文档 | backend/docs/README.md, frontend/docs/README.md |
| 2026-08-06 | 阶段一完成：前后端骨架、9 表迁移、认证模块、布局与登录页 | progress.md, tech-stack.md |
| 2026-08-07 | 常驻库模块完成（CRUD/Excel导入/出勤率 + 前端列表/弹窗） | backend/docs, frontend/docs, progress.md |
| 2026-08-11 | 联赛日程模块完成（级联创建/删除 + 前端日历/详情Tab） | backend/docs, frontend/docs, progress.md |
| 2026-08-11 | 出勤库模块完成（导入/补人/状态/保存），术语”客人”改”补人”（数据库 v1.4） | database-design.md, backend/docs, frontend/docs, progress.md |
| 2026-08-11 | 排表模块完成（候选池/拖拽编排/备注/总览/导出PNG），测试与构建通过 | backend/docs, frontend/docs, progress.md |
| 2026-08-17 | 新增部署文档 DEPLOY.md，同步 Docker Compose 部署文件（Dockerfile/nginx.conf/docker-compose.yml/.env.example） | DEPLOY.md, progress.md |
| 2026-08-17 | 录屏审核/数据分析/系统配置模块完成，全站 UI 优化（浅色雅金风），全部前后端模块开发完成 | backend/docs, frontend/docs, progress.md |
| 2026-08-18 | 数据库设计 v1.5：users 新增 plain_password/developer 角色、profession_configs 新增 remark、lineups 新增 title_remark/groups_remark | database-design.md |
| 2026-08-18 | 技术栈更新：新增 echarts 依赖、Docker Compose 部署架构完善 | tech-stack.md |
| 2026-08-18 | 前后端模块文档更新：全部 P0/P1/P2 功能标记为已完成，进度 100% | backend/docs, frontend/docs |
| 2026-08-18 | 进度文档更新：目录结构、模块状态、开发阶段 7 完成 | progress.md |
| 2026-08-26 | 数据分析模块文档对齐现有代码（8 Tab / 后端 7 接口 / 16 项衍生指标，移除 HTML 报告导出描述）；新增 data-analysis-complete.md 文档索引（移入 memory-bank） | architecture.md, progress.md, database-design.md, design-document-v2.md, backend/docs, frontend/docs |
| 2026-08-26 | 文档全面对齐：architecture.md 补充 security-review.md 索引；progress.md 修复 Alembic 迁移数 12→9、补全 services/api/utils 文件列表、新增分析调整/开发者 API 模块；design-document-v2.md 修正布局尺寸与角色描述、补充分析调整；tech-stack.md 修正 ECharts/FastAPI 版本、补全文件列表；backend/frontend docs 补全 developer 角色与分析调整模块 | 全部文档 |
| 2026-08-26 | 文档命名统一：DATA_ANALYSIS_COMPLETE.md → data-analysis-complete.md、SECURITY-REVIEW.md → security-review.md，memory-bank 全部文件统一为小写 kebab-case；同步更新所有内部引用 | architecture.md, progress.md, deploy.sh, security-review.md |
| 2026-08-26 | 全面审查修复：code_rule.md 4条失效路径更正（design-document.md→design-document-v2.md、.trae/→.claude/）；architecture.md 目录树 .trae→.claude 并补充 git-commit-message.md 索引；implementation-plan.md 修正 Python 3.12→3.13、JWT 7天→10小时、模块依赖树补充分析调整；backend/.env.example 补充 DEBUG 变量、移除无效 ALGORITHM/ACCESS_TOKEN_EXPIRE 配置 | code_rule.md, architecture.md, implementation-plan.md, backend/.env.example |
| 2026-08-26 | 新增 AI 入门文档：根目录 `CLAUDE.md`（精简版，AI 自动读取）+ `memory-bank/ai-context.md`（完整扩展版），涵盖项目概述、技术栈、编码规范、Git 工作流、文档体系、安全要点 | CLAUDE.md, ai-context.md, architecture.md |
| 2026-08-26 | 目录树补全：architecture.md 和 progress.md 补充 CLAUDE.md、GIT-GUIDE.md、.claude/rules/ 入库条目；architecture.md 数据库设计描述修正 9 表→10 表、v1.5→v1.6；progress.md database-design 版本号 v1.5→v1.6 | architecture.md, progress.md |
| 2026-08-26 | 新增 AI 操作检查清单（ai-checklist.md）：记录版本号散落、文件重命名联动、目录树同步、.env 对齐等易错模式与自检流程；CLAUDE.md 新增"操作前必读"提示；architecture.md/progress.md 同步更新索引与目录树 | ai-checklist.md, CLAUDE.md, architecture.md, progress.md |
| 2026-08-26 | 文档瘦身与单一权威源：design-document-v2 删除内嵌 UI 规范（~200 行）改为引用 ui-style-guide；CLAUDE.md/ai-context.md 技术栈/Git/安全改为引用；ai-checklist 新增权威源规则表；修复 README 9 表→10、backend/docs v1.5→v1.6、UI 主色统一为 #C9A13B | 全部文档 |
| 2026-08-26 | 新增 UI 优化方案文档（ui-polish-plan.md）：4 优先级 11 项优化清单（卡片层级/数字滚动/按钮微光/奖牌微光/弹窗金线/滚动条/槽位反馈/路由过渡等），含动画族规范、卡片层级规范、验收标准、文件变更清单；ui-style-guide.md 新增 §10 优化补充规范（动画族/卡片层级/交互反馈） | ui-polish-plan.md, ui-style-guide.md |
| 2026-09-15 | 补人姓名规范化修复文档同步：progress.md 目录树补 services/lineup_attendance.py 与 utils/member_names.py 并记录修复；backend/frontend 模块文档更新记录同步 | progress.md, backend/docs, frontend/docs |
| 2026-09-15 | ai-context.md §8 新增「出勤库 60 人上限漏洞」记录（用户决策暂不修复）：含内存库复现结论、触发路径、已定待实施方案与残余并发风险 | ai-context.md |
| 2026-09-15 | 文档全面优化（依据实际代码核实）：design-document-v2 v2.4（出勤率公式/术语/帮众权限/页面树修正，补个人战绩与系统日志模块）；database-design v1.7；tech-stack 去重与失实项修正；ai-context 引用化与模块补全；data-analysis-complete 瘦身（768→610 行，修复代码块围栏）；implementation-plan/ui-polish-plan 归档标注；ai-checklist 编号修复 + 新增遗漏模式 | 全部文档 |
| 2026-09-15 | 工具目录改名同步（.claude/ → .agent/）：architecture.md 与 progress.md 目录树、`.agent/rules/` 路径引用、样例文档路径（`.agent/docs/`）、deploy.sh 打包排除项同步更新 | architecture.md, progress.md, database-design.md, design-document-v2.md, ai-context.md, ai-checklist.md, deploy.sh |
| 2026-09-15 | 根目录 `CLAUDE.md` 更名为 `AGENTS.md`（AI 开发指南）：扩充为项目规范 + 权威源映射 + 各文档维护时机 + 文档同步与进度追踪流程（自检清单）+ AI 行为约定；权威源映射表与自检清单由 ai-checklist.md 迁入并以其为准；ai-checklist/ai-context/architecture/progress/.agent/rules 引用同步 | AGENTS.md, ai-checklist.md, ai-context.md, architecture.md, progress.md |
| 2026-09-15 | 文档失实项修正（实测核对）：全局表数 10→11、迁移数 13→14、database-design v1.8（补 operation_logs 表）；backend/frontend docs 角色场景/模块清单/待办状态按代码校正；README 功能表与权限行、DEPLOY.md 迁移 head（n8o9p0q1r2s3）同步 | 全部文档 |
| 2026-09-15 | 仓库收录策略调整：`.agent/rules/*.md` 4 份规则文档入库（AGENTS.md 权威源可追溯），本文档 §文档结构总览同步标注入库/忽略范围；`.agent/docs/` 仅文本 CSV 入库、24MB Excel 分析表本地忽略 | architecture.md, progress.md, .gitignore |
| 2026-09-17 | 新增成员战绩与战报实施方案（stats-report-plan.md 入索引：目录树 + 文档说明 §18 + 更新记录）：成员详情战绩页与单场图文战报，方案已确认待实施 | stats-report-plan.md, design-document-v2.md, backend/docs, frontend/docs |
| 2026-09-17 | 成员战绩与战报方案实施完成：stats-report-plan 状态更新（已实施待验收，含实施记录）、文档说明 §18 描述同步；design-document v2.5 描述去规划标注；backend/frontend docs 状态流转；代码变更记录见 progress.md | stats-report-plan.md, design-document-v2.md, backend/docs, frontend/docs, progress.md |
| 2026-09-17 | 战报 v2 重设计：海报扩为 8 区块（总览/MVP 与数据之王/阵营对比 6 指标/榜单去重/逐局战况/职业伤害占比）；stats-report-plan §3.2–3.3 与更新记录同步；design-document §4.5 战报描述更新；frontend docs 同步 | stats-report-plan.md, design-document-v2.md, frontend/docs |
| 2026-09-17 | 战报口径调整（仅我方阵营）：stats-report-plan §1.2/§3 与更新记录同步（7 区块、排表判定我方、两请求加载）；design-document §4.5 更新；frontend docs 与 progress 目录树/更新记录同步 | stats-report-plan.md, design-document-v2.md, frontend/docs, progress.md |
| 2026-09-18 | 战报区块替换（职业分布 → 小队战况）：stats-report-plan §3 与更新记录同步；design-document §4.5 更新；frontend docs 与 progress 目录树/更新记录同步 | stats-report-plan.md, design-document-v2.md, frontend/docs, progress.md |
| 2026-09-18 | UI 优化可选项收尾（ui-polish-plan v1.3 全部完成）：表格密度切换（顶栏全局开关）/空状态 SVG 插画（EmptyState 4 变体全站替换）/职业标签 hover 微光；ui-style-guide §9 实现索引 + §10.1/§10.3/§10.4 同步；frontend docs 与 progress.md 同步 | ui-polish-plan.md, ui-style-guide.md |
| 2026-09-18 | 用户隔离定向修复（security-review §十 F-1～F-5）：security-review 新增 §十（修复记录/验证范围/未解决项更正，§14 文档说明同步）；design-document §3.2/§4.1 补充账号创建边界与导出标识规则；ai-checklist 新增遗漏模式 14（数据归属字段被请求体覆盖）；backend/frontend docs 更新记录；progress 目录树（+2 selfcheck 脚本）与更新记录 | security-review.md, design-document-v2.md, ai-checklist.md, backend/docs, frontend/docs, progress.md |
| 2026-09-20 | 新增游戏 ID 改名申请与战绩关联设计（design-game-id-change.md 入索引：目录树 + 文档说明 §19 + 更新记录）：帮众提交、管理员审核、通过后同步常驻库并支持新旧 ID 战绩合并查询；database-design v1.9（表数 11→12）、design-document v2.6、data-analysis/stats-report 口径同步；代码实施与验证状态见 progress.md | design-game-id-change.md, database-design.md, design-document-v2.md, data-analysis-complete.md, stats-report-plan.md, progress.md |
| 2026-09-20 | 游戏 ID 改名申请与战绩关联实施完成：新增 member_game_id_requests 表与迁移 o9p0q1r2s3t4、改名申请 API/服务/生命周期、个人战绩新旧 ID 合并与冲突 409 退路、帮众改名页与常驻库改名审核 Tab；4 个新增 selfcheck（13/5/9/1 项）与既有 16 项回归全部通过，后端 compileall、前端 vue-tsc/vite build 通过；design-game-id-change 状态更新为已实施待验收，security-review 新增 §十一 | design-game-id-change.md, database-design.md, security-review.md, backend/docs, frontend/docs, progress.md |
| 2026-09-24 | F01/F04 定向修复文档同步：security-review 新增 §十二输出边界与历史 XSS 结论更正；frontend/docs 补排表保存约定及人工回归清单，文档说明与目录注释同步；新增图表源码登记在 progress 的代码目录树，本索引不重复维护源码树 | security-review.md, frontend/docs/README.md, progress.md, ai-checklist.md |
| 2026-09-28 | 新增 code-ui-audit-2026-09.md 审查报告并登记 | architecture.md, code-ui-audit-2026-09.md, progress.md |
| 2026-09-28 | security-review.md / ui-style-guide.md 随严重问题修复同步更新（accounts 统一脱敏关闭 + 生产弱密钥启动门禁专节；主按钮墨色文字与禁用态规范），code-ui-audit-2026-09.md C-1～C-3 标注已修复 | security-review.md, ui-style-guide.md, code-ui-audit-2026-09.md |
| 2026-09-28 | ai-checklist §五 新增遗漏模式 20（非 cmd shell 中 `> nul` 重定向误创建 nul 文件）；.gitignore 增加 Windows 保留设备名 nul 忽略规则，删除误创建的 backend/nul | ai-checklist.md, progress.md, .gitignore |
| 2026-10-02 | 新增项目合规化与工程完善计划（`.agent/plans/compliance-remediation-plan.md`，登记为本索引 §21 并补目录树 `.agent/plans/`）：以行业权威规范为基准的全仓静态审查结论与整改路线——42 项差距证据清单（含 3 项 P0 交付阻断项）、Wave 0～4 共 31 项任务与逐项验收命令、6 项待确认决策；本轮仅新增计划文档，未改动代码与配置 | compliance-remediation-plan.md, architecture.md, AGENTS.md, progress.md |
| 2026-10-02 | Wave 0 文档一致性批次 1（合规化计划 W0-3/4/5/7）：①本索引 19 处「路径」条目由陈旧绝对路径 `e:\code\@Cjy\...`（本仓库旧位置）改为仓库相对路径（`.agent/rules/code_rule.md` 2 处同步）；②`memory-bank/SECURITY-REVIEW.md` **实际**改名为 `security-review.md`（2026-08-26 曾记录改名但未落地，本次两步 `git mv` 落实，历史记录中的旧名按 §3.3 保留）；③`README.md` 删除复制的代码目录树，改为引用本索引与 `progress.md`；④`backend/.dockerignore`、`frontend/.dockerignore` 旧目录名 `.claude` → `.agent`；⑤3 个一次性分析脚本移除 4 处硬编码绝对路径（改由 `NSH_DB_PATH`/`NSH_ANALYSIS_TS` 覆盖）；⑥`analysis.ts` 计分口径脚本引用 v3 → v4 | architecture.md, code_rule.md, security-review.md, README.md, progress.md |
| 2026-10-02 | Wave 0 批次 2（合规化计划 W0-6/W0-8）：①`tech-stack.md` §部署方案 按 `DEPLOY.md` 权威源重写——删除「前端容器 80/443 HTTPS」「后端容器多阶段构建」「deploy.sh（Linux 一键部署）」等失实描述，改为单层 TLS 摘要 + 引用（不复制 DEPLOY 内容），并在 `docker-compose.yml` 顶部标注「本地/单机演示拓扑」；②`.qoder/plans/` 3 份外部工具草案登记为本索引 §22 并补目录树（明确标注非项目权威文档） | tech-stack.md, architecture.md, progress.md |
| 2026-10-02 | Wave 0 批次 3（合规化计划 W0-2）：新增 `.gitattributes`（`* text=auto eol=lf`；`*.bat`/`*.cmd`/`*.ps1` 保持 CRLF；常见二进制标 `binary`）与 `.editorconfig`；配套执行 `git add --renormalize .` 归一存量换行（改造前实测 `i/crlf` 260 / `i/lf` 75），归一作为独立提交以便回溯 | .gitattributes, .editorconfig, architecture.md, progress.md |
| 2026-10-02 | Wave 1 批次 1（合规化计划 W1-1/W1-2/W1-6，P0 交付链）：①`frontend/nginx.conf` 入库（占位符版构建输入）并解除 `.gitignore` 忽略，修复全新克隆 `COPY nginx.conf` 构建失败；②`frontend/nginx.conf.example` 收窄为边缘层模板（内层以 `nginx.conf` 为唯一副本）；③新增 `deploy.sh.example`（占位符 + 排除清单 + 非零退出健康检查），`DEPLOY.md §三` 同步说明；④`README.md` 补「数据源模式（DB_MODE）」与构建前置说明 | DEPLOY.md, README.md, nginx.conf, nginx.conf.example, deploy.sh.example, architecture.md, progress.md |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 21（静默命令须判 `$LASTEXITCODE`：`git check-ignore -q` 的 `[bool]` 判定恒为 False，曾误报 deploy.sh 失去忽略）与 22（计数结论必须记录匹配范围与大小写选项：F-37 首记 23 处实为活引用 25 处 + 历史 2 处） | ai-checklist.md, progress.md, architecture.md |
| 2026-10-02 | Wave 2 批次 1（合规化计划 W2-1/W2-5/W2-7，质量门禁）：新增 `.github/workflows/ci.yml`（backend 编译+迁移+导入 / frontend `npm ci`+`vue-tsc`+`vite` / repo-hygiene 行数+陈旧路径+换行 / docker-build 双镜像）与 `.github/dependabot.yml`；新增 `scripts/check_file_length.py`；`.agent/rules/file-length-rule.md` 增补「前端 TS」行数类别与「自动检查（CI 门禁）」小节 | ci.yml, dependabot.yml, check_file_length.py, file-length-rule.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 2（合规化计划 W2-3 后端部分）：新增 `backend/ruff.toml`（规则集 E4/E7/E9/F，按文件豁免迁移与一次性脚本）与 `backend/requirements-dev.txt`（`ruff==0.12.0`）；CI backend job 增加 dev 依赖安装与 `ruff check .`；修复 9 处告警（8 项安全自动修复 + `models/user.py` 的 `Guild` 改 `TYPE_CHECKING` 导入）；`tech-stack.md` 开发工具与依赖权威源同步 | ruff.toml, requirements-dev.txt, ci.yml, tech-stack.md, user.py, architecture.md, progress.md |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 24：提交消息经 PowerShell 传参被拆参（`\|` 被当成 pathspec 致提交失败）与 `git commit -F` 漏写首行主题（整段正文被取为 subject，需 `--amend -F` 修正）；附「提交后复核 `%s` 与摘要长度」约定 | ai-checklist.md, progress.md, architecture.md |
| 2026-10-02 | Wave 2 批次 3（合规化计划 W2-4）：提交消息自动校验落地——`scripts/check_commit_msg.py`（15 条内置用例、BOM 容错）、`.githooks/commit-msg` 与 `scripts/install_git_hooks.sh`（零依赖 `core.hooksPath` 方案）、`.github/commit-msg-baseline` 与 CI `commit-msg` job（仅校验基线之后的提交，历史不追溯）；`.agent/rules/git-commit-message.md` 补 `merge` 类型与「自动校验」小节 | check_commit_msg.py, commit-msg, install_git_hooks.sh, commit-msg-baseline, ci.yml, git-commit-message.md, progress.md, architecture.md |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 25：PowerShell 向原生程序传文本会注入 BOM、重编码并隐式用空格拼接数组（实测导致 10 个合规提交被判违规的假阴性）；附「传文本优先走文件、管道须设无 BOM 编码、校验器容错 BOM」处置约定 | ai-checklist.md, progress.md, architecture.md |
| 2026-10-02 | Wave 2 批次 4（合规化计划 W2-2 后端部分）：新增 `backend/pytest.ini` 与 `backend/tests/`（conftest、support、4 个测试模块），`python -m pytest` 可同时收集新用例与既有 6 个 `selfcheck_*.py`；`backend/requirements.txt`/`requirements-dev.txt` 补 PEP 263 编码声明（修复中文 Windows 下 pip 解码失败）；CI backend job 增 pytest 步骤；`README.md`（测试与排错）与 `tech-stack.md`（开发工具、依赖权威源）同步 | pytest.ini, tests/, requirements.txt, requirements-dev.txt, ci.yml, README.md, tech-stack.md, architecture.md, progress.md |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 27：`git add -A` 会把工具在仓库根目录产生的临时目录（`pip-metadata-*/`、`pip-unpack-*/`、`.tmp-venv*/`）一并提交；`.gitignore` 已增补相应忽略规则；误提交且未推送时以删目录 + `git rm -r --cached` + `--amend` 修正（本次提交已由 55 文件修正为 17 文件） | ai-checklist.md, .gitignore, progress.md, architecture.md |
| 2026-10-02 | Wave 2 批次 5（合规化计划 W2-3 前端部分）：新增 `frontend/eslint.config.js`（vue flat/essential + typescript-eslint + skipFormatting；`vue/no-mutating-props` 过渡期 warn）与 `frontend/.prettierrc.json`；`package.json` 增 lint/lint:fix/format/format:check 脚本与 5 个 lint/format devDependencies；`src/composables/lineupBoard.ts` 新增导出类型 `SlotDragEvent` 取代 4 处 `any`（`LineupEditor.vue` 同步引用）；CI frontend job 增 `npm run lint`；`README.md` 补 Python 版本支持说明；`tech-stack.md` 开发工具与说明同步 | eslint.config.js, .prettierrc.json, package.json, package-lock.json, lineupBoard.ts, LineupEditor.vue, ci.yml, README.md, tech-stack.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 6（合规化计划 W2-2 前端部分）：新增 `frontend/vitest.config.ts` 与 4 个 spec（`utils/constants`、`utils/profession`、`utils/scheduleSort`、`match-data/analysis`，共 38 用例）；`package.json` 增 test/test:watch 脚本与 `vitest@3.2.7`+`jsdom` devDependencies；CI frontend job 增 `npm run test`；`tech-stack.md` 开发工具表同步（标注 vitest 须用 3.x 以匹配 vite 5） | vitest.config.ts, *.spec.ts, package.json, package-lock.json, ci.yml, tech-stack.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 7（合规化计划 W2-6 部分）：新增 `frontend/src/utils/attendance.ts`（出勤率展示口径唯一来源：阈值常量、低出勤判定、进度条颜色、百分比格式化）与 `attendance.spec.ts`（6 用例）；`AttendanceRatePanel.vue` / `MemberDetailHeader.vue` / `HomeAttendanceRanking.vue` 共 7 处硬编码（阈值 4 处、格式化 3 处）及组件内本地 `ratePercent()` 改为引用该模块；计划 F-03 描述按复核结果更正（出勤率公式无重复实现，原表述过重） | attendance.ts, attendance.spec.ts, AttendanceRatePanel.vue, MemberDetailHeader.vue, HomeAttendanceRanking.vue, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 8（合规化计划 W2-6 收尾，F-04）：弱密钥启动门禁由 `app/core/config.py` **导入期**移至应用启动期——新增 `InsecureSecretKeyError`、`FATAL_SECRET_KEY_MESSAGE`（原文逐字保留）、`WEAK_SECRET_KEY_WARNING`、`validate_secret_key()`（抛异常，可测）、`enforce_secret_key()`（打印 FATAL + 退出码 1）；`app/main.py` 新增 `startup_checks()` 并在 `on_startup` 中首先调用；`backend/tests/test_config_gate.py` 扩到 15 用例（含子进程回归：仅导入 config 不退出 / 调用门禁必拒绝启动）；修复 `tests/test_permissions.py` 未使用的 `unittest` 导入（`ruff check .` 曾因此报错） | config.py, main.py, test_config_gate.py, test_permissions.py, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 3 批次 1（合规化计划 W3-4 部分 / W4-4）：按公开仓库标准补齐 4 份根文档——`CHANGELOG.md`（Keep a Changelog 1.1.0；`[未发布]` 汇总本轮合规化改动，`v1.0.0/v1.1.0/v1.2.0` 由 `git log` 归并并标注依据；记录 `package.json` 版本不一致待 D-4）、`CONTRIBUTING.md`（摘要 + 权威源链接 + 与 CI 对应的本地门禁命令）、`SECURITY.md`（支持版本 / GitHub 私有报告渠道 / 处理时限目标 / 已知接受风险引用）、`CODE_OF_CONDUCT.md`（Contributor Covenant 2.1 官方中文译本）；本索引新增 §23 与目录树条目，`AGENTS.md` §2.2 与 `README.md` 同步链接 | CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, architecture.md, AGENTS.md, README.md, progress.md |
| 2026-10-02 | Wave 3 批次 2（合规化计划 W3-1 探针 / W4-1 生产关闭 API 文档）：新增 `backend/app/api/v1/health.py` 健康检查端点（`/health` 与 `/api/v1/health`，含数据库连通性，库不可用返回 503）；`docker-compose.yml` healthcheck 由根路径改探 `/health`；`core/config.py` 新增 `api_docs_enabled()`，`app/main.py` 据此在**生产环境关闭** `/docs` / `/redoc` / `/openapi.json`（本地开发保留）；新增 `backend/tests/test_health.py`（5 用例：探针语义、双路径路由、文档暴露面子进程断言），`tests/test_config_gate.py` 增 2 例文档开关判定；`DEPLOY.md §二` 新增「健康检查与在线 API 文档」小节 | health.py, main.py, config.py, docker-compose.yml, DEPLOY.md, test_health.py, test_config_gate.py, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 2（合规化计划 W4-3）：`core/config.py` 的 `CORS_ORIGINS` 外置为环境变量（新增 `_parse_cors_origins` 解析函数，未设置时回退本地开发来源），`.env.example` 与 `DEPLOY.md §六` 同步；`memory-bank/security-review.md` 新增 **§十四 依赖漏洞审计**（npm audit 7→4 项、pip-audit 2 个包，含逐项可达性判定与后续升级项），并更正 §十三 中已改名的门禁函数（`_validate_secret_key` → `validate_secret_key` / `enforce_secret_key`，执行点移至应用启动期）；`backend/tests/test_config_gate.py` 增 4 条 CORS 用例（含子进程端到端）；`frontend/package-lock.json` 经非破坏性依赖修复更新 | config.py, .env.example, DEPLOY.md, security-review.md, test_config_gate.py, package-lock.json, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 3（合规化计划 W4-2）：`memory-bank/security-review.md` 新增 **§十五 暴露面清单与 OWASP 对照**（15.1 暴露面清单 / 15.2 Top 10:2025 条目级对照 / 15.3 ASVS 5.0.0 域级对照 / 15.4 新识别 6 项不足）；合规化计划新增差距 F-43~F-46 与任务 W4-5~W4-8（CSP 收紧、告警通道、威胁建模、ASVS 条目级核对） | security-review.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | ai-checklist §五 新增遗漏模式 30：同一文档存在多个同前缀表格时，「最后一行匹配 `| 前缀-`」的插入锚点会跨表命中（本轮合规化计划 §5 任务表与 §7 进度表各错一次，修正两轮）；校验正则亦需先自测正/负样本 | ai-checklist.md, compliance-remediation-plan.md, progress.md, architecture.md |
| 2026-10-02 | Wave 3 批次 3（合规化计划 W3-2 / W3-3）：新增 `scripts/backup-db.sh.example`（SQLite 在线 backup API 自动化：默认 dry-run、生成后完整性校验、保留轮转、cron 示例）与 `scripts/release-archive.sh.example`（镜像 tar 归档 + 清单，版本权威为 git 标签，含标签/工作区核对）；`DEPLOY.md §五` 新增「自动化备份」（含 WAL 下直接 `cp` 丢数据的实测证据）与「恢复演练记录」小节，文件末尾新增 **§九 版本归档与回滚**（归档、回滚七步、数据库迁移不可逆警示、归档保留） | backup-db.sh.example, release-archive.sh.example, DEPLOY.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 3 批次 4（合规化计划 W3-6，决策 D-2）：`GIT-GUIDE.md` 远端策略由「双远程」改为 **「单远端 `origin` 为准 + 可选镜像」**（§1 仓库概览与策略段、§4.4 推送 main、§5.2 推送标签、§6「镜像远端（可选）」，必做/可选命令分列并给出配置镜像命令）；历史事实备注按 §3.4 保留不回改、仅调整结论句。同步权威源：`AGENTS.md §5`、`memory-bank/ai-context.md`、`memory-bank/progress.md` 代码树说明。同时按代码事实更正 `GIT-GUIDE.md §7.1`——原文把 `frontend/nginx.conf` 列为「禁止提交」，而该文件自 2026-10-02 起已入库（容器构建输入，占位符版）。`GIT-GUIDE.md §8` 发布检查清单新增三项（更新 CHANGELOG / **发布前**归档制品 / **发布前**数据库备份），与 `DEPLOY.md §九` 的发布纪律对齐；`AGENTS.md`、`ai-checklist.md`（新增第 31 条：追加式表格的尾部锚点会被自己的写入破坏）、合规化计划 §7 同步 | GIT-GUIDE.md, AGENTS.md, ai-context.md, ai-checklist.md, progress.md, compliance-remediation-plan.md, architecture.md |
| 2026-10-02 | Wave 1 批次 4（合规化计划 W1-4 / W1-5，含一处计划口径更正）：①**依赖锁定（W1-4 部分）**：`backend/requirements.txt` 两个范围约束改为精确锁定（`fastapi==0.142.2`、`python-multipart==0.0.32`）并显式锁定传递引入的 `starlette==1.7.0`（均为已实测组合；3.11 兼容性依据 PyPI 元数据 `requires_python >=3.10`）；新增门禁 `scripts/check_requirements_pins.py` 接入 CI `repo-hygiene` job。②**Python 版本表述（W1-5 文档部分）**：按代码事实把 8 处「3.13」统一为 3.11（`AGENTS.md`、`README.md` ×2、`backend/docs/README.md`、`ai-context.md`、`tech-stack.md` ×4）。③**口径更正**：W1-5 原文为「基础镜像升级到 `python:3.13-slim` / `node:22-alpine` 并统一文档」，因本机 Docker 不可用无法验证镜像升级，按 `AGENTS.md §3.2`（以代码为准）先把文档改为现状 3.11，镜像升级拆分为新任务 **W1-7**（§5/§7 同步登记） | requirements.txt, check_requirements_pins.py, ci.yml, AGENTS.md, README.md, backend/docs/README.md, ai-context.md, tech-stack.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 4（合规化计划 W4-6 / F-44）：新增错误率告警——`backend/app/core/alerting.py`（纯策略：阈值判定 / 负载契约 / 标准库 POST）+ `backend/app/services/alert_service.py`（窗口统计与编排、进程内去重）+ `main.py` 后台循环（每 `ALERT_CHECK_INTERVAL_MINUTES` 分钟，启动即查一次）；新增 `tests/test_alerting_policy.py`（无依赖可跑）与 `tests/test_alerting_service.py`；`core/config.py` 增 4 个 ALERT_* 配置，`.env.example`、`DEPLOY.md §四/§六` 同步说明。**同时修复测试收集期依赖硬失败**：`tests/test_core_security.py`、`tests/test_permissions.py`、`tests/test_alerting_service.py` 与 7 个 `scripts/selfcheck_*.py` 改为模块级 SkipTest（原来在无依赖环境是 pytest 退出码 2 的收集错误）；`backend/pytest.ini` 补第 4 条约定；ai-checklist 新增第 32 条 | alerting.py, alert_service.py, config.py, main.py, test_alerting_policy.py, test_alerting_service.py, test_core_security.py, test_permissions.py, scripts/selfcheck_*.py, pytest.ini, .env.example, DEPLOY.md, ai-checklist.md, security-review.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 5（合规化计划 W4-7）：`memory-bank/security-review.md` 新增 **§十六 威胁建模（STRIDE）**——7 类资产 + 5 个信任边界 + 18 条威胁核对（均附代码证据与残余风险），并更正 §15.3/§15.4 结论。建模产出 **F-47 导出文件公式注入**（用户输入以 `=` 开头被 openpyxl 写成公式）并**当轮修复**：`backend/app/utils/excel_export.py` 统一 `_text_cell` 显式声明文本单元格，新增 `backend/tests/test_excel_export_formula.py` 往返回归；顺带把该工具的 ORM 依赖改为 `TYPE_CHECKING` | security-review.md, excel_export.py, test_excel_export_formula.py, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 0 批次 8（新增 **W0-9** 环境变量文档联动门禁）：新增 `scripts/check_env_docs.py`（11 条内置自检）固化 AGENTS §3.3 第 7 条的「配置↔文档联动」；实跑发现 **7 个环境变量代码会读但未文档化**（`DEBUG`/`DATABASE_URL`/`LOG_RETENTION_DAYS`/`DEVELOPER_USERNAME`/`ADMIN_USERNAME`/`MEMBER_USERNAME`/`DEFAULT_GUILD_NAME`）并已按用途分组补入 `.env.example`；门禁接入 CI `repo-hygiene`。同时修正门禁自身的一个误判（整行注释中的 `os.getenv` 被统计） | check_env_docs.py, .env.example, ci.yml, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 7（合规化计划 **W2-2 收尾**）：`backend/scripts/selfcheck_indicators.py` 由「模块级断言脚本」改造为 3 个 unittest 用例类（8 用例，`--ignore` 随之移除），`backend/pytest.ini` 更新说明；`memory-bank/data-analysis-complete.md` 与 `progress.md` 代码树同步。**并修复一个真实缺陷**：`tests/test_alerting_service.py` 用同步 `setUp()` 访问 `DbTestCase.asyncSetUp()` 才创建的 `self.engine`，导致 5 个用例失败（该缺陷此前因本地无依赖被跳过而未暴露）| selfcheck_indicators.py, pytest.ini, test_alerting_service.py, data-analysis-complete.md, progress.md, ai-checklist.md, compliance-remediation-plan.md, architecture.md |
| 2026-10-02 | Wave 1 批次 5（新增 **W1-8** 依赖版本陈旧治理 / **F-48**）：`python-jose` 由 `3.3.0`（2021 年）升到 `3.5.0`（上游 3.4.0 即为修复 JWT 相关 CVE 发布；PyPI 元数据 `requires_python >=3.9`、`vulnerabilities: []`）；`requirements-dev.txt` 的 `httpx` 换成 `httpx2`（starlette 1.7 弃用告警）；`main.py` 由 `@app.on_event("startup")` 迁移到 `lifespan`（并新增退出时取消后台循环）。**全量套件 124 passed + 72 subtests、exit 0、0 warnings**（升级前 55 warnings）。`security-review.md` 新增 §14.6（含工具纪律更正：pip-audit 本轮未跑完，不视为依赖面完整）| requirements.txt, requirements-dev.txt, main.py, test_health.py, tech-stack.md, security-review.md, CHANGELOG.md, ai-checklist.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 8（合规化计划 W2-2 **接口级补齐**）：新增 `backend/tests/test_api_endpoints.py`（10 用例 / 2 subtests，经 TestClient 打完整链路：CORS 中间件 → 审计中间件 → 依赖注入 → 路由 → 序列化 → 异常处理器），覆盖登录成功/失败、**登录失败锁定（含锁定后正确密码仍被拒 + `remaining_seconds`）**、未知账号锁定、缺/坏令牌、**令牌版本吊销**、角色越权 403、CORS 预检、`/health`；DB 隔离为「内存库 + 覆盖 `get_db` + 三处自带 session 工厂也指向测试库」。**完整基线 134 passed + 74 subtests，exit 0，0 warnings**。同时修正 `httpx`→`httpx2` 的 4 处遗留引用与 `progress.md` 的 `tests/` 树描述 | test_api_endpoints.py, pytest.ini, backend/docs/README.md, progress.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md |
| 2026-10-02 | Wave 4 批次 7（合规化计划 W4-8 **部分完成：3/6 域**）：`security-review.md` 新增 **§十七 ASVS 5.0.0 条目级核对**（V13 配置 21 / V8 访问控制 13 / V16 日志 17 = **51 条**，逐条给结论与证据；统计 21✅/16🟡/5❌/9⚪）。条目编号与原文取自官方 tag `v5.0.0`（commit `60437a5`）经 **git 稀疏检出**落本地后解析（HEAD 已校验一致）。**产出三项发现并登记**：F-49 容器以 root 运行（Dockerfile 建了 appuser 却无 `USER`，CIS 4.1）→ 新任务 W1-9；F-50 授权失败的读操作未审计（GET 403 不落库）、F-51 审计详情未转义换行（日志注入）→ 新任务 W4-9 | security-review.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 8（合规化计划 W4-8 **完成 6/6 域**）：`security-review.md §十七` 补齐 **V6 认证 47 / V7 会话 19 / V9 自包含令牌 7**（新增 17.6~17.8 与 17.9 发现表），全量统计更新为 **124 条：49✅ / 29🟡 / 18❌ / 28⚪**。取数改用 `api.github.com` 内容接口 + 本地 base64 解码落盘（sha 与首轮一致）。**新增两项发现**：F-52 无口令强度下限与弱口令校验、F-53 无自助改密且管理员可直接设定口令 → 新任务 W4-10 | security-review.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 9（合规化计划 W4-9）：审计中间件覆盖**带凭证的 401/403 读请求**（F-50，该路径改为 `await` 落库：罕见路径 +审计不宜丢失；写路径仍 `create_task`）；`log_service.escape_control` 控制字符转义（F-51，应用于 `username`/`path`/`ip` 与 `sanitize_detail` 字符串分支）。新增 `backend/tests/test_audit_denials.py`（6 用例，用**文件库 + stdlib sqlite3** 绕开异步连接跨事件循环问题）。**完整基线 140 passed + 74 subtests、exit 0、0 warnings**；教训记入 ai-checklist 第 39 条（create_task 副作用跨用例泄漏 → 失败点不固定先疑竞态）| main.py, log_service.py, test_audit_denials.py, CHANGELOG.md, security-review.md, ai-checklist.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 10（合规化计划 W4-10）：新增 `backend/app/core/password_policy.py`（纯逻辑口令策略）——**删除**原「必须同时含字母和数字」规则（违反 ASVS 6.2.5），改为长度 8–128 + 上下文词表 + 不得含登录名 + 非单一重复字符；`schemas/config.py` 改调策略；新增 `POST /api/v1/auth/password` 自助改密（`auth_service.change_own_password`：校验当前口令、改密后 `token_version+1` 使旧令牌全失效）；新增 `tests/test_password_policy.py`（13 用例，纯标准库）与 5 条接口级用例。**更正首轮 ASVS 审计的两处误判**（6.2.1 误判未满足、6.2.5 误判满足，均因只审 service 未审 schema），统计重算为 52✅/29🟡/15❌/28⚪。**基线 158 passed + 84 subtests、0 warnings** | password_policy.py, schemas/config.py, schemas/auth.py, auth_service.py, api/v1/auth.py, test_password_policy.py, test_api_endpoints.py, CHANGELOG.md, security-review.md, ai-checklist.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | 文档/门禁同步：`AGENTS.md §2.2` 对整改计划的描述去掉会失效的固定编号区间（原写「F-01～F-42」，实际已到 F-53）改为「F 编号持续追加」；新增 `scripts/check_plan_integrity.py` 并接入 CI，登记为计划任务 W2-9（§5/§7 成对）；计划 §8 补第 8 组「仓库级门禁脚本」验收命令（此前 §8 只覆盖 git/构建/部署/运行时，未收录 4 个门禁）；`memory-bank/progress.md` 的 `scripts/` 树行由枚举改为按类描述（原枚举漏 `check_requirements_pins.py`、`check_env_docs.py`）| AGENTS.md, compliance-remediation-plan.md, progress.md, architecture.md, ai-checklist.md |
| 2026-10-02 | Wave 4 批次 11（合规化计划 **W4-11 自助改密前端入口**）：新增 `frontend/src/components/account/PasswordChangeDialog.vue` 与 `utils/passwordForm.ts`（纯校验闸门）、`AppHeader.vue` 菜单入口；修正 `http.ts` 把改密 401 误判为登录过期的问题；`vitest.config.ts` 补 `@vitejs/plugin-vue`（此前 `.vue` 用例无法加载）。新增 16 条前端用例（9 纯逻辑 + 7 组件），**`npm run test` 60 passed / 7 文件、exit 0、无 unhandled error**；lint 0 error；`vue-tsc` + vite build exit 0。**边界**：无浏览器，页面交互未验收。教训记入 ai-checklist 第 43/44/45 条 | PasswordChangeDialog.vue, passwordForm.ts, AppHeader.vue, http.ts, auth.ts, vitest.config.ts, CHANGELOG.md, compliance-remediation-plan.md, architecture.md, progress.md |












---

## 使用说明

1. **开发前**：阅读本文档了解项目结构，然后按需阅读具体文档
2. **更新文档后**：必须同步更新本文档的"文档说明"和"更新记录"
3. **新增文档**：必须在本文档中添加对应说明

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
| 2026-10-02 | Wave 2 批次 12（合规化计划 **W2-10 陈旧绝对路径门禁脚本化** + 计划 **§9 验收清点**）：新增 `scripts/check_stale_paths.py`（原检查只写在 CI YAML，本地不可执行），CI 与本计划 §8 均改为调用它，本地与 CI 口径一致；计划新增 §9「验收清点」，按「本机已执行并通过 / 本机不可执行 / 待决策」三张表列出全部验收项与阻塞原因 | check_stale_paths.py, ci.yml, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 13（合规化计划 **W4-12 规范复核**，产出并修复 **F-54**）：按 `AGENTS.md §3.3` 第 5 条 grep 旧值复核，发现前端 `ConfigGuildPanel.vue` 仍强制「含字母和数字」而后端已放开组成限制（前端拦、后端收）→ 改为复用 `utils/passwordForm` 共用谓词；同步 `GuildCreate` 字段描述、`security-review.md` M-3 修订说明、`tech-stack.md`（登记 `@vue/test-utils`）、`CONTRIBUTING.md`（本地门禁 1→5 道）、`design-document-v2.md`（权限矩阵 + §4.7 登记自助改密）、两端 docs README | ConfigGuildPanel.vue, passwordForm.ts, schemas/config.py, CONTRIBUTING.md, tech-stack.md, security-review.md, design-document-v2.md, frontend/docs/README.md, backend/docs/README.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 14（合规化计划 **W2-11**）：新增 `scripts/check_doc_numbers.py`（8 条自检，真值取自代码）——校验「N 张表」「N 个 Alembic 迁移」「database-design vX.Y」三类当前态声明；本计划 §8 与 CI `repo-hygiene` 同步接入（门禁 5→6 道）、`CONTRIBUTING.md` 命令清单同步。**修正两处旧值**：`backend/docs/README.md`（database-design v1.8→v1.9）、`memory-bank/tech-stack.md`（摘要行 Python 3.13→3.11）。教训记入 ai-checklist 第 48 条 | check_doc_numbers.py, ci.yml, CONTRIBUTING.md, tech-stack.md, backend/docs/README.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 2 批次 15（合规化计划 **W2-12**）：`scripts/check_env_docs.py` 扩展为**双向落地校验**——在原「代码 ↔ `.env.example`」之外，新增「`.env.example` 的每个键必须在 `DEPLOY.md` 出现」；`DEPLOY.md §六` 表格补全并加「表格口径」说明；自检 11→14 条。**实测证据**（`git show HEAD:DEPLOY.md` + 同一取键函数）：修复前有 7 个键未在部署文档出现 | check_env_docs.py, DEPLOY.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 16（合规化计划 **W4-13 容器与拓扑声明核实**，并更正 **F-49**）：核对 `nginx.conf`（内层构建输入）与 `nginx.conf.example`（边缘模板）职责分工——无重复维护 ✓；compose 与 `DEPLOY.md §二` 的差异属**本地演示 vs 生产单层 TLS**的设计意图（两侧均已写明）✓；`.gitignore` 第 99 行为注释、无残留忽略规则 ✓。**更正 F-49**：后端 `entrypoint.sh` 已用 `exec gosu appuser` 降权（原「后端以 root 运行」有误），仅前端成立（无 `USER`）→ W1-9 范围收窄为前端 | compliance-remediation-plan.md, security-review.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 17（合规化计划 **W4-14 威胁模型与部署声明复核**）：逐行核对 `frontend/nginx.conf` 与 `DEPLOY.md §二` 的四项声明（gzip / `/assets/` immutable / `index.html` no-store / `client_max_body_size 20m`）**全部为真**；抽查 `security-review.md §十六` STRIDE「现有控制」6 条数字（800 / 5000 / 5MB / `^https?://` / 日志保留 / 登录限流 5·5）**全部准确**；**更正一条过时的残余风险**——第 4 行「无口令复杂度要求」在 W4-10 实施口令策略后已不成立，改为「无 MFA」并补齐现有控制，同步更正 16.3 两处 | security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 18（合规化计划 **W4-15 ASVS 判定行抽样复核**）：抽样 §17 的 124 条判定（优先挑引用 F 编号/写着未做的行），**更正 3 处过时判定**——`13.3.2` ❌→🟡（后端 gosu 已降权，仅前端 root）、`16.3.2` 🟡→✅（F-50 已修）、`16.4.1` 🟡→✅（F-51 已修）；另反向验证 5 条 ✅ 行全部为真；统计重算为 **54✅ / 28🟡 / 14❌ / 28⚪** | security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 19（合规化计划 **W4-16**）：新增 `scripts/check_verdict_sync.py`（自检 10 条）——从计划 §4 取已修复的 `F-<n>`，扫描 `security-review.md §17` 判定行，判定非 ✅ 却引用已修复编号即报告；引入 `（残留判定：…）` 显式豁免；用 `HEAD~1` 真实历史反向验证（精确报出第 38 轮修掉的 `16.3.2`/`16.4.1`，不误报 `13.3.2`）；接入 CI 与计划 §8/§9.1、`CONTRIBUTING`（门禁 6→7 道）| check_verdict_sync.py, ci.yml, CONTRIBUTING.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 20（合规化计划 **W4-17**）：抽样复核 `§17.6~17.8`（V6/V7/V9，73 条，此前未抽）——更正 `6.1.2`（❌→🟡：口令上下文词表已在 `password_policy.CONTEXT_WORDS`，只是未成文）与 `9.2.3` 的「待办/取舍」措辞矛盾；统计重算为 **54✅ / 29🟡 / 13❌ / 28⚪**；给 `check_verdict_sync.py` 补**反向方向**（自称已修复但计划未标修复 → 报矛盾），自检 10→13 条 | security-review.md, check_verdict_sync.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 21（合规化计划 **W4-18**）：`DEPLOY.md §六` 新增「**关键秘密清单**」（7 类秘密的存放位置/访问边界/泄漏影响 + `git check-ignore -v` 验证命令）与「**秘密轮换与泄漏处置**」（周期建议、6 类秘密的轮换命令与验证、泄漏处置四步），闭合 ASVS `13.1.4`（🟡→✅）并改善 `13.3.4`（❌→🟡）；修 **F-55**：`frontend/.dockerignore` 补 `.env*`、`.gitignore` 补 `.env.development` 并显式 `!.env.example`（双向验证：`.env.development` 命中忽略、`.env.example` 不被忽略且跟踪状态不变）；统计重算为 **55✅ / 29🟡 / 12❌ / 28⚪** | DEPLOY.md, frontend/.dockerignore, .gitignore, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-02 | Wave 4 批次 22（合规化计划 **W4-19**）：成文三份「清单型」控制——`security-review.md §15.5 通信需求清单`（入站/容器间/卷/出站/构建期/宿主运维面/用户外链，含「服务端不抓取用户 URL」的全仓检索证据）、`DEPLOY.md §四 逐层日志清单`（边缘/内层/backend/审计表/告警五层的载体·格式·留存·检索方式）、`security-review.md §十八 安全事件清单`（11 类事件 + 检测信号 + 响应动作 + **自动化状态如实标注**）；ASVS 判定 `13.1.1`/`16.1.1`/`16.3.3` 🟡→✅，统计重算为 **58✅ / 26🟡 / 12❌ / 28⚪** | security-review.md, DEPLOY.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 仓库卫生（发现 **F-60**）：`git add -A` 把 `vue-tsc` 产物 `frontend/tsconfig.node.tsbuildinfo` 一并提交；`.gitignore` **已补** `*.tsbuildinfo`/`.eslintcache`；**移出版本库属 git 删除操作，按 §5 待用户授权 → 登记 W2-13**；教训记入 ai-checklist 第 68 条 | .gitignore, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 34（**W4-22 文档引用存活核对**，新增检查）：`scripts/check_doc_refs.py`（自检 18/18）扫描 26 个文档的 **942 处**反引号引用 → 有效 860、缺失 44、行号越界 0、歧义 38；**44 条缺失中 37 条为故意不存在**（运维脚本/运行时数据/改名历史/占位符/忽略目录/容器路径）→ **不接入门禁、保持报告模式**；两条真引用（`styles/medals.css`、`verify_e2e.py`）已核实不存在并在原文档标注「已移除」；工具自身 3 个缺陷（`lstrip` 误用 ×2、glob 误抽）已修并补回归样例；教训记入 ai-checklist 第 69 条 | check_doc_refs.py, code-ui-audit-2026-09.md, data-analysis-complete.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 35（公开前**仓库密钥扫描** + **F-62 修复**）：扫描 399 个跟踪文件与 git 全历史——**历史无任何真实密钥** ✓（无 `.env`/`*.pem`/`*.key` 提交、`jsdz` 零命中、5 个 `SECRET_KEY=` 提交逐个复核为 0 处真实赋值 ✓）；发现并修复 **F-62**：`_secret_key_is_weak` 的 hex 豁免通道放过了 CI 的 `0123456789abcdef…`（零熵）✗ → 增加 `_hex_is_low_entropy`（周期性 + 不同字符数 <8）+ 显式封禁 + `HexEntropyTest` 4 用例；登记 **F-61**（默认 `admin123` 在自身黑名单中）与 **W1-14**；`security-review.md` 新增 **§14.9**；教训记入 ai-checklist 第 70 条 | config.py, test_config_gate.py, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 36（**F-63**：计划结构 + 验收数字校正）：发现计划有**两个 `## 9.`**（风险登记 / 验收清点）✗ → 验收清点重编号为 **§11**（1–11 唯一单调）+ 子节 9.x→11.x + 引用更新；**验收清点数字按本轮实测刷新**（后端 **178 passed + 89 subtests**、前端 lint **0 warning**、构建 **≈8.4s（vite 6.4.3）**、扫描 **360** 个跟踪文件、复跑清单补到 **7 道**）；`check_plan_integrity` 新增**章节编号唯一性检查**（2 条自检样例 + 反向验证）；教训记入 ai-checklist 第 71 条 | compliance-remediation-plan.md, check_plan_integrity.py, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 37（**F-64**：技术栈权威源回填 + 交叉核对门禁）：`tech-stack.md` 四处漂移（`Vite 5.x`→**6.x**、`Pillow 11.x`→**12.x**、`Vitest 3`→**4**（并删除已失效的「须为 3.x」约束）、lint `10 warning`→**0**）已按实测回填，另修 `passlib` 残留表述与 `；；`；`check_doc_numbers` 新增 **tech-stack ↔ 清单实际版本**交叉核对（`real_pins()`/`check_tech_stack()`，含反向验证）；教训记入 ai-checklist 第 72 条 | tech-stack.md, check_doc_numbers.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 38（**F-65**：模板作用域说明；三轮「疑似漂移」核实后**均不成立**）：为 `.env.example`（部署权威）与 `backend/.env.example`（本地参考）互相注明作用域/权威关系（**不改值**）；结清 `ai-checklist §3.1` 自 2026-08-26 悬空的检查项；核实确认「file-length 豁免表行数」是**登记基线 + 20% 容差**（非漂移）、`start.bat` 首次启动即提供 README 所述默认账号；教训记入 ai-checklist 第 73 条 | .env.example, backend/.env.example, ai-checklist.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-03 | 批次 39（**F-66**：§8 回归命令清单校正 + 全量回归复核）：§8 补 `npm run lint`/`npm run test`、`check_commit_msg.py`、`check_doc_refs.py`（标注**仅报告**），删除「会因缺 nginx.conf 失败」等过时说明与**不可运行的 `mypy app`**（tech-stack 记其尚未引入），并声明 §8 为**权威清单**；本轮全量回归全绿（pytest **178 passed + 89 subtests**、前端 60 passed/7 文件、lint 0 warning、build exit 0、7 道门禁自检全通过）；教训记入 ai-checklist 第 74 条 | compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 40（**F-67 台账缺口** + 机会式扫描**未发现新缺陷**）：补齐 W2-3 遗留项的任务登记——新增 **W2-14**（lint/format/类型检查收紧：vue `flat/recommended` + Prettier 一次性格式化、ruff `I`/`UP`/`B`/`E501`/`format`、评估引入 `mypy`）；同轮三个候选经核实**全为检测器误报**（模块 docstring 判据漏了编码声明行、CHANGELOG 中文标题属有意翻译、AGENTS 对 `.agent/rules/*.md` 用通配）；教训记入 ai-checklist 第 75 条 | compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 41（**F-68**：CI 静态审计）：`ci.yml` 补齐 `check_file_length --self-test`（此前 7 道门禁中唯一未跑自检的一道）并本地等价复跑通过；把过时的「后续扩展（W2-2/W2-3 之后…）」注释改写为**现状说明**（含仍未接入的 mypy=W2-14、基座版本=W1-5/W1-7）；确认 `check_doc_refs.py` 未被接入 CI（刻意保持仅报告）；教训记入 ai-checklist 第 76 条 | .github/workflows/ci.yml, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 42（新角落扫描**未发现真缺陷**；补验 CI 未跑步骤）：确认 `*.db`/`data/` 未被跟踪**且历史从未提交** ✓、`.gitattributes` 覆盖二进制且索引 **0 CRLF** ✓、两份 `.dockerignore` 与 Dockerfile 自洽（含 `--from=build` 语义）✓、`entrypoint.sh` 由 Dockerfile `chmod +x` 兜底 ✓；本地补验并回填 §11.1：`alembic upgrade head`（**12 张业务表** ✓）、`app.main` 导入 ✓、**生产弱密钥启动门禁经真实 lifespan 拒绝启动** ✓；四个自查误报（含启动期/导入期测法陷阱）记入 ai-checklist 第 77 条 | compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 43（**F-69** 自查工具覆盖缺口 + 提交规则链一致性核对）：`check_doc_refs.py` 的 `SCAN` 补入 `backend/docs/README.md`/`frontend/docs/README.md`（此前遗漏），补后重跑确认其引用 **4 + 5 条全部存活** ✓；逐条核对【权威源 `.agent/rules/git-commit-message.md` ↔ 执行者 `check_commit_msg.py`】：10 个 type、scope 必填、摘要 ≤50、至少一个中文、禁用短语、放行前缀**全部一致** ✓；教训记入 ai-checklist 第 78 条 | scripts/check_doc_refs.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 43b（**F-70** 噪声口径）：`check_doc_refs.py` 新增 `strip_history_rows()`，排除带日期的更新记录行（与 `check_doc_numbers` 同款口径）——修复前缺失数随记录增长而从 44 涨到 65（新覆盖文档贡献 0）；教训记入 ai-checklist 第 79 条 | scripts/check_doc_refs.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 44（**F-71** 进度权威口径 + bash 语法检查复验）：`AGENTS §2.2` 两文档定位改为「功能点勾选清单」并指向 `progress.md`（消解与 §3.4 的矛盾）；两 `docs/README.md` 进度跟踪节顶部补权威口径说明；`§8` 的 shell 语法检查命令补 **Git for Windows bash 显式路径**（本机 bash 不在 PATH，否则无法复现）；复验 `deploy.sh.example`、`backup-db.sh.example`、`release-archive.sh.example`、`entrypoint.sh`、`.githooks/commit-msg`、`install_git_hooks.sh` **全部语法 OK** ✓；核实行数限额类别与门禁完全对齐、DEPLOY 的 `.example` 复制步骤齐备；教训记入 ai-checklist 第 80 条 | AGENTS.md, backend/docs/README.md, frontend/docs/README.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 45（**F-72** 数据模型权威源漏列）：以「空库迁移 + `PRAGMA table_info`」为真值，逐列核对发现 `database-design.md` 漏登 **5 列**（`guilds.icon_char`、`users.token_version`、`match_data.round_no`、`schedules.profession_config`、`recordings.note`），文档全文 0 次提及、§4 更新记录停在 2026-09-20 ✗ → 已按 `models/**` + `alembic/versions/**` 补入（含类型/约束/迁移 revision）并加 `match_data` 索引说明；新增 **W2-15**（列级核对护栏）；教训记入 ai-checklist 第 81 条 | database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 45 收口（**F-72 完成**：共补登 **6 个**未登记列 + 修复标题截断）：逐表双向终检（空库迁移 + `PRAGMA table_info`）最终 **两侧 0 差异** ✓；三处自伤（子串判存在 / 插入点含后续标题 / 验证用全局集合）记入 ai-checklist 第 82 条 | database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 46（**F-73** 角色矩阵 ↔ 端点守卫核对）：解析 **80 个端点**的 `Depends(...)` 与 `design-document-v2.md §3.2` 矩阵逐行比对——**写操作侧一致** ✓；**读取类不一致** ✗（`GET /attendance`、`GET /lineups` 实现为 `get_current_user` 且代码注释写明「帮众可查看」，而矩阵写帮众 ❌）→ 按 `AGENTS §3.2` **以代码为准对齐矩阵**并补「读取类接口口径」；`security-review.md` 新增 **§14.10**（差异表 + 处置 + **待用户确认是否收紧代码**）；**未改运行时鉴权**；教训记入 ai-checklist 第 83 条 | design-document-v2.md, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 47（**F-74** CHANGELOG 未发布小节重写）：核对 `v1.2.0..HEAD` **83 个提交**，发现「未发布」小节停在 2026-10-02，自助改密 / 健康检查 / 错误率告警 / 备份归档模板 / 长口令截断修复 / CSP 与静态资源收紧 / 前端工具链升级等**使用者可见变更全未记录** ✗，且以「Wave 0～2 已完成」承载进度（违反 `AGENTS §3.4`）✗ → 已按**使用者影响**重写四条分类（新增/变更/修复/安全），清除进度类表述并指向 `progress.md` 与整改计划；教训记入 ai-checklist 第 84 条 | CHANGELOG.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 48（UI 规范权威源核对：**无缺陷**，验证型收获）：`ui-style-guide.md` 令牌表 23 对值与 `theme.css` 实际声明逐对归一化比对——**22/22 真实令牌对完全一致** ✓（唯一差异 `--gold-gradient` 属记法差异）；颜色字面量归一化并纳入 `.ts` 图表色后，规范独有 **2** 个 ✓；已把该实测回填计划 §11.1；两处自查误报（记法差异 / 十六进制大小写未归一）记入 ai-checklist 第 85 条 | compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 49（**F-75 修复**：赛程级联删除漏删 `squad_adjustments`；**F-76 登记**）：`schedule_service.delete_schedule` 补齐 `SquadAdjustment` 删除（文档 §3.2 的 6 表规则），新增回归测试 `backend/tests/test_schedule_cascade.py`（6 张从表逐一断言 0 残留）；登记 F-76（`AppSidebar.vue` 硬编码侧边栏渐变色调，建议 token 化，零视觉变化但需人工视觉确认）；教训记入 ai-checklist 第 86 条 | schedule_service.py, test_schedule_cascade.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 50（**F-77 / F-78 修复**：删除路径同一族的三处缺陷）：`guild_service.delete_guild` 补删 `squad_adjustments`（文档要求删除帮会含「分析」）；`detach_member` 同步把 `attendance_records` / `recordings` 的 `member_id` 置空（推广项目既有的「防主键复用误关联」口径）；`backend/tests/test_schedule_cascade.py` 扩为 3 个用例类（赛程级联 / 帮会级联 / 成员解绑），全量 pytest 通过；教训记入 ai-checklist 第 87 条 | guild_service.py, game_id_request_lifecycle.py, test_schedule_cascade.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 51（核实为一致 + **新增语义回归测试**）：审查「更新/导入路径」——`match_data_service.import_csv` 按 `(schedule_id, round_no)` 先删后写（= 文档「一局一表、重导覆盖该局」✓）；`game_id_request_service.audit_request` 用条件更新原子占用申请（并发双审只成功一次 → 重复审核 409 且不覆盖首位审核人 ✓）、通过时同一事务按 `Member.name == old_game_id` 条件改名 ✓、成员已删除则 409 ✓；`member_service.update_member` 改名走 `invalidate_pending_by_member` + `record_admin_rename`（均 `flush`，不调用会自提交的辅助函数 ✓）。新增 `backend/tests/test_game_id_audit.py`（**6 个用例**）锁定这些文档化语义；期间发现 schema 级控制「通过需显式确认已核实身份、驳回必须填原因」并纳入用例；教训记入 ai-checklist 第 88 条 | test_game_id_audit.py, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 52（**F-79 修复**：补人部分唯一索引）：文档声称的补人唯一性（`attendance_records` 按 `(schedule_id, member_name, is_filler=1)`、`recordings` 按 `(schedule_id, member_name, round_number)`）实测**并不存在**（`PRAGMA index_list` 只有含 `member_id` 的唯一约束，`partial=0`；补人 `member_id` 为 NULL 且 SQLite 中 NULL 互不冲突）→ 唯一防线是应用层查重（有竞态）✗；新增迁移 `p0q1r2s3t4u5` 建两条部分唯一索引（可逆）+ 模型同步声明 + `test_filler_uniqueness.py`（4 用例）；迁移三态实测通过；文档同步（迁移数、head、§4 新增 v1.10 行）；并把既有自检与 head 解耦（改为 upgrade 被测 revision）；教训记入 ai-checklist 第 89 条 | alembic/versions, models/attendance.py, models/recording.py, tests/test_filler_uniqueness.py, selfcheck_migration_game_id.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 53（**F-79 反向验证**：新约束与业务路径兼容，无缺陷）：为确认补人部分唯一索引（迁移 `p0q1r2s3t4u5`）不会打断既有写入路径，新增 `backend/tests/test_attendance_import_paths.py`（5 用例）：重复 `import_formal`/`import_members` **幂等**（0 新增、全部 skipped）✓；重复添加补人抛**业务错误**（`AttendanceServiceError`，非数据库异常）✓；`ensure_recordings` 二次调用**不新增**（人数 × 局数）✓；导入 61 名正式成员按文档抛**上限错误**（60 人上限生效）✓。代码路径结论：三个导入函数先算 `new_members` 再校验容量 ✓、`add_filler` 有应用层姓名查重 ✓、`ensure_recordings` 以 `existing_map` 插入不存在者 ✓；教训记入 ai-checklist 第 90 条 | tests/test_attendance_import_paths.py, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 54（录屏审核状态机核对：**F-80 登记** + 权威源补迁移规则 + 6 用例）：新增 `backend/tests/test_recording_review_state.py`（6 用例全过）实测——未提交链接时通过/驳回均抛业务错误 ✓；已通过行**重新提交链接即回到 pending 并清空** `review_remark`/`reviewed_at` ✓；跨赛程 id 视为不存在 ✓；批量通过跳过未提交者（2 条中通过 1 条）✓；前端「驳回」入口只出现在 `v-if=row.url` 内 → 与后端约束一致 ✓。据此把状态迁移规则补进 `database-design §2.8` ✓，并登记 **F-80（P3）**：审核结论可被静默覆盖且**被清除的审核意见无持久化留存**（审计中间件只到请求级）；代码未改（属产品决策，待用户确认）；教训记入 ai-checklist 第 91 条 | tests/test_recording_review_state.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 55（排表导入语义核对：**F-81 登记** + 权威源补规则 + 5 用例）：`import_lineup` 的六条语义（不能自导入 / 源须属本帮会 / 源无排表 404 / 只导入选中小队 / 仅保留当前候选池成员（正式按 `member_id`、补人按姓名）/ 改名后以出勤库当前姓名替换旧快照）原先**只写在 docstring** ✗ → 已按实现补进 `database-design §2.7` 业务规则 ✓；新增 `backend/tests/test_lineup_import.py`（5 用例全过）钉住语义 ✓；顺带确认录屏待办「赛后 7 天」窗口在权威源（设计文档页面树）与前端口径一致 ✓（属显示提示类规则，实现位于前端 ✓）；教训记入 ai-checklist 第 92 条 | tests/test_lineup_import.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 56（联赛日程规则 + 日志保留核对：**F-82 登记** + 权威源补边界 + 6 用例）：核实 `rounds` 不可修改由 **schema 层**保证（`ScheduleUpdate` 不含该字段 + DB `CHECK 1-3`）✓、`round_results` 长度须等于 `rounds` 且取值限白名单 ✓、`profession_config` 需职业合法且 **0-60** ✓、日志保留 90 天且「启动即清 + 每日一次」✓（`main.py` 的 `sleep(24*3600)`）✓；上述**机制与边界原先未进权威源** ✗ → 按实现补进 `database-design §2.5` ✓；新增 `backend/tests/test_schedule_rules.py`（6 用例全过）钉住规则（含 `patch.object(log_service, "async_session_factory", ...)` 打桩以让 `clear_old_logs` 在 `:memory:` 库上真实生效）✓；确认 `round_results`/`LOG_RETENTION`/`clear_old_logs` 此前**无测试覆盖** ✓；教训记入 ai-checklist 第 93 条 | tests/test_schedule_rules.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 57（成员 Excel 导入规则核对：**F-83 登记** + 8 用例 + 边界口径补记）：先用 `git grep` 与断言清单确认既有覆盖（`selfcheck_member_exports.py` 的来源行/回导/空导出/文件名/403/出勤隔离 ✓、`test_excel_export_formula.py` 的公式注入 ✓），**不重复**；补测三条缺口——重名跳过、5000 行上限、`.xlsx` 扩展名与 5MB 大小双检 ✓；读实现后确认上限语义为「**最多 5000 行、第 5001 行拒绝**」（判定在追加之前）→ 改为**双向断言** ✓，并把该边界口径补进 `security-review` 威胁核对表第 10 行 ✓；新增 `backend/tests/test_member_import_rules.py`（**8 用例全过** ✓）；教训记入 ai-checklist 第 94 条 | tests/test_member_import_rules.py, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 58（**F-84 修复**：职业配置目标人数值域统一；含代码改动）：`target_count` 原先三层不一致——单职业端点仅 `ge=0`、**批量端点 `list[dict]` 零校验**、每赛程覆盖 0–60 ✗；已修：`utils/constants.py` 新增 `MAX_PROFESSION_TARGET = 999` ✓、单职业端点加 `le=999` ✓、批量入口改为 `list[ProfessionConfigItem]` 类型化 ✓、`config_service` 两路径服务层兜底 ✓、`database-design §2.3` 补记值域 ✓；新增 `backend/tests/test_profession_config_rules.py`（5 用例全过 ✓）；另核实备份/归档脚本模板（`set -euo pipefail`、默认 `DRY_RUN=1`、先 `PRAGMA integrity_check` 再拷出、`find -mtime +30 -delete` 轮转）与 `DEPLOY.md §五/§九`、`security-review` 第 9/16 行一致 ✓，并把 `bash -n` 静态校验加入计划 §8 回归清单 ✓；教训记入 ai-checklist 第 95 条 | schemas/config.py, services/config_service.py, utils/constants.py, tests/test_profession_config_rules.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 59（**F-85 修复**：排表唯一占位不变量；含代码改动）：`_validate_structure` 原先只校验 10 队/队序（进攻1×3、进攻2×3、防守1×2、防守2×2）/每队 6 槽/槽位序号，**不检查同一成员占用多个槽位** ✗（前端拖拽是「移动」故 UI 不会产生，直接调接口可写入，导致小队分析重复计数）；已修：增加去重校验（正式按 `member_id`、补人按归一化姓名；正式与补人同名合法 ✓），并新增 `backend/tests/test_lineup_structure.py`（10 用例全过 ✓，含 4 个结构分支、重复 id、重复补人、反向同名、经 `save_lineup` 的端到端）；`database-design §2.7` 补记结构与唯一占位规则；顺带核实 `guilds.icon_char` 的「最多 4 字符」与 schema `max_length=4`、前端 `maxlength="4"` 一致 ✓（非缺陷）；教训记入 ai-checklist 第 96 条 | services/lineup_service.py, tests/test_lineup_structure.py, database-design.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 59 补充（**F-85 后续：文件行数超限 → 拆分**）：给 `_validate_structure` 加唯一占位校验后 `lineup_service.py` 达 **309 行**、**超过服务层 300 行上限** ✗（`check_file_length` 门禁在提交前拦下 ✓）；按 `.agent/rules/file-length-rule.md` **拆分**而非申请豁免：抽出 `backend/app/utils/lineup_structure.py`（`empty_lineup_data` + `validate_structure`，64 行 ✓），`lineup_service` 仍**转出同名函数**（调用方与测试无需改动 ✓），行数回到 **260** ✓；此为 F-85 修复的收尾，教训并入 ai-checklist 第 96 条 ⑥ | lineup_service.py, utils/lineup_structure.py, tests/test_lineup_structure.py |
| 2026-10-03 | 批次 59 收尾2（**更正上一条记录 + F-86**）：上一条提交信息与记录称「已把 `utils/lineup_structure.py` 与 `tests/test_lineup_structure.py` 登记进 `progress.md` 目录树」，**实际未生效** ✗——该目录树是**按组注释行**（如 `├── utils/ # 工具函数（…）`）而非每文件一行，脚本的四次插入全部落空 ✓ → 本次**真实更新**：`utils/` 注释补 `lineup_structure` ✓；`tests/` 注释把「11 个模块」更正为 **24** 并补主题清单与「以 `git ls-files backend/tests/*.py` 为准」的指引 ✓（登记 F-86）✓ | progress.md, compliance-remediation-plan.md, architecture.md, progress.md |
| 2026-10-03 | 批次 60（审计日志时间口径核对：**F-87 登记** + 权威源补记 + 6 用例）：核实日志三端点均 `require_developer` ✓（=「仅开发者可查」✓）、`query_logs` 支持 username/guild_id/module/level/时间/分页 ✓，`candidate_pool` 以**出勤库** `status='normal'` 为准 ✓（= 文档口径 ✓，常驻库状态不参与筛选 ✓），`MEMBER_STATUSES = ["formal","substitute"]` ✓ 与文档一致 ✓；发现 `operation_logs.created_at` 实为 **naive-UTC**、统计按**北京时间**划分，而权威源未记载该约定 ✗、`get_log_stats` 无测试 ✗ → `§2.11` 补记时区约定 ✓，新增 `backend/tests/test_log_stats.py`（6 用例全过 ✓：午夜边界、深夜记录归属、7 桶由旧到新、窗口外第 8 天不计入、空库零值）；目录树测试模块数同步 24 → **25** ✓；教训记入 ai-checklist 第 97 条 | database-design.md, tests/test_log_stats.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 61（帮会创建语义核对：**F-88 登记** + 服务层口令兜底 + 7 用例）：核实 `create_guild` 为**单次事务**（帮会 → `{名}_admin` / `{名}_member` 双账号 → **全部职业配置 target 0** → 结尾一次 `commit()`）✓，初始密码经 `GuildCreate` 的 `validate_password` ✓（弱口令/上下文词表、不限字符组成 ✓），重名显式拒绝 ✓；发现事务边界与职业配置初始化**未进权威源** ✗、`DEPLOY.md` 的「阈值 0 表示禁用」与实现「**≤0**」不一致 ✗、该路径**零测试** ✗ → `database-design §2.1` 补记创建语义 ✓、`DEPLOY.md` 精确化 ✓、`create_guild` 加服务层口令兜底 ✓、新增 `test_guild_create.py`（6 用例全过 ✓，含**原子性决定性用例**：账号名冲突 → 帮会与职业配置零残留 ✓）；`candidate_pool`/日志权限口径一并核实为一致 ✓；教训记入 ai-checklist 第 98 条 | guild_service.py, tests/test_guild_create.py, database-design.md, DEPLOY.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 61 更正（**如实记录数字**）：上一条记录与提交信息写「`test_guild_create.py` 7 用例」，**实际为 6 个测试方法** ✗（`pytest --collect-only` 实测 6 ✓）→ 已更正三处记录中的计数 ✓；该轮结论（F-88 修复、原子性用例、服务层兜底、措辞精确化）不变 ✓ | progress.md, compliance-remediation-plan.md, architecture.md |
| 2026-10-03 | 批次 62（账号管理安全行为核对：**F-89 登记** + 7 用例）：核实代码防线完整 ✓（`create_account` 角色白名单 `["admin","member"]` 防提权 ✓、`update_account` 不接受 role ✓、`update_account_status` 状态白名单 ✓、`delete_account` 拒绝开发者 ✓、admin 因 `guild_id` 过滤碰不到开发者 ✓、`_build_account_out` 仅 developer 保留 `plain_password` ✓），且帮会边界**已有** `selfcheck_security_fixes.py` 覆盖 ✓（不重复）；但**角色白名单与明文脱敏零测试** ✗ → 新增 `backend/tests/test_account_rules.py`（7 用例全过 ✓）；教训记入 ai-checklist 第 99 条 | tests/test_account_rules.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 63（前端职业常量核对：**F-90 登记** + 消除副本 + 锁定测试）：核实前端 `PROFESSIONS` 与后端 `backend/app/utils/constants.py` **逐项同序一致** ✓（11 种）；UI 规范 §7 的 11 对（色值 + 文字颜色）与 `utils/profession.ts` **完全吻合** ✓（`profTagStyle` 的 `#fff`/`#333` 亦与规范一致 ✓）；发现**同一份色表被复制两份** ✗（`analysis.ts` 的副本无测试覆盖）、注释把权威源写成 **§9** ✗（实为 §7）、`analysis.ts` 的 `profColor` 兜底 `#999` 与统一来源 `#c9a13b` 不同 ✗ → `analysis.ts` 改为引用并转出统一来源 ✓（值一致故零视觉变化 ✓）、`§9` → `§7` ✓、新增 `professionSource.spec.ts`（色值/文字颜色/职业清单同序/单一来源同一对象 ✓）；并跑 `npm run lint` + `npm run test` + `npm run build` ✓；另核实改名申请**提交侧**已被 `selfcheck_game_id_requests*.py` 覆盖 ✓（不重复）；教训记入 ai-checklist 第 100 条 | analysis.ts, profession.ts, professionSource.spec.ts, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 64（前端职业单一来源核对：**F-91 登记** + 两处消重 + 权威源补记）：发现 `lineupBoard.ts` 的 `PROF_ORDER` 是**第二份 11 职业数组** ✗（6 处引用、零测试）、`TANKS` 与 `.vue` 标题重复 ✗、前后端职业分类语义不同且未记载 ✗ → `PROF_ORDER` 上移到 `utils/constants.ts` 并由 `lineupBoard` 转出 ✓（既有 import 零改动，且该文件在行数豁免清单中、移出后变短 ✓）、`TANKS` 导出为 `TANK_PROFESSIONS` 且标题改为派生 ✓（渲染文本不变 ✓）、两种分类补记进 `data-analysis-complete.md` ✓、`professionSource.spec.ts` 增加 3 条锁定 ✓；赛程排序（前端 proximity vs 后端 `match_time desc`）语义不同属正常 ✓；验证 `npm run lint` / `test` / `build` ✓；教训记入 ai-checklist 第 101 条 | constants.ts, lineupBoard.ts, professionDetailCharts.ts, ProfessionDetailTab.vue, professionSource.spec.ts, data-analysis-complete.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 65（前后端字段对账：**F-92 登记** + 新增报告型校验脚本）：临时对账先误报（跨行正则吃掉**每类首个字段**→ `id` 全部误报 ✗；`MemberInfo` 配对写成 `MemberBase` 而非 `MemberOut` 再次误报 ✗），读源码（`AttendanceRecordOut.id` 在第 9 行 ✓）后推翻 ✓ → 新增 `scripts/check_type_drift.py`（**行式解析** ✓、继承链 ✓、配对表自检 ✓、`--strict` 可选 ✓、`--self-test` **7/7** ✓），实跑 **16 对模型无漂移** ✓，并做**注入式反向验证**（`ghost_field` 被检出 ✓、严格模式 exit 1 ✓、还原后恢复 ✓）；已登记 §8（仅报告 ✓）；教训记入 ai-checklist 第 102 条 | scripts/check_type_drift.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 65 收尾（**如实更正**）：上一条提交信息称「代码目录树补记该脚本」，实际**未生效** ✗——我的守卫用「整文件是否含 `check_type_drift`」判断，而刚写入的**记录行**里就含该字符串 → 守卫误判为已登记 ✓✗（「守卫匹配错对象」，见第 96 条 ⑦ / 第 102 条 ④ 同源）。本次改为**只在目录树区块内定位 `scripts` 行**并补记 ✓，写入后复查目标行 ✓ | progress.md |
| 2026-10-03 | 批次 66（前端 API ↔ 后端路由对账：**F-93 登记** + 新增报告型脚本）：新增 `scripts/check_api_paths.py`（行式解析、路径参数归一为 `{p}` 只比形状、含全局前缀、`--self-test` **9/9** ✓、默认报告型、`--strict` 检出即非零、`--list-unused` 列信息项）；实跑 **81 条后端路由 vs 77 个前端唯一调用 → 无失配 PASS** ✓；**注入式反向验证**通过（临时加 `/definitely-not-a-route` → 检出 + 严格模式 exit 1 + 还原恢复 ✓）；发现 4 条未被前端调用的路由（`/health` ×2 属正常 ✓；**`POST /api/v1/developer/guilds` 与 `.../{id}/accounts` 疑与 `/config/guilds` 重复** ✗，**仅登记待确认**）；清理脚本内一处死循环 ✓；登记 §8（仅报告）并补记代码目录树 ✓；教训记入 ai-checklist 第 103 条 | scripts/check_api_paths.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 67（数据库权威源 ↔ 模型对账：**F-94 登记** + 新增报告型脚本）：新增 `scripts/check_schema_drift.py`（行式解析、模型侧只认 `mapped_column` 排除 `relationship` ✓、按 class/表名边界 flush ✓、双向报告 + 单侧表报告 ✓、`--self-test` **7/7** ✓、默认报告型、`--strict` 非零）；实跑 **12 张表 vs 12 张表、字段完全一致 PASS** ✓（**独立证实 F-72 已修复** ✓）；**注入式反向验证**通过（删 `guilds.icon_char` → 检出 + 严格模式 exit 1 + 还原恢复 ✓）；**自检先于实跑逮到解析器缺陷** ✗✓（新 `__tablename__` 不 flush → 一文件多表只留最后一张 → 已按边界 flush 修正 ✓）；登记 §8（仅报告）与代码目录树 ✓；教训记入 ai-checklist 第 104 条 | scripts/check_schema_drift.py, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |
| 2026-10-03 | 批次 67 更正（**如实记录数字 + 说明误判来源**）：上一条提交信息与三处记录写「`--self-test` **5/5**」，实际首版自检**未通过**（2 条失败 ✗）→ 我先把「5/5」写进了提交 ✗；根因是**我的自检期望错**（不是脚本错 ✓）：`analyze()` 只比对**共同存在**的表 ✓，仅文档有的表由 `tables_only_in_one()` 报告 ✓，而我却期望它也出现在 `analyze` 里 ✗。修正后自检为 **7 条**（文档解析 2 条 / 关系属性排除 / 模型侧漂移 / 仅文档表归属与字段解析 / 文档侧漂移 / 单侧表 / 一致不误报 ✓），**7/7 通过** ✓，实跑仍 PASS ✓；已把三处记录的 5/5 更正为 7/7 ✓。教训：**自检必须实跑看到 7/7 再写进提交信息** ✗✓ | scripts/check_schema_drift.py |




















































---

| 2026-10-02 | Wave 4 批次 23（合规化计划 **W4-20**）：`frontend/nginx.conf.example` 的 CSP `connect-src` 由 `'self' https:` **收窄为 `'self'`**（依据：前端无跨域 XHR/fetch/WS、baseURL 同源相对路径、唯二 https 链接为备案号 `<a href>` 顶层导航），文件头写明依据/收益/边界；`security-review.md` `13.2.4` 🟡→✅、CSP 相关行补 W4-20 完成标注，统计 **59✅ / 25🟡 / 12❌ / 28⚪** | nginx.conf.example, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-02 | Wave 4 批次 24（合规化计划 **W4-21**）：`frontend/nginx.conf` 的 `/assets/` 增加**静态资源扩展名白名单**（依据 `npm run build` 产物实测扩展名集合）+ 非白名单 `return 404` 兜底，并按 nginx 语义确认缓存头仍继承；`security-review.md` `13.4.7` 🟡→✅，统计 **60✅ / 24🟡 / 12❌ / 28⚪**；计划 §9 补本轮全量回归结果与「nginx 配置无自动校验」缺口；**主动放弃**给 Dockerfile 加 `nginx -t`（构建期解析 `backend` 主机名会失败，无 Docker 无法验证）| nginx.conf, security-review.md, compliance-remediation-plan.md, architecture.md, progress.md |

| 2026-10-02 | 收口核对（批次 25，**无代码改动**）：重跑全量回归与 7 道门禁（全绿）；按计划 §7 现场解析真实完成度并纠正汇报口径——**Wave 2 实为 11/12**（`W2-8` props 债始终待开始，我此前多轮误报 12/12），Wave 0 8/9、Wave 1 3/9、Wave 3 4/6、Wave 4 21/21，**合计 47/57**；教训记入 ai-checklist 第 60 条（进度数字必须现场解析） | ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 26（合规化计划 **W1-8 续**）：**Pillow `11.1.0` → `12.3.0`**（上游依据 `GHSA-62p4-gmf7-7g93` = `CVE-2026-54058`，high，受影响 `< 12.3.0`；**可达性：不可达**——只生成导出图、全仓无 `Image.open`）；实测导入级兼容 + 后端全量 **158 passed + 84 subtests exit 0**；`security-review.md` 新增 §14.7；新登记 **F-56**（导出路径无测试覆盖）、**W1-10**（bcrypt 直连、移除 passlib）、**W1-11**（补 image_export 覆盖） | requirements.txt, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 27（合规化计划 **W1-11**，收口 **F-56**）：新增 `backend/tests/test_image_export.py`（6 用例）固定 `draw_members_png` 的行为契约——PNG 合法性、宽度恒定、高度按模块常量独立重算、空列表不抛异常、正式/替补/副职业分支、人数上限守卫；全量 pytest **158 → 164 passed**；`security-review.md §14.7` 的测试缺口条目标注收口；教训记入 ai-checklist 第 62 条 | test_image_export.py, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 28（合规化计划 **W1-10**）：移除未维护的 **`passlib`**、改用 `bcrypt` 直连，`bcrypt` `4.0.1` → **`4.3.0`**；新增 `tests/test_password_hash_compat.py`（5 用例）；**过程中抓到并修复真实缺陷 F-58**（`bcrypt` 4.x 对截断哈希 Rust panic，`PanicException` 非 `Exception` 子类 → 格式预校验 + 宽捕获）；登记 **F-57**（72 字节静默截断）与 **W1-12**；`tech-stack.md`/`security-review.md §14.7` 同步；教训记入 ai-checklist 第 63 条 | security.py, requirements.txt, test_password_hash_compat.py, test_core_security.py, tech-stack.md, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 29（合规化计划 **W1-12**，收口 **F-57**）：口令改为**预哈希方案**——新哈希先 `base64(SHA-256(口令))` 再 bcrypt（`sha256$<bcrypt>`），任意长度口令完整参与，解除 72 字节静默截断；旧哈希仍走直连并在**登录时惰性升级**；**实测否决**「策略收紧到 72 字节」（中文仅 24 字符，违反 ASVS 6.2.9）与「立即升 bcrypt 5.0.0」（对 >72 字节连 `checkpw` 都报错 → 会锁死既有用户）；新增 `tests/test_password_hash_migration.py`（3 用例）并扩展兼容性用例；教训记入 ai-checklist 第 64 条 | security.py, auth_service.py, test_password_hash_compat.py, test_password_hash_migration.py, test_core_security.py, requirements.txt, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 30（合规化计划 **W1-8 收口**）：用 GitHub Advisory API 逐包核对**全部依赖公告**——后端 12 个固定依赖**受影响 0 条** ✓（Pillow 78 条公告修复版均 ≤12.3.0、starlette 最新上限 <1.3.1、python-jose critical 修复于 3.4.0）；前端 19 包运行期 0 条、开发期 6 条（vite/esbuild/vitest，**dev-only**，`vite.config.ts` 未设 `host` → 默认仅绑 localhost ✓ 已缓解）；`security-review.md` 新增 §14.8 全量核对表；登记 **F-59 / W1-13**（前端工具链跨大版本升级）；教训记入 ai-checklist 第 65 条 | security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 1 批次 31（合规化计划 **W1-13**，收口 **F-59**）：前端工具链升级——`vite` 5.4.21 → **6.4.3**、`esbuild` → **0.25.12**（随 vite 依赖）、`vitest` 3.2.7 → **4.1.11**；升级后逐包复核公告：**6 条中 5 条清除**，剩余 1 条（esbuild）经 API `withdrawn_at` **实证为上游已撤回**；回归证据 build exit 0 / test 60 passed / lint 0 error；`CONTRIBUTING.md` 补充换源指引；教训记入 ai-checklist 第 66 条 | frontend/package.json, frontend/package-lock.json, CONTRIBUTING.md, security-review.md, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

| 2026-10-03 | Wave 2 批次 32（合规化计划 **W2-8**）：用 `defineModel` 消除 **10 处 `vue/no-mutating-props`** 告警（4 个文件：`SquadCardsGrid`/`MemberTablePanel`/`MemberToolbar`/`LogFilterBar`）；因父组件为 `reactive` 常量、`defineModel` 就地写共享对象语义与改前一致 → **父组件零改动**；验证：lint **10→0**、`vue-tsc` exit 0、`build` exit 0、`test` 60 passed；**页面级交互验收仍待浏览器授权**；教训记入 ai-checklist 第 67 条 | SquadCardsGrid.vue, MemberTablePanel.vue, MemberToolbar.vue, LogFilterBar.vue, compliance-remediation-plan.md, ai-checklist.md, architecture.md, progress.md |

## 使用说明

1. **开发前**：阅读本文档了解项目结构，然后按需阅读具体文档
2. **更新文档后**：必须同步更新本文档的"文档说明"和"更新记录"
3. **新增文档**：必须在本文档中添加对应说明

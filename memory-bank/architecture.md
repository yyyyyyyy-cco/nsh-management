# 项目文档索引

## 文档结构总览

```
nsh-management/
├── .agent/
│   ├── docs/                         # 内部样例（比赛 CSV 入库；Excel 分析表仅本地）
│   ── rules/                        # AI 编码规则（已入库）
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
│   ├── ui-polish-plan.md         # UI优化方案文档
│   └── ui-style-guide.md         # UI风格参考文档
├── backend/
│   └── docs/README.md            # 后端模块开发文档
├── frontend/
│   └── docs/README.md            # 前端模块开发文档
├── AGENTS.md                     # AI 开发指南：规范/文档维护/进度追踪（自动读取）
├── DEPLOY.md                     # 部署文档（Docker Compose）
├── GIT-GUIDE.md                  # Git 管理规范
├── .gitignore                    # Git忽略规则
└── README.md                     # 项目说明
```

---

## 文档说明

### 1. 产品设计文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\design-document-v2.md`
- **作用**：定义产品功能、用户角色（developer/admin/member）、权限、页面结构、API接口、数据库设计等，整合UI设计规范（浅色雅金风）
- **状态**：当前唯一有效版本，开发以本文档为准
- **更新时机**：需求变更、功能调整时更新

### 1.1 UI风格参考文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\ui-style-guide.md`
- **作用**：定义「浅色雅金风（宣纸鎏金）」设计规范：色彩令牌、字体、组件规范、布局、动画、职业色映射；实现位置为 `frontend/src/styles/`（theme.css / element-plus.css / index.css）
- **更新时机**：UI 风格调整、设计令牌变更时更新

### 1.2 UI优化方案文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\ui-polish-plan.md`
- **作用**：记录 UI 优化方案（P0-P3 共 11 项优化清单：视觉层次/交互反馈/细节打磨/微动效）、CSS 新增动画族规范、卡片层级规范、文件变更清单、验收标准（2026-09-18 全部完成：P0–P3 11 项 + §2.5 代码质量 2 项 + 3 项可选项——表格密度切换/空状态 SVG 插画/职业标签 hover 微光；最终规范见 ui-style-guide.md §10）
- **前置文档**：`ui-style-guide.md`（权威视觉规范，本文档仅补充优化增量）
- **更新时机**：优化项完成或方案调整时更新

### 2. 数据库设计文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\database-design.md`
- **作用**：定义全部数据表结构（12 表，含 squad_adjustments、operation_logs、member_game_id_requests）、字段约束、索引、JSON存储结构及关键业务规则落表方案；当前版本 v1.9（含 developer 角色、plain_password、remark、title_remark、groups_remark、分析调整、操作审计、游戏 ID 修改申请）
- **更新时机**：表结构变更、业务规则调整时更新

### 3. 技术栈文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\tech-stack.md`
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
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\architecture.md`
- **作用**：整理项目所有文档的作用和目录，方便快速查找
- **更新时机**：每次更新其他文档后必须同步更新本文档

### 8. 实施方案文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\implementation-plan.md`
- **作用**：定义项目开发任务分解、模块依赖关系、开发阶段规划（2026-09-15 起转为历史规划存档，最新进度见 progress.md）
- **更新时机**：开发计划调整时更新

### 9. 项目进度文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\progress.md`
- **作用**：记录代码模块结构、开发进度、代码变更记录；当前阶段 7 已完成（功能增强与部署）
- **更新时机**：每次更新代码后必须同步更新本文档

### 10. 后端模块开发文档
- **路径**：`e:\code\@Cjy\nsh-management\backend\docs\README.md`
- **作用**：后端模块的需求说明、开发计划（全部 P0/P1/P2 已完成）、进度跟踪
- **更新时机**：后端每个功能点完成时更新

### 11. 前端模块开发文档
- **路径**：`e:\code\@Cjy\nsh-management\frontend\docs\README.md`
- **作用**：前端模块的需求说明、开发计划（全部 P0/P1/P2 已完成）、进度跟踪
- **更新时机**：前端每个功能点完成时更新

### 12. 部署文档
- **路径**：`e:\code\@Cjy\nsh-management\DEPLOY.md`
- **作用**：Docker Compose 部署全流程：架构、环境变量、部署步骤、运维（日志/升级/备份/恢复）、常见问题
- **更新时机**：部署配置（Dockerfile / nginx.conf / docker-compose.yml / .env 变量）变更时更新

### 13. 数据分析模块完整方案
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\data-analysis-complete.md`
- **作用**：数据分析模块规格与实施记录（2026-09-15 瘦身归档）：CSV 结构与字段映射、小队结构、16 项衍生指标公式、开发方案、ECharts 图表规划、实施记录与口径确认
- **更新时机**：数据分析模块功能调整时更新

### 14. 安全审查文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\security-review.md`
- **作用**：项目安全审查记录，涵盖认证、权限、数据安全等方面的审查结论与改进项（§一～九为 2026-08-20 全量审查；§十为 2026-09-18 用户隔离定向修复 F-1～F-5、验证范围与未解决项更正）
- **更新时机**：安全相关变更或审查时更新

### 15. AI 项目完整上下文文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\ai-context.md`
- **作用**：根目录 `AGENTS.md` 的完整扩展版，为 AI 助手提供项目全貌：功能模块、技术栈详情、编码规范、Git 工作流、文档体系、安全要点、已知待优化项
- **更新时机**：项目架构、技术栈、规范发生重大变更时更新

### 16. AI 操作检查清单
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\ai-checklist.md`
- **作用**：记录 AI 在本项目中犯过的错误和容易遗漏的联动点（版本号散落、文件重命名联动、目录树同步、.env 对齐等），每次修改前必读
- **更新时机**：发现新的遗漏模式时补充

### 17. AI 开发指南（入口文档）
- **路径**：`e:\code\@Cjy\nsh-management\AGENTS.md`
- **作用**：AI 入口文档（原 `CLAUDE.md`，2026-09-15 更名扩充）：项目简介、权威源映射、各文档维护时机、文档同步与进度追踪流程（自检清单）、代码/Git/安全摘要、AI 行为约定
- **更新时机**：项目结构、规范或维护流程变更时更新

### 18. 成员战绩与战报实施方案
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\stats-report-plan.md`
- **作用**：成员详情战绩页（管理员独立页）与单场图文战报的实施方案（2026-09-17 已实施完成，待浏览器验收）：决策记录、交互设计、技术方案、文件清单、验证方案、二期规划
- **更新时机**：方案调整或实施完成时更新

### 19. 游戏 ID 改名申请与战绩关联设计
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\design-game-id-change.md`
- **作用**：帮众提交游戏 ID 修改申请、管理员审核、通过后同步常驻库，以及个人战绩/成员详情新旧 ID 合并查询专项设计（2026-09-20 设计确认并实施完成，待浏览器验收；实施与验证状态见 progress.md）：背景决策、业务流程、API 合同、关联算法与冲突边界、权限事务、前端交互、验证方案
- **更新时机**：功能调整或实施完成时更新

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

---

## 使用说明

1. **开发前**：阅读本文档了解项目结构，然后按需阅读具体文档
2. **更新文档后**：必须同步更新本文档的"文档说明"和"更新记录"
3. **新增文档**：必须在本文档中添加对应说明

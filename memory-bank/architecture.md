# 项目文档索引

## 文档结构总览

```
nsh-management/
├── .claude/
│   └── rules/
│       ├── code_rule.md              # 项目规则
│       ├── file-length-rule.md       # 代码文件长度规则
│       ├── function_rule.md          # 模块开发文档规则
│       └── git-commit-message.md     # Git 提交信息规范
├── memory-bank/
│   ├── architecture.md           # 本文档 - 项目文档索引
│   ├── data-analysis-complete.md # 数据分析模块完整方案
│   ├── database-design.md        # 数据库设计文档
│   ├── design-document-v2.md     # 产品设计文档（当前主文档）
│   ├── implementation-plan.md    # 实施方案文档
│   ├── progress.md               # 项目进度文档
│   ├── tech-stack.md             # 技术栈文档
│   └── ui-style-guide.md         # UI风格参考文档
├── backend/
│   └── docs/README.md            # 后端模块开发文档
├── frontend/
│   └── docs/README.md            # 前端模块开发文档
├── DEPLOY.md                     # 部署文档（Docker Compose）
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

### 2. 数据库设计文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\database-design.md`
- **作用**：定义全部数据表结构（9 表）、字段约束、索引、JSON存储结构及关键业务规则落表方案；当前版本 v1.5（含 developer 角色、plain_password、remark、title_remark、groups_remark）
- **更新时机**：表结构变更、业务规则调整时更新

### 3. 技术栈文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\tech-stack.md`
- **作用**：记录前后端技术选型（含 echarts 图表库）、项目结构、Docker Compose 部署方案、依赖包等
- **更新时机**：技术栈变更、依赖升级时更新

### 4. 项目规则文档
- **路径**：`.claude/rules/code_rule.md`
- **作用**：定义强制前置要求、文档更新规则
- **更新时机**：项目规则调整时更新

### 5. 代码文件长度规则
- **路径**：`.claude/rules/file-length-rule.md`
- **作用**：定义文件行数限制、拆分触发条件、拆分策略
- **更新时机**：编码规范调整时更新

### 6. 模块开发文档规则
- **路径**：`.claude/rules/function_rule.md`
- **作用**：定义模块开发文档的要求、模板、更新规则
- **更新时机**：模块开发规范调整时更新

### 6.1 Git 提交信息规范
- **路径**：`.claude/rules/git-commit-message.md`
- **作用**：定义 Git 提交信息格式（Conventional Commits + 中文）、类型、范围、正文要求
- **更新时机**：提交规范调整时更新

### 7. 项目文档索引（本文档）
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\architecture.md`
- **作用**：整理项目所有文档的作用和目录，方便快速查找
- **更新时机**：每次更新其他文档后必须同步更新本文档

### 8. 实施方案文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\implementation-plan.md`
- **作用**：定义项目开发任务分解、模块依赖关系、开发阶段规划
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
- **作用**：定义数据分析模块完整方案：CSV 结构、字段映射、16 项衍生指标、阵营对比、职业深度、小队分析、ECharts 图表规划与实施记录（当前代码已按此实现，为数据分析模块主参考文档）
- **更新时机**：数据分析模块功能调整时更新

### 14. 安全审查文档
- **路径**：`e:\code\@Cjy\nsh-management\memory-bank\security-review.md`
- **作用**：项目安全审查记录，涵盖认证、权限、数据安全等方面的审查结论与改进项
- **更新时机**：安全相关变更或审查时更新

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

---

## 使用说明

1. **开发前**：阅读本文档了解项目结构，然后按需阅读具体文档
2. **更新文档后**：必须同步更新本文档的"文档说明"和"更新记录"
3. **新增文档**：必须在本文档中添加对应说明

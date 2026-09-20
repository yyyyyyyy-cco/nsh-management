# 后端项目 开发文档

## 需求说明

### 功能概述
基于 FastAPI + SQLAlchemy + SQLite 的后端服务，为帮会联赛管理系统提供 RESTful API，涵盖认证、常驻库、联赛日程、出勤库、排表、录屏审核、数据分析、系统配置等模块。

### 业务目标
- 多帮会数据隔离（guild_id），每个帮会一个管理员账号 + 一个帮众共享账号
- JWT 认证 + 角色权限控制（developer/admin/member）
- 登录限流（5 次失败锁定 5 分钟）
- 全部业务规则按 database-design.md v1.8 落表

### 用户场景
- 开发者：创建帮会、派发账号、删除帮会、全局管理
- 管理员：登录、管理成员/赛程/出勤/排表、审核录屏、导入 CSV 分析、调整小队分配、系统配置
- 帮众：浏览联赛总览（录屏上传）、查看个人战绩与联赛日程（详情内录屏提交/数据分析只读）、提交录屏链接

## 开发计划

### 功能清单
- [x] 后端项目初始化、目录结构搭建（P0）
- [x] 依赖安装（FastAPI、SQLAlchemy、Pydantic、JWT、Alembic 等）（P0）
- [x] 数据库配置（异步连接、Session 管理）（P0）
- [x] 数据模型定义（11 张表，见 database-design.md v1.8）（P0）
- [x] Pydantic Schema 定义（P0）
- [x] 全局异常处理、CORS 配置（P0）
- [x] 认证模块：登录/登出/获取用户信息 + 登录限流（含未知账号锁定）（P0）
- [x] 常驻库 API（CRUD、搜索筛选、Excel 导入、出勤率统计、职业统计）（P1）
- [x] 联赛日程 API（CRUD、级联创建/删除）（P1）
- [x] 出勤库 API（导入成员/替补/补人、请假导入、状态管理、职业切换）（P1）
- [x] 排表 API（候选池、JSON 排表存取、导入历史排表、标题/组备注）（P2）
- [x] 录屏审核 API（提交、审核、批量审核、全局进度）（P2）
- [x] 数据分析 API（CSV 导入解析、6 榜排行、职业 17 项统计、16 项衍生指标、阵营对比、小队分析）（P2）
- [x] 分析调整 API（小队分析内未排表成员→目标队伍临时分配，仅作用于分析视图）（P2）
- [x] 系统配置 API（职业配置、账号管理、帮会管理、开发者角色）（P2）
- [x] 个人战绩 API（玩家名搜索、按游戏 ID 聚合历史比赛数据与排名）（P2）
- [x] 系统日志 API（审计中间件自动落库写操作与 5xx、查询/统计/清理，仅开发者）（P2）
- [x] Docker 部署（Dockerfile、docker-compose、deploy.sh、entrypoint.sh）（P2）

### 依赖关系
- 依赖 database-design.md v1.8（表结构）
- 依赖 tech-stack.md（技术选型、requirements.txt）
- 认证模块是其他所有 API 的前置（依赖注入校验 Token）
- 排表/录屏/分析依赖赛程模块的级联创建

## 进度跟踪

### 当前状态
**状态**：已完成
**完成进度**：100%（全部功能模块开发完成）

### 已完成
- ✅ 项目初始化、目录结构、依赖安装（venv，Python 3.13）
- ✅ 数据库配置（SQLAlchemy 2.0.36 异步 + aiosqlite）
- ✅ 11 张表模型 + 14 个 Alembic 迁移（data/nsh.db）
- ✅ Pydantic Schema、全局异常处理、CORS
- ✅ 认证模块（登录/登出/me + 5 次失败锁定 5 分钟 + 未知账号锁定 + 锁定倒计时 remaining_seconds）
- ✅ 开发者角色（developer，不绑定帮会，可创建帮会/派发账号/删除帮会）
- ✅ 默认数据初始化（app/init_db.py：仅空库时初始化，admin/member 密码可选）
- ✅ 常驻库 API：CRUD、搜索（姓名）、职业/状态筛选、分页、批量删除、职业统计聚合
- ✅ 常驻库 Excel 导入（openpyxl 后端解析、表头自动识别、重名跳过、非法职业跳过）
- ✅ 出勤率统计接口（正常/(正常+请假)，无记录为 null）
- ✅ 联赛日程 API：CRUD + 时间范围查询（日历用）
- ✅ 级联创建（建赛程自动建空排表，验证 lineups=1）
- ✅ 级联删除（录屏→分析→出勤→排表→赛程，验证 lineups=0）
- ✅ 局数校验（1-3）、结果/每局结果校验（数量与局数一致）
- ✅ 出勤库 API：一键导入正式（幂等）、替补候选与导入、添加补人、批量导入成员、请假导入
- ✅ 状态切换（单人/批量，即时生效）、60 人上限校验（补人/导入路径）、缺口统计
- ✅ 出勤职业切换（PUT attendance/{id}/profession，校验主/副职业范围，补人不可改）
- ✅ 排表 API：空结构初始化（10队×6槽）、候选池（出勤正常成员，含补人）
- ✅ 保存校验（结构/槽位序号/成员归属本帮会/姓名按库规范化/备注清理）
- ✅ 导入历史排表（GET/POST lineup/history + import，按小队导入，仅候选池成员排入）
- ✅ 排表备注（title_remark 标题备注、groups_remark 各组备注 JSON）
- ✅ 排表请假联动（get_lineup 读取时自动清空请假成员槽位）
- ✅ 补人姓名规范化（新增/查重/排表职业映射/候选池/历史导入统一去除首尾空白；规范化后重名或空名显式报冲突）
- ✅ 录屏审核 API：提交/审核/批量审核/全局进度（请假人员自动排除）
- ✅ 数据分析 API：CSV 导入/6 榜排行/职业 17 项统计/16 项衍生指标/阵营对比/小队分析（HTML 报告导出已移除）
- ✅ 16 项衍生指标计算（calculate_indicators：效率/生存/占比/技能四类）
- ✅ 阵营对比接口（camp-compare：11 项指标差值/波动值）
- ✅ 小队分析接口（squad-analysis：关联排表，仅我方阵营，未排表兜底）
- ✅ 分析调整 API（squad_adjustments：GET/PUT，临时分配未排表成员到目标队伍，仅作用于分析视图）
- ✅ 个人战绩 API（玩家名搜索、按游戏 ID 聚合历史战绩与排名）
- ✅ 系统日志 API（审计中间件：写操作 + 5xx 自动落库、登录埋点、查询/统计/清理、90 天保留清理，仅开发者）
- ✅ 系统配置 API：职业配置（含 remark 说明字段）、账号管理、帮会管理（开发者）
- ✅ 级联删除帮会（DELETE /config/guilds/{id}，仅开发者，删除全部关联数据）
- ✅ 删除账号（DELETE /config/accounts/{id}，不能删自己/开发者）
- ✅ 用户表新增 plain_password 字段（本地管理工具查看明文密码）
- ✅ 用户表 guild_id 允许 NULL（developer 角色）、relationship + guild_name 属性
- ✅ Docker 部署：backend/frontend Dockerfile（多阶段构建）、docker-compose.yml、deploy.sh、entrypoint.sh、nginx.conf
- ✅ .env.example 部署环境变量模板
- ✅ 成员详情接口（GET /members/{member_id}，require_admin；注册于 /export、/export-image、/profession-stats、/attendance-rate 等具体路径之后，防动态路由捕获 422）

### 进行中
- 无

### 待开始
- 无

### 下一步计划
测试与优化：补充单元测试、压力测试、安全审计；未解决风险见 `memory-bank/security-review.md` §十。

### 隔离与导出回归（2026-09-18 新增）
在项目根目录用 backend 虚拟环境运行（无需 pytest/httpx，不连接业务数据库）：

```bat
backend\.venv\Scripts\python.exe -X utf8 backend\scripts\selfcheck_security_fixes.py
backend\.venv\Scripts\python.exe -X utf8 backend\scripts\selfcheck_member_exports.py
```

覆盖：账号跨帮会创建拒绝（403）、开发者目标帮会校验（400/404/422）、批量 ID 边界（空/超限/非正整数 → 422）、未绑定帮会创建/导入成员拒绝、出勤率跨帮会隔离、Excel 新旧格式回导兼容与来源行不可改写归属。

### 更新记录
| 日期 | 更新内容 |
|------|----------|
| 2026-08-06 | 初始化文档 |
| 2026-08-06 | 阶段一完成：基础框架 + 认证模块，冒烟测试通过 |
| 2026-08-07 | 常驻库模块完成（CRUD/筛选/导入/出勤率），测试通过 |
| 2026-08-11 | 联赛日程模块完成（CRUD/级联创建与删除），测试通过 |
| 2026-08-11 | 出勤库模块完成（导入/补人/状态/保存），术语”客人”改为”补人” |
| 2026-08-11 | 排表模块完成（空结构/候选池/保存校验/规范化），测试通过 |
| 2026-08-17 | 录屏审核模块完成（列表/提交/审核/批量审核/进度统计） |
| 2026-08-17 | 数据分析模块完成（CSV导入/排行榜/职业统计/HTML报告导出） |
| 2026-08-17 | 系统配置模块完成（职业配置/账号管理/帮会管理） |
| 2026-08-18 | 开发者角色完善（plain_password/developer role/帮会CRUD/账号删除） |
| 2026-08-18 | 出勤库增强（批量导入成员/请假导入/职业切换） |
| 2026-08-18 | 排表增强（导入历史排表/标题备注/组备注/请假联动） |
| 2026-08-18 | 认证增强（未知账号锁定/锁定倒计时 remaining_seconds） |
| 2026-08-18 | Docker 部署完成（Dockerfile/docker-compose/deploy.sh/nginx.conf） |
| 2026-08-18 | 测试脚本清理（删除 7 个硬编码脚本，新增 generate_import_template） |
| 2026-08-26 | 数据分析 API 增强（16 项衍生指标/阵营对比/小队分析接口）、移除 HTML 报告导出，文档对齐 |
| 2026-08-26 | 新增分析调整 API（squad_adjustments），文档全面对齐（developer 角色、表数 10、迁移数 9、v1.6 引用） |
| 2026-09-15 | 补人姓名规范化修复（出勤与排表姓名匹配统一去首尾空白，新增 utils/member_names 与 services/lineup_attendance，重名冲突显式报错） |
| 2026-09-15 | 文档失实项修正：表数 10→11、迁移数 13→14、database-design 引用 v1.6→v1.8、帮众场景按代码校正、补个人战绩/系统日志模块、移除「保存考勤」失实表述 |
| 2026-09-17 | 登记规划中功能：成员详情接口 GET /members/{member_id}（P1，方案见 stats-report-plan.md） |
| 2026-09-17 | 成员详情接口实施完成（GET /members/{member_id}，require_admin，注册于全部具体路径之后防路由捕获） |
| 2026-09-18 | 修复登录响应丢失 guild_icon：User 模型补 guild_icon property（与 guild_name 对称），UserOut.model_validate 序列化恢复正常（修复前登录后切换账号图标显示为空，/me 手动构造路径正常） |
| 2026-09-18 | 用户隔离定向修复（security-review §十 F-1～F-5）：①`POST /config/accounts` 管理员仅能为本帮会创建、跨帮会 403，开发者目标帮会需存在（400/404/422），service 写库前校验帮会存在；②`attendance_rate` 关联 Schedule 按 guild_id 聚合；③未绑定帮会创建/导入成员提前 403（更正：Member.guild_id 非空约束本就存在，原为 500 风险非写入成功）；④Excel 导出各 Sheet 加帮会来源行 + 文件名含帮会名，导入兼容新旧格式且归属以认证帮会为准；⑤批量 ID 统一 BatchIds（1～500 严格正整数） |
| 2026-09-18 | 新增回归脚本：`scripts/selfcheck_security_fixes.py`（8 项，真实 JWT + ASGI 路由）、`scripts/selfcheck_member_exports.py`（8 项，出勤隔离 + Excel 回导），16 项全部通过 |

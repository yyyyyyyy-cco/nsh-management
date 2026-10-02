# 更新日志

本文件记录本项目的**显著变更**（面向使用者与运维者），格式遵循
[Keep a Changelog 1.1.0](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循
[语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

**维护约定**

1. 新变更先写入 `## [Unreleased]` 段，发布时改为 `## [x.y.z] - YYYY-MM-DD`（日期用标签创建日）。
2. 分类固定六类，按需出现：`新增` / `变更` / `弃用` / `移除` / `修复` / `安全`。
3. 只写「对人有用」的条目：内部重构若无外部可见影响，不单独成条。
4. **不复制其他权威源**：逐条实现与整改进度见 `memory-bank/progress.md`；合规差距与路线见
   `.agent/plans/compliance-remediation-plan.md`；发布流程见 `GIT-GUIDE.md` §5。
5. 本文件建立于 2026-10-02（v1.2.0 发布当日）。**早于此的 1.0.0 / 1.1.0 段由 `git log` 归并**
   （标注了归并依据），不是逐条回溯；更早历史请查标签与提交记录。
6. 已知不一致（待决策 D-4）：`frontend/package.json` 的 `version` 仍为 `0.1.0`，与标签 `v1.x` 不一致。
   本项目为私有应用（不发布到 npm），故暂以 **git 标签**为版本权威；联动机制见计划 D-4。

---

### 安全

- **口令策略调整（行为变更）**：不再要求「必须同时含字母和数字」（该要求违反 ASVS 6.2.5），改为 8–128 位 + 常见弱口令/项目相关词拦截 + 不得含登录名；纯字母、纯数字、纯符号口令现均可使用。

- **审计留痕更完整**：除写操作外，**携带令牌却被拒的读请求（401/403）也会记入审计**（越权尝试不再无痕）；匿名 401 不记录以免探测刷日志。审计/日志中的控制字符（含换行）统一转义，防止伪造日志行。

- **依赖安全性**：`python-jose` 由 3.3.0（2021 年）升级到 **3.5.0**（上游 3.4.0 即为修复 JWT 相关 CVE 发布）；同时把测试用 HTTP 客户端由 `httpx` 换成 `httpx2`，全量测试**告警清零**（0 warnings）。

- **错误率告警**：新增后台告警循环——最近 `ALERT_WINDOW_MINUTES`（默认 30）分钟内 `level=error` 审计日志达 `ALERT_ERROR_THRESHOLD`（默认 20）条即触发；配置 `ALERT_WEBHOOK_URL` 时 POST JSON，**未配置时也会写 WARNING 日志**（不静默）。阈值 0 表示禁用（`DEPLOY.md §四/§六`、`.env.example`）。
- **CSP 收紧**：边缘 Nginx 的 `script-src` 去掉 `'unsafe-inline'` 与 `'unsafe-eval'`（构建产物无内联脚本，唯一 `new Function` 为 core-js 的带 `window` 回退的全局探测），并补 `object-src 'none'`、`base-uri 'self'`、`form-action 'self'`；`X-XSS-Protection` 置 `0`（现代浏览器已弃用该过滤器）。

### 修复

- **导出 Excel 公式注入**：成员姓名/备注等用户输入以 `=`/`+`/`-`/`@` 开头时，导出文件可能被 Excel 当作公式求值；现已统一按文本单元格写入（回归用例 `backend/tests/test_excel_export_formula.py`）。

### 新增

- **自助修改口令**：新增 `POST /api/v1/auth/password`（需提供当前口令），界面入口在右上角用户名菜单 →「修改密码」；改密后**其他设备上的旧登录立即失效**，当前会话也会回到登录页。

- **备份与制品归档脚本模板**：`scripts/backup-db.sh.example`（SQLite 在线 backup API、默认 dry-run、生成后完整性校验、保留轮转）与 `scripts/release-archive.sh.example`（镜像 tar + 清单，版本权威为 git 标签）。
- **依赖精确锁定**：`fastapi`/`python-multipart` 由范围约束改为 `==` 精确版本，并显式锁定传递引入的 `starlette`；新增 CI 门禁 `scripts/check_requirements_pins.py`。

## [Unreleased]

合规化整改带来的**使用者可见变更**（整改进度见 `memory-bank/progress.md`；差距清单见
`.agent/plans/compliance-remediation-plan.md`）。条目按**使用者影响**归并，非逐提交罗列。

### 新增

- **自助修改密码**：前端新增入口，后端新增 `POST /auth/password`；口令策略按 ASVS 5.0.0 校正
  （只校验长度与黑名单，**不再强制"字母 + 数字"组合**），改密后**旧登录立即失效**（`token_version` 自增）。
- **健康检查端点** `GET /health`（含数据库连通性；数据库不可用时返回 503），供容器 healthcheck 与监控使用；
  生产环境（`APP_ENV=production`）同时**关闭** `/docs`、`/redoc`、`/openapi.json`。
- **错误率告警**：最近 N 分钟内 `level=error` 审计日志达到阈值即触发；未配置 `ALERT_WEBHOOK_URL` 时
  **仍写 WARNING 日志**（不静默）。
- **运维模板**：`scripts/backup-db.sh.example`（SQLite 在线 backup API + `PRAGMA integrity_check`，默认 dry-run）、
  `scripts/release-archive.sh.example`（按版本号归档镜像与清单），并在 `DEPLOY.md` 补齐**回滚/归档**流程。
- **测试与静态检查**：后端 `pytest`（含生产弱密钥门禁、权限矩阵、姓名规范化等用例）、前端 Vitest；
  后端 Ruff、前端 ESLint + Prettier，以及 CI 工作流与提交消息校验钩子。

### 变更

- **前端工具链升级**：`vite` 6.4.3、`vitest` 4.1.11（清除 dev 工具链公告），Node 侧要求 `^18 || ^20 || >=22`。
- **依赖升级**：`python-jose` 3.5.0；`bcrypt` 4.3.0（**移除未维护的 passlib**，改为直连调用）；
  生产弱密钥门禁由**导入期**改为**应用启动期**（`startup_checks()`），运维可见文案与"拒绝启动"语义不变。
- **Nginx 收紧**：内层 `frontend/nginx.conf` 对 `/assets/` 增加**静态资源扩展名白名单**（其余一律 404）；
  边界层模板 `nginx.conf.example` 将 CSP `connect-src` 收窄为 `'self'`，并停用 `X-XSS-Protection`。
- **口令口径统一**：帮会面板初始口令校验与后端一致（前端不再拦截纯字母/纯数字口令）。
- **仓库规范**：`.gitattributes` 换行与二进制策略、`.editorconfig`、`.githooks/commit-msg` 提交消息校验。

### 修复

- **长口令截断**：bcrypt 只使用前 72 字节——改为 **SHA-256 预哈希**（`sha256$` 前缀）后再哈希，
  并支持**旧哈希登录时惰性升级**；同时修复非法哈希导致的进程级 panic（改为校验失败）。
- **弱密钥门禁**：拒绝**低熵**十六进制（如顺序串），CI 占位密钥显式封禁。
- **静态资源与 CSP**：见「变更」的 Nginx 两条（修复的是可被探测的资源路径与过宽的 `connect-src`）。
- **部署模板入库**：`frontend/nginx.conf` 与 `deploy.sh.example` 入库，修复镜像构建缺失 `nginx.conf` 的问题。

### 安全

- 跨帮会创建账号与批量写操作越界修复、账号响应脱敏、成员数据隔离收紧（v1.2.0 起持续）。
- 审计日志覆盖**带凭证的拒绝请求**，并转义日志中的控制字符（防日志注入）。
- 生产弱密钥启动门禁、口令预哈希、CSP/静态资源收紧（详见上列条目）。

---

## [1.2.0] - 2026-10-02

> 归并依据：`git log v1.1.0..v1.2.0`（24 个提交）。

### 新增

- 帮众专属首页，并改为帮众登录后的默认落点。
- 游戏 ID 改名审批与身份关联：数据表、Alembic 迁移、服务与路由，以及帮众提交页与管理员审核页。
- 战报增强：分析调整小队归属、逐局重伤王、六榜。
- 个人战绩支持新旧 ID 合并查询与归属提示；新增成员详情战绩页与管理员战绩入口。
- 小队分析支持取消单个成员分配；表格密度切换与空状态插画收尾 UI 优化。

### 修复

- **安全**：修复跨帮会创建账号与批量写操作越界，收紧成员数据隔离；账号响应统一脱敏并新增生产弱密钥门禁。
- 排表保存串行化，阻止重载覆盖未保存编辑。
- 图表自定义 HTML tooltip 转义动态文本。
- 补 `User.guild_icon` 序列化，修复帮会图标字丢失。
- 导入导出携带帮会来源标识，拒绝未绑定帮会的操作。

---

## [1.1.0] - 2026-09-16

> 归并依据：`git log v1.0.0..v1.1.0`（38 个提交）。

### 新增

- 操作日志系统：审计写操作并支持查询与清理。
- 个人战绩查询模块（含排行榜：己方阵营/全部排名切换、重伤趋势）与帮众侧边栏入口。
- 常驻库 Excel 与图片导出。
- 出勤库备注全链路：导入带出、管理员编辑、候选池展示。
- 单场职业配置覆盖；玩家名模糊搜索与查询框自动补全。
- 移动端表格改行列表，新增骨架屏与路由分包预取；UI 优化方案 11 项。

### 修复

- **部署**：生产改单层 TLS；修复限流与审计日志取真实客户端 IP；微信端旧页面缓存问题
  （`index.html` 强化 `no-store` 并内嵌 meta 缓存标签）。
- 补人姓名统一去首尾空白；修复排表偶发不显示职业。

---

## [1.0.0] - 2026-08-27

首个标签，记录项目初始可发布版本。本文件建立于 1.2.0 发布日，未回溯此版本的逐条变更，
历史请查该标签对应的提交记录（`git log v1.0.0`）。

[Unreleased]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yyyyyyyy-cco/nsh-management/releases/tag/v1.0.0
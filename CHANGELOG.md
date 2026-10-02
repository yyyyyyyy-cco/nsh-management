# 更新日志

本文件记录本项目的**显著变更**（面向使用者与运维者），格式遵循
[Keep a Changelog 1.1.0](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循
[语义化版本 2.0.0](https://semver.org/lang/zh-CN/)。

**维护约定**

1. 新变更先写入 `## [未发布]` 段，发布时改为 `## [x.y.z] - YYYY-MM-DD`（日期用标签创建日）。
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

- **错误率告警**：新增后台告警循环——最近 `ALERT_WINDOW_MINUTES`（默认 30）分钟内 `level=error` 审计日志达 `ALERT_ERROR_THRESHOLD`（默认 20）条即触发；配置 `ALERT_WEBHOOK_URL` 时 POST JSON，**未配置时也会写 WARNING 日志**（不静默）。阈值 0 表示禁用（`DEPLOY.md §四/§六`、`.env.example`）。
- **CSP 收紧**：边缘 Nginx 的 `script-src` 去掉 `'unsafe-inline'` 与 `'unsafe-eval'`（构建产物无内联脚本，唯一 `new Function` 为 core-js 的带 `window` 回退的全局探测），并补 `object-src 'none'`、`base-uri 'self'`、`form-action 'self'`；`X-XSS-Protection` 置 `0`（现代浏览器已弃用该过滤器）。

### 修复

- **导出 Excel 公式注入**：成员姓名/备注等用户输入以 `=`/`+`/`-`/`@` 开头时，导出文件可能被 Excel 当作公式求值；现已统一按文本单元格写入（回归用例 `backend/tests/test_excel_export_formula.py`）。

### 新增

- **备份与制品归档脚本模板**：`scripts/backup-db.sh.example`（SQLite 在线 backup API、默认 dry-run、生成后完整性校验、保留轮转）与 `scripts/release-archive.sh.example`（镜像 tar + 清单，版本权威为 git 标签）。
- **依赖精确锁定**：`fastapi`/`python-multipart` 由范围约束改为 `==` 精确版本，并显式锁定传递引入的 `starlette`；新增 CI 门禁 `scripts/check_requirements_pins.py`。

## [未发布]

合规化整改（依据 `.agent/plans/compliance-remediation-plan.md`；Wave 0～2 已完成，Wave 3～4 进行中）。

### 新增

- **测试体系**：后端 `backend/pytest.ini` 与 `backend/tests/`（安全工具、生产弱密钥启动门禁、
  权限依赖矩阵、姓名规范化）；既有 6 个 `backend/scripts/selfcheck_*.py` 一并纳入 pytest 收集。
  前端 Vitest（`frontend/vitest.config.ts`）与 4 个测试文件（业务常量、职业色、赛程排序、评分与聚合分析）。
- **静态检查与 CI 门禁**：后端 Ruff（`backend/ruff.toml`）、前端 ESLint 10 + Prettier 3（扁平配置）、
  `.github/workflows/ci.yml`（后端 / 前端 / 仓库卫生 / 提交消息 / 镜像构建 5 个 job）、
  `.github/dependabot.yml`、`.githooks/commit-msg` 提交消息校验与 `scripts/check_commit_msg.py`、
  `scripts/check_file_length.py` 行数门禁。
- **仓库规范文件**：`.gitattributes`（换行与二进制策略）、`.editorconfig`、`backend/requirements-dev.txt`、
  `scripts/install_git_hooks.sh`。
- **部署模板**：`frontend/nginx.conf`（内层反代，入库）、`deploy.sh.example`（占位符模板）。
- **前端单一来源工具**：`frontend/src/utils/attendance.ts`（出勤率阈值、低出勤判定、百分比格式化）。

### 变更

- **部署**：`frontend/nginx.conf.example` 收敛为**边界层**模板，内层反代拆到入库的 `frontend/nginx.conf`；
  `deploy.sh` 改为 `deploy.sh.example`（占位符 + 路径锚定排除 + 健康检查与域名校验，非零退出）。
- **文档**：`README.md` 明确支持的 Python 版本（3.11～3.13，3.14 因 `pydantic-core` 无 wheel 不可用）
  并补充 pip 镜像与编码排错；`docker-compose.yml` 标注为本地/单机演示拓扑。
- 代码树与文档索引改为引用 `memory-bank/progress.md` / `memory-bank/architecture.md` 权威源，不再复制。

### 修复

- `backend/requirements.txt`、`backend/requirements-dev.txt`：补 PEP 263 编码声明
  （`# -*- coding: utf-8 -*-`），**修复中文 Windows（cp936）下 `pip install -r requirements.txt`
  因 gbk 解码失败而中断**——该命令正是 `README.md` 的安装第一步。
- `backend/scripts/audit_weights_v4_*.py`、`derive_weights_v4_*.py`、`sim_contribution_weights_v4_*.py`：
  移除硬编码的 `e:\code\@Cjy\...` 绝对路径，改为环境变量（`NSH_DB_PATH`、`NSH_ANALYSIS_TS`）与相对路径。
- `backend/app/models/user.py`：修复 F821（`Guild` 改为 `TYPE_CHECKING` 相对导入）。
- 前端 `lineupBoard.ts`：新增导出类型 `SlotDragEvent`，取代 4 处 `any`（vuedraggable 事件对象）。

### 安全

- **生产弱密钥启动门禁由「导入期」改为「应用启动期」**（`backend/app/core/config.py` → `app/main.py`
  的 `startup_checks()`）：原先任何导入配置的场景（alembic、测试收集、一次性脚本）在生产环境下都会
  被 `sys.exit(1)` 终止；现运维可见文案与「拒绝启动」语义不变，且门禁可被单元测试覆盖。
- 新增门禁回归用例：生产弱密钥拒绝启动（子进程非零退出 + `FATAL` 文案）、强密钥放行、开发环境仅告警、
  **仅导入配置不退出**。

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

[未发布]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/yyyyyyyy-cco/nsh-management/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/yyyyyyyy-cco/nsh-management/releases/tag/v1.0.0
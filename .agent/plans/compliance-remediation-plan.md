# 项目合规化与工程完善计划

> 本文档面向「刚从 Git 拉取的全新检出」，以行业权威规范为基准，逐条列出仓库当前的不合规项与整改路线。
> 存放位置遵循 `AGENTS.md` §2.2「新增文档必须登记到 `architecture.md`」：本文档已登记为 `architecture.md` 文档说明 §21，并在其目录树与更新记录中登记。

| 项 | 值 |
|----|----|
| 文档版本 | v1.1（2026-10-02 记录决策确认，见 §3.1） |
| 创建日期 | 2026-10-02 |
| 适用基线 | 分支 `main`，提交 `2a2b081`（标签 `v1.2.0` → `e8d33ba`） |
| 依据来源 | 本轮对全仓的**只读静态审查**（文件读取 + 内容检索 + Git 元数据），未运行构建/测试、未访问生产服务器 |
| 维护规则 | 每完成一项任务即更新 §7 进度表；波次结束或决策变更时更新本表版本号与 `architecture.md` 更新记录 |

---

## 1. 背景与目标

### 1.1 背景

本仓库为全新克隆。经静态审查确认，项目**业务代码质量与文档治理意识高于同类中小型项目平均水平**（分层清晰、权限集中、审计与门禁齐备、文档有权威源映射），但**交付链路（构建/部署/发布）存在阻断级缺陷**：仓库内的构建输入不完整，生产配置完全在仓库之外，无 CI、无自动化测试、无回滚手段。

### 1.2 目标（Definition of Done）

| 编号 | 完成定义 | 可验证方式 |
|------|---------|-----------|
| D1 | 全新克隆可复现本地开发与双镜像构建 | 干净目录执行 `docker compose build` 成功（§8 命令 4） |
| D2 | 生产部署链路可从仓库复现 | 仓库内含配置模板；`DEPLOY.md` 无「只能改服务器」的隐式前置（§8 命令 5） |
| D3 | 每次推送有 CI 门禁 | GitHub Actions 绿：类型检查 + 构建 + 测试 + 镜像构建（§8 命令 6） |
| D4 | 发布可回滚 | 制品按版本标识 + `DEPLOY.md` 有回滚章节（§8 命令 7） |
| D5 | 合规文件齐备 | `LICENSE`/`CHANGELOG.md`/`SECURITY.md`/`CONTRIBUTING.md` 按 §3 D-1 决策确定的范围齐备 |
| D6 | 文档满足自身规范 | 全仓小写 kebab-case、无陈旧绝对路径、无重复权威源、全部登记入索引 |
| D7 | 每项改动可验证 | 每项任务在 §5 附带「验收命令」，在 §7 记录验证证据 |

### 1.3 不在本次范围

- 业务功能新增与 UI 调整（本计划只做合规化与工程效能，不改业务语义）
- 数据库表结构变更（无必要，`alembic` 版本链完整：12 张表 / 15 个迁移，head `o9p0q1r2s3t4`）
- 生产服务器上的直接操作（须先经 §3 决策与 §6 授权，并遵循「先备份 → 改 → 验证」流程）

---

## 2. 依据的行业权威规范

> 「本项目适用条款」为实施时应引用的范围；ASVS 的具体条目号在任务实施时按 `v5.0.0-<章>.<节>.<条>` 格式引用（官方建议带版本前缀引用）。

| 规范 | 版本 / 来源 | 本项目适用条款 | 用于 |
|------|------------|---------------|------|
| Semantic Versioning | 2.0.0（[semver.org](https://semver.org/spec/v2.0.0.html)） | 版本号与 tag 名称一致（现为 `vX.Y.Z`，已合规） | 发布、F-22 |
| Conventional Commits | 1.0.0（[conventionalcommits.org](https://www.conventionalcommits.org/en/v1.0.0/)） | `<type>(<scope>): <subject>`，与 `.agent/rules/git-commit-message.md` 一致 | 提交规范、F-32 |
| Keep a Changelog | 1.1.0（[keepachangelog.com](https://keepachangelog.com/en/1.1.0/)） | `CHANGELOG.md` 结构、`Unreleased` 段、Added/Changed/Fixed/Security 分类 | F-25、W3-4 |
| OWASP ASVS | **5.0.0**（官方页标注最新稳定版；[owasp.org/projects/asvs](https://owasp.org/projects/asvs)） | 配置（V13/V14）、认证（V6）、会话（V7）、访问控制（V8）、日志与错误处理（V16）章节级对照 | 安全核查、W4-2 |
| OWASP Top 10 | **2025**（[top10.owasp.org](https://top10.owasp.org/)） | A01 访问控制失效、A02 配置错误、A05 注入、A09 日志与告警失效 | 安全核查、W4-2 |
| SLSA | v1.2（[slsa.dev/spec/v1.2](https://slsa.dev/spec/v1.2/)） | 构建可复现、来源可追溯（provenance）——本项目对应「镜像由仓库输入构建」 | 供应链、F-08/F-09/F-15 |
| OpenSSF Scorecard | 自评清单（[github.com/ossf/scorecard](https://github.com/ossf/scorecard)） | 分支保护、依赖更新、CI、许可、安全策略、代码审查 | 仓库治理总checklist |
| The Twelve-Factor App | [12factor.net](https://12factor.net/) | III 配置外置、V 构建/发布/运行分离、XI 日志作为事件流 | 部署、F-10/F-19 |
| CIS Docker Benchmark | [cisecurity.org](https://www.cisecurity.org/benchmark/docker) | 非 root 运行、镜像最小化、健康检查、资源限制、不嵌密钥 | 容器、F-14/F-16 |
| PEP 8 / PEP 484 / PEP 621 | [peps.python.org](https://peps.python.org/) | 代码风格、类型注解、`pyproject.toml` 元数据与依赖声明 | 后端、F-15/F-29 |
| Vue 官方风格指南 | 优先级 A/B（[vuejs.org/style-guide](https://vuejs.org/style-guide/)） | 组件命名多单词、单文件组件块顺序、props 细节 | 前端、F-30 |
| EditorConfig | [editorconfig.org](https://editorconfig.org/) | 缩进与换行统一（仓库当前无 `.editorconfig`） | F-31 |
| Git `.gitattributes` | [git-scm.com/docs/gitattributes](https://git-scm.com/docs/gitattributes) | `text=auto` + `eol` 归一（官方建议避免混合换行） | F-31 |
| MIT License（SPDX: MIT） | [opensource.org](https://opensource.org/license/mit) | 声明与文件一致（README 已声明 MIT，缺文件） | F-23 |
| Contributor Covenant | 2.1（[contributor-covenant.org](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)） | 社区行为准则（按 §3 D-1 决策启用） | F-24 |
| ADR（架构决策记录） | Nygard, 2011 | 关键决策留痕（本项目可复用 `architecture.md` 更新记录承担，**暂不引入**） | 治理（可选） |

> 判定范围说明：以上为**行业通行做法**，本项目的对齐程度见 §4；凡仓库内无依据的推断均不写入结论。

---

## 3. 关键决策（**开工前需用户确认**）

| 编号 | 决策项 | 选项 | 默认建议 | 阻塞的任务 |
|------|--------|------|---------|-----------|
| D-1 | 仓库可见性（public / private） | public / private | 未确认前不建 `CONTRIBUTING.md`/`CODE_OF_CONDUCT.md`，先做 `LICENSE` | W0-1、W4-4 |
| D-2 | 远端策略 | ①补配 `gitee` 镜像 ②改规范为「单远端 + 可选镜像」 | ②：仓库无协作者证据，`GIT-GUIDE.md:15,18,281` 的强制双远端与事实不符 | W3-6 |
| D-3 | 授权范围 | ①允许本会话执行 `git commit` ②允许删除 3 个已合并远端分支 | 均需显式授权（`AGENTS.md` §5：未经允许禁止提交或删除） | 全部任务 |
| D-4 | 版本联动 | ①`frontend/package.json` 与 tag 联动 ②保持独立 | ①：否则制品无法反查版本（当前恒 `0.1.0`） | W3-4 |
| D-5 | 生产配置可否去敏入库 | ①可（入库 `.example`）②不可（只出 diff 告警脚本） | 需你判断敏感度；不过至少应做 ② | W1-3 |
| D-6 | 换行归一 | ①一次 `renormalize` 提交（触达约 260 文件 diff）②仅记录不改 | ①：混合换行已产生过实际困扰（`progress.md` 2026-09-24 记录「按 cr-at-eol 口径检查差异空白」） | W0-2 |

### 3.1 决策确认记录（2026-10-02）

| 编号 | 确认结果 | 影响 |
|------|---------|------|
| D-1 | **公开仓库**：按公开标准补齐 `LICENSE` + `CONTRIBUTING.md` + `SECURITY.md` + `CODE_OF_CONDUCT.md` | W0-1、W4-4 全量执行；`LICENSE` 版权人名称**待用户提供**（未提供前 W0-1 阻塞） |
| D-2 | **改规范为「单远端 + 可选镜像」**：更新 `GIT-GUIDE.md` §1/§5.2/§8 及 `README.md`/`DEPLOY.md` 相关表述 | W3-6 按此执行，不再要求强制 `gitee` 推送 |
| D-3 | **允许执行 `git commit`**（限本地提交；不含推送、不含删除远端分支/标签） | 各任务按「一次一个主题」提交；推送与远端操作仍需逐次授权 |
| D-6 | **执行换行归一**：新增 `.gitattributes` 后单独提交 `git add --renormalize .` | W0-2 全量执行；归一提交必须独立、不与逻辑改动混合 |
| D-4 | 待确认 | 不阻塞 Wave 0；W3-4 前需确认 |
| D-5 | 待确认 | 不阻塞 Wave 0；W1-3 前需确认（未确认时 W1-3 退化为仅出 diff 告警脚本） |

**执行节奏（2026-10-02 确认）**：用户先评审本计划，评审通过后由 **Wave 0** 开始逐项执行；每项任务完成后更新 §7 进度表并留下验证证据。

---

## 4. 差距清单（42 项，证据 → 规范 → 波次）

> 严重度：**P0** 阻断级 / **P1** 高 / **P2** 中 / **P3** 低。

| # | 差距 | 证据（文件:行 / 命令结论） | 对应规范 | 波次 | 严重度 |
|---|------|--------------------------|---------|------|--------|
| F-01 | 行数规则未覆盖 `.ts` composable 与 `components/*.ts` | `.agent/rules/file-length-rule.md:8-13`；实测 `lineupBoard.ts` 484 行、`analysis.ts` 295、`useAttendanceList.ts` 240、`useRecordingList.ts` 223 | PEP 8 精神 + 项目自有规则 | W2-5 | P2 |
| F-02 | 行数豁免自评化、无复核；豁免文件持续增长 | `file-length-rule.md:45,57-59,61-78` vs 实测：`LineupEditor.vue` 1029→**1062**、`lineupBoard.ts` 431→484、`reportData.ts` 327→358 | 同上 | W2-5 | P2 |
| F-03 | ~~出勤率口径散落 10 个文件、前端重复计算~~ → **复核更正（2026-10-02）**：出勤率**公式并无重复实现**——唯一实现是 `backend/app/services/member_service.py:241`（`round(正常/(正常+请假), 4)`，无记录 `null`），前端 27 处命中全部是读取 / 排序 / 展示，并不重算。真实问题为**值与会话格式化多处维护**：低出勤阈值 `0.5` 硬编码 4 处（`AttendanceRatePanel.vue` ×3、`MemberDetailHeader.vue` ×1）、百分比格式化 3 处且存在两种口径（`toFixed(1)` vs `Math.round`）、另有组件内本地 `ratePercent()` | 复核命令：读 `member_service.py:217-254`（唯一公式）+ 前端 `grep 'attendance_rate'`（27 处无重算）；`0.5`/`toFixed(1)` 命中明细见 W2-6 | `AGENTS.md` §2.1（值只允许在权威源维护） | W2-6 ✅（已收敛） | P2（原 P1 降级：确认无公式分歧风险） |
| F-04 | `config.py` 导入期副作用（弱密钥 `sys.exit(1)` + `mkdir`） | `backend/app/core/config.py:9-15,120,130` | PEP 8 / 可测试性 | **W2-6 ✅（2026-10-02 已修复）** | P2 |
| F-05 | 陈旧文件名引用：注释指向 `sim_contribution_v3_20260907.py`，实际只有 v4 | `frontend/src/components/match-data/analysis.ts:44`；`git ls-files backend/scripts` | `AGENTS.md` §3.3 第 6 条 | W0-5 | P2 |
| F-06 | 3 个一次性分析脚本（v4）docstring 齐全，但路径硬编码到**旧仓库绝对位置** 4 处，且除被误引为 v3 外无任何引用 | `backend/scripts/*_v4_20260907.py`（docstring 完整）；`Select-String -CaseSensitive 'e:\code\@Cjy'` 命中 4 处；`analysis.ts:44` 误引 v3 | 可维护性 | W0-5 ✅（已修） | P3 |
| F-07 | 复用逻辑偏重落在组件层（`components` 83 文件 13.7k 行 vs `utils` 3 文件 73 行） | 目录统计（`(Get-Content).Count` 口径） | Vue 风格指南（复用优先） | W2-6 | P3 |
| **F-08** | **`frontend/Dockerfile` 依赖未入库的 `frontend/nginx.conf` → 全新克隆构建必失败** | `frontend/Dockerfile:11`；`git check-ignore -v` → `.gitignore:99`；`Test-Path frontend/nginx.conf` = False；仓库仅有 `frontend/nginx.conf.example` | SLSA v1.2（构建输入完整） | **W1-1** | **P0** |
| **F-09** | **部署入口 `deploy.sh` 未入库且本地不存在** | `DEPLOY.md:54-63`；`git check-ignore -v` → `.gitignore:98` | SLSA v1.2 / 12-Factor V | **W1-2** | **P0** |
| **F-10** | **配置漂移被制度化且无检测**：`deploy.sh` 排除 `docker-compose.yml`/`Dockerfile`/`nginx.conf`/`entrypoint.sh`/`alembic.ini`，这些「只能直接在服务器改」 | `DEPLOY.md:65-70,77-84`；服务器项目目录非 git 仓库（`DEPLOY.md:12`） | 12-Factor III / SLSA | **W1-3** | **P0** |
| **F-11** | **仓库 `docker-compose.yml` 描述的是已废弃拓扑**（映射 80/443 + 挂证书），与 `DEPLOY.md` 单层 TLS 冲突；`tech-stack.md` 架构图同样过时 | `docker-compose.yml:32-37` vs `DEPLOY.md:19-52` vs `tech-stack.md:96-126` | 单一权威源 | **W1-3** | **P0** |
| F-12 | 无回滚方案；镜像无 tag/digest | `DEPLOY.md` 八节无回滚章节（仅 §七 Q6 应急绕过门禁） | DORA 回滚能力 | W3-3 | P1 |
| F-13 | 无 CI；类型检查在镜像构建被跳过且无替代门禁 | `frontend/Dockerfile:6`；`Test-Path .github` = False | Scorecard / CIS | W2-1 | P1 |
| F-14 | 基础镜像 `node:18-alpine`（Node 18 已 EOL）与 `python:3.11-slim`（文档声明 3.13，共 8 处） | `frontend/Dockerfile:1`、`backend/Dockerfile:1`、`README.md:34`、`tech-stack.md:36,57,161`、`ai-context.md:65`、`AGENTS.md:12` | CIS Docker / PEP | W1-5 | P1 |
| F-15 | 依赖未全量锁定（`fastapi>=0.115.0`、`python-multipart>=0.0.18`），无哈希；`tech-stack.md` 却称「实际锁定版本」。**2026-10-02 实证**：一次干净安装解析到 **fastapi 0.142.2 / starlette 1.7.0**（项目开发期为 0.115.x 量级），版本漂移已具体化 | `backend/requirements.txt`（两处范围约束）；本轮 W2-2 安装日志 | PEP 621 / SLSA | W1-4 | P1 |
| F-16 | 无 `/health`、`/metrics`、错误追踪；健康检查直接探根路径 `/` | 全仓 `grep '/health|/metrics|prometheus|sentry'` 无命中；`docker-compose.yml:22-27` | 12-Factor XI / SRE | W3-1 | P2 |
| F-17 | 备份/恢复全手工，无自动化、无演练记录 | `DEPLOY.md:120-149`；全仓无备份脚本命中 | 运维基线 | W3-2 | P2 |
| F-18 | 生产默认暴露 `/docs`、`/redoc`、`/openapi.json`，且安全审查未覆盖 | `backend/app/main.py:36`（未设 `docs_url`）；`SECURITY-REVIEW.md` 无 `/docs|openapi|redoc` 命中 | OWASP Top 10:2025 A02 | **W4-1 ✅（2026-10-02 已关闭）** | P1 |
| F-19 | `CORS_ORIGINS` 硬编码，未外置 | `backend/app/core/config.py:36` | 12-Factor III | W4-3 | P3 |
| F-20 | 3 个已合并远端分支未清理，且命名违反自家规范（大写、非连字符） | `git branch -r --merged`（`Data-analysis`/`UI-design`/`member-panel`，落后 main 65/50/54）；`GIT-GUIDE.md:35` | Scorecard（分支卫生） | W3-5 | P2 |
| F-21 | 规范声明双远端，实际仅 `origin` | `GIT-GUIDE.md:15,18,166-174,281` vs `git remote -v` | 规范一致性 | W3-6 | P2 |
| F-22 | 制品版本与 tag 无联动（`frontend/package.json` 恒 `0.1.0`） | `frontend/package.json:4` | SemVer / 12-Factor V | W3-4 | P2 |
| F-23 | README 声明 MIT 但无 `LICENSE` 文件 | `README.md:134-136`；`Test-Path LICENSE` = False | SPDX/MIT | W0-1 | P2 |
| F-24 | 无 `CONTRIBUTING.md` | `Test-Path` = False（规范散落 `GIT-GUIDE.md`、`.agent/rules/`） | OpenSSF Scorecard | **W4-4 ✅（2026-10-02 已补）** | P3 |
| F-25 | 无 `CHANGELOG.md`（`progress.md` 更新记录代偿） | `Test-Path` = False | Keep a Changelog 1.1.0 | **W3-4 ✅（2026-10-02 已补）** | P3 |
| F-26 | 无公共 `SECURITY.md`（漏洞报告渠道） | `Test-Path` = False（内部 `SECURITY-REVIEW.md` 存在） | OpenSSF Scorecard | **W4-4 ✅（2026-10-02 已补）** | P3 |
| F-27 | 无测试框架；仅 7 个手工 `selfcheck_*.py`（依赖真实库、无 runner） | `git ls-files backend/scripts`；`requirements.txt` 无 pytest | 测试基线 | W2-2 | P1 |
| F-28 | 前端零测试 | `frontend/package.json:6-11` 无 test 脚本 | Vue 风格指南（可测） | W2-2 | P2 |
| F-29 | 后端无 lint/format/类型检查（无 `pyproject.toml`/`ruff.toml`/`.flake8`/`mypy.ini`） | `Test-Path` 全 False；`tech-stack.md:138` 自认未配置 | PEP 8 / PEP 484 | W2-3 | P2 |
| F-30 | 前端无 ESLint/Prettier（仅 `vue-tsc`） | 无相关配置文件 | Vue 风格指南 | W2-3 | P2 |
| F-31 | 无 `.gitattributes`/`.editorconfig`；`git ls-files --eol` = **CRLF 260 / LF 74** 混合 | `git ls-files --eol` 统计；`progress.md:302` 记「按 cr-at-eol 口径检查差异空白」 | Git 官方 / EditorConfig | W0-2 | P1 |
| F-32 | 无 pre-commit / commit-msg 钩子（规范靠自觉） | 无 `.pre-commit-config.yaml`；`package.json` 无 husky | Conventional Commits | W2-4 | P3 |
| F-33 | 无依赖更新自动化（Dependabot/Renovate） | `.github` 不存在 | Scorecard / OWASP A06 | W2-7 | P2 |
| F-34 | 无监控告警（与 F-16 同源，治理视角） | 见 F-16 | SRE / 12-Factor XI | W3-1 | P2 |
| F-35 | 无备份自动化与恢复演练（与 F-17 同源） | 见 F-17 | 运维基线 | W3-2 | P2 |
| F-36 | `.qoder/plans/` 3 个 `.md` 已入库但未登记索引 | `git ls-files .qoder`；`grep qoder` 在 `AGENTS.md`/`architecture.md` 无命中 | `AGENTS.md` §2.2 | W0-6 | P2 |
| F-37 | 陈旧绝对路径：**活引用 25 处**——文档路径 21 处（`architecture.md` 19 + `.agent/rules/code_rule.md` 2）+ 3 个分析脚本硬编码 4 处（DB 快照与 analysis.ts）；另有 `progress.md` 2 处为历史记录中对同期**另一项目** `E:\code\@Cjy\B` 的引用（按 `AGENTS.md` §3.3「历史条目保留」处理）。原记录「23 处」系首次仅 grep `*.md` 且 `Select-String` 默认不区分大小写所致，已更正 | `Select-String -CaseSensitive 'e:\code\@Cjy'`；`code_rule.md:20-21`；`backend/scripts/*_v4_20260907.py` | 文档与代码可移植性 | W0-3 / W0-5 ✅（已修） | P2 |
| F-38 | 文件名大小写与引用不一致：索引内为 `memory-bank/SECURITY-REVIEW.md`，11 个文件按小写 `security-review.md` 引用，且 `architecture.md:196` 记录「已改名为小写」（该记录早于实际落地） | `git ls-files memory-bank`；`Select-String 'security-review\.md'` 命中 11 文件 | `AGENTS.md` §2.2（小写 kebab-case） | W0-4 ✅（已修） | P1 |
| F-39 | `.dockerignore` 残留旧目录名 `.claude` | `backend/.dockerignore:2`、`frontend/.dockerignore:2`（规则目录已改为 `.agent`） | `AGENTS.md` §3.3 第 6 条 | W0-5 ✅（已修） | P2 |
| F-40 | `README.md:88-119` 复制了代码目录树（权威源应仅 `progress.md`） | `README.md:88-119` vs `AGENTS.md:36` | 单一权威源 | W0-7 ✅（已修） | P2 |
| F-41 | 部署章权威源冲突：`tech-stack.md` 称「前端容器 80/443 HTTPS」「后端多阶段构建」「启动脚本 deploy.sh」 | `tech-stack.md:121-126`；`backend/Dockerfile:1-25` 实为单阶段；`deploy.sh` 不在库 | 单一权威源 | W0-8 | P1 |
| F-42 | 引导文档不完整：`start.bat` 默认 `DB_MODE=prod` 指向生产快照 `nsh-server-20260907.db`，README 未提 | `start.bat` 前 25 行；`README.md:40-60` | 12-Factor III / 引导完整性 | W1-6 | P2 |

---

## 5. 分波次执行计划

> 每项任务含：动作 / 涉及文件 / 验收命令（编号见 §8）/ 依赖 / 风险与回滚 / 估算（S ≤ 0.5h，M ≤ 2h，L > 2h）。

### Wave 0 —— 仓库与文档一致性（不改变运行行为，零风险）

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W0-1 | 新增 MIT `LICENSE`（与 `README.md:136` 声明一致，年份与版权人按 D-1 确认） | `LICENSE` | 命令 1 | D-1 | 低；`git rm` 回滚 | S |
| W0-2 | 新增 `.gitattributes`（`text=auto` + 选定 eol）与 `.editorconfig`；如需归一则单独提交 `git add --renormalize .` | `.gitattributes`、`.editorconfig`、全仓 | 命令 2 | D-6 | 中：归一 diff 巨大 → 独立提交便于回滚 | M |
| W0-3 | 清除 23 处陈旧绝对路径，改为仓库相对路径 | `memory-bank/architecture.md`、`memory-bank/progress.md`、`.agent/rules/code_rule.md` | 命令 3 | — | 低 | S |
| W0-4 | `memory-bank/SECURITY-REVIEW.md` → `security-review.md`（Windows 需两步 `git mv`），核对 11 处引用 | 同上 + 引用方 | 命令 3 | — | 低；需在区分大小写环境复核 | S |
| W0-5 | 修正 `analysis.ts:44` 的 v3→v4 引用；给 3 个日期戳脚本加用途说明（或移入 `backend/scripts/archive/`）；清理两处 `.dockerignore` 的 `.claude` | `analysis.ts`、`backend/scripts/*`、两个 `.dockerignore` | 命令 3 | — | 低 | S |
| W0-6 | `.qoder/plans/` 三文档登记入 `architecture.md` **或** 加 `.gitignore` 排除（二选一） | `architecture.md` 或 `.gitignore` | 命令 3 | — | 低 | S |
| W0-7 | 删除 `README.md` 中复制的目录树，改为引用 `progress.md` | `README.md` | 命令 3 | — | 低 | S |
| W0-8 | 按 `DEPLOY.md:19-52` 重写 `tech-stack.md §部署方案`（删除「前端容器 80/443 HTTPS」「后端多阶段构建」等失实描述），并在 `docker-compose.yml` 顶部标注「本地/单机演示拓扑」 | `tech-stack.md`、`docker-compose.yml` 注释 | 命令 3 | — | 低 | M |

### Wave 1 —— 交付链路可复现（解除 P0）

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W1-1 | 将 `nginx.conf.example` 的 A 段落为入库的 `frontend/nginx.conf`（保留占位符，B 段留在 `.example` 供边缘层使用）；`.gitignore` 移除 `frontend/nginx.conf` 并说明「服务器实际文件另有其版本，入库版仅保证构建可复现」 | `frontend/nginx.conf`、`.gitignore`、`frontend/nginx.conf.example`、`DEPLOY.md` | 命令 4 | — | 低；注意与服务器版差异需记录 | M |
| W1-2 | 新增 `deploy.sh.example`（含打包排除清单、路径锚定告警、健康检查失败即非零退出），`DEPLOY.md §三` 补「复制为 `deploy.sh` 并填占位符」 | `deploy.sh.example`、`DEPLOY.md` | 命令 5 | — | 低；不覆盖现有 `deploy.sh` | M |
| W1-3 | ①`docker-compose.yml` 顶部注释定性；②按 D-5 把服务器侧 `docker-compose.yml`/`nginx-proxy` conf 去敏后入库为模板，或提供 `scripts/check-config-drift.sh` | `docker-compose.yml`、`deploy/server/*.example`、`scripts/` | 命令 5 | D-5 | 中；服务器不改动，仅新增模板 | L |
| W1-4 | 后端依赖全量锁定：`pip-compile --generate-hashes` 或 `uv lock`；同步修正 `tech-stack.md:55` 表述 | `backend/requirements*.txt`、`pyproject.toml`（可选）、`tech-stack.md` | 命令 6 | — | 中；锁定后需重建镜像验证 | M |
| W1-5 | 基础镜像升级：`node:22-alpine`、`python:3.13-slim`；统一 8 处文档版本声明 | 两个 `Dockerfile`、`README.md`、`tech-stack.md`、`AGENTS.md`、`ai-context.md` | 命令 4 | — | 中：升级可能暴露兼容问题 → 逐镜像验证 | M |
| W1-6 | `README.md` 补「构建前置（复制 nginx.conf）」与「数据源模式（`DB_MODE`）」小节；快照文件名改为可配置 | `README.md`、`start.bat` | 命令 1 | — | 低 | S |

### Wave 2 —— 质量门禁

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W2-1 | 新增 `.github/workflows/ci.yml`：前端 `npm ci && npm run build`；后端 `compileall` + `alembic upgrade head`（临时库）+ selfcheck；双镜像 `docker build` | `.github/workflows/ci.yml` | 命令 6 | D-3 | 低 | M |
| W2-2 | 把 7 个 `selfcheck_*.py` 迁为 pytest 用例（内存 SQLite 优先），保留脚本作为入口；前端引入 Vitest（先覆盖 composables 纯函数） | `backend/tests/**`、`backend/requirements-dev.txt`、`frontend/src/**/*.spec.ts`、`frontend/package.json` | 命令 6 | — | 中：迁移需保持断言等价 | L |
| W2-3 | 后端 `ruff`（lint+format）+ `mypy`（渐进）；前端 `eslint` + `prettier`（vue preset） | `pyproject.toml`、`ruff.toml`、`.eslintrc`/`eslint.config.js`、`.prettierrc`、`package.json` | 命令 6 | — | 中；首轮会有大量告警 → 按目录分批收敛 | L |
| W2-4 | `pre-commit`（ruff/eslint/行数检查）+ commit-msg 校验（Conventional Commits，中文摘要 ≤50 字符） | `.pre-commit-config.yaml`、`scripts/check-commit-msg.*` | 命令 6 | — | 低 | M |
| W2-5 | `file-length-rule.md` 补 `.ts` 类别上限（建议 200）；豁免清单增「复核日期」列并要求超限 >1.5 倍强制重评；把行数检查脚本化进 CI | `.agent/rules/file-length-rule.md`、`scripts/check-file-length.*` | 命令 6 | — | 低 | M |
| W2-6 | 出勤率口径收敛为后端唯一实现、前端仅展示；`config.py` 导入期副作用改为显式启动校验（保留 fail-closed） | `member_service.py`、`AttendanceRatePanel.vue` 等、`core/config.py`、`main.py` | 命令 6 | — | 中：涉及业务口径，需口径对齐说明 | L |
| W2-7 | 新增 `.github/dependabot.yml`（pip + npm，周更，分组） | `.github/dependabot.yml` | 命令 6 | — | 低 | S |
| **W2-8** | **（2026-10-02 实测新增）** 修复 10 处 `vue/no-mutating-props`：子组件直接变更 props（`query` / `compareChecked` / `filters`），涉及 `match-data/SquadCardsGrid.vue`、`members/MemberTablePanel.vue`、`members/MemberToolbar.vue`、`logs/LogFilterBar.vue`；改为 `emit` 更新 + 父组件 `v-model`，同步解除 ESLint 中该规则的 warn 降级 | 上述 4 个组件及其父组件、`frontend/eslint.config.js` | 命令 6 | — | 中：属行为改动，需浏览器验收 | M |

### Wave 3 —— 运维与发布

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W3-1 | 新增 `GET /health`（含 DB ping）与可选 `/version`；compose 健康检查改探 `/health`；接入 uptime 探活 | `backend/app/main.py`、`backend/app/api/v1/health.py`、`docker-compose.yml` | 命令 7 | — | 低 | M |
| W3-2 | 备份自动化脚本（调用 SQLite backup API）+ 服务器 cron 示例 + 每季恢复演练记录模板 | `scripts/backup-db.sh.example`、`DEPLOY.md §五` | 命令 7 | D-3/D-5 | 低；脚本默认 dry-run | M |
| W3-3 | 发布制品版本化（镜像打 `vX.Y.Z` 或 tar 存档命名）+ `DEPLOY.md` 新增「§回滚」章节（停服→切版本→`up -d`→验证） | `DEPLOY.md`、`deploy.sh.example` | 命令 7 | W1-2 | 中：回滚演练需在非生产先验证 | M |
| W3-4 | 新增 `CHANGELOG.md`（Keep a Changelog 1.1.0：`Unreleased` + Added/Changed/Fixed/Security，按 `v1.0.0/v1.1.0/v1.2.0` 回填）；按 D-4 决定是否联动 `package.json` 版本 | `CHANGELOG.md`、`frontend/package.json`、`GIT-GUIDE.md §8` | 命令 1 | D-4 | 低 | M |
| W3-5 | 清理 3 个已合并远端分支；在 `GIT-GUIDE.md §2.2` 增「合并即删」条目 | 远端（需授权）、`GIT-GUIDE.md` | 命令 1 | D-3 | 中：仅删已合并分支，删除前逐支核对 `--merged` | S |
| W3-6 | 按 D-2 落地单/双远端：改 `GIT-GUIDE.md:15,18,166-174,281` 与 `README`/`DEPLOY.md` 相关表述，或补配 `gitee` 并验证推送 | `GIT-GUIDE.md` 等 | 命令 1 | D-2 | 低 | S |

### Wave 4 —— 安全加固与审查补全

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W4-1 | 生产关闭 `/docs`、`/redoc`、`/openapi.json`（`docs_url=None` 等，条件由 `DEBUG`/`APP_ENV` 决定）；本地保留 | `backend/app/main.py`、`core/config.py` | 命令 6 | — | 低；需确认开发者无依赖在线文档 | S |
| W4-2 | `SECURITY-REVIEW.md` 新增「暴露面清单」小节，按 OWASP ASVS 5.0.0（配置/认证/会话/访问控制/日志）与 Top 10:2025 条目逐项对照并标注结论 | `memory-bank/security-review.md`、`architecture.md` | 命令 3 | W0-4 | 低 | L |
| W4-3 | `CORS_ORIGINS` 外置为环境变量；执行前端与后端依赖漏洞审计（`npm audit` / `pip-audit`）并记录结论 | `core/config.py`、`.env.example`、`memory-bank/security-review.md` | 命令 6 | — | 中：升级依赖需回归 | M |
| W4-4 | 按 D-1 决策补 `SECURITY.md`/`CONTRIBUTING.md`/`CODE_OF_CONDUCT.md`（引用规范而非复制既有内容） | 根目录文件 | 命令 1 | D-1 | 低 | M |

---

## 6. 变更纪律与授权边界

1. **提交纪律**：一次一个主题提交，信息遵循 `.agent/rules/git-commit-message.md`（`<type>(<scope>): <中文摘要 ≤50 字符>`，类型限 `feat/fix/docs/style/refactor/perf/test/chore/ci`）。
2. **授权边界**（沿用 `AGENTS.md` §5）：`git commit`、删除分支/标签、远端与服务器操作、`renormalize` 大批量 diff —— **均须先取得用户许可**（见 §3 D-3）。
3. **文档同步**（`AGENTS.md` §3.3）：改代码 → 同步 `progress.md`（目录树 / 模块表 / 更新记录）；新增或改名文档 → 同步 `architecture.md` 三项（说明 / 目录树 / 更新记录）；受影响的权威源（`database-design.md`/`tech-stack.md`/`design-document-v2.md`）一并更新。
4. **验证纪律**：每项任务完成必须留下**可复现的验证证据**（命令 + 输出结论），写入 §7 进度表；不允许「改完即算完成」。
5. **服务器侧改动**：一律「先备份（`*.bak-日期`）→ 改 → 重建镜像 → 验证」，并在 `DEPLOY.md` 留下同步记录（沿用 2026-09-11/09-15 既有做法）。

---

## 7. 进度跟踪表

| 任务 | 状态 | 完成日期 | 验证证据 | 关联提交 |
|------|------|---------|---------|---------|
| W0-1 新增 LICENSE | ⛔ 阻塞 | | 阻塞项：需用户提供版权人名称/年份（见 §3.1 D-1） | — |
| W0-2 .gitattributes / .editorconfig | ✅ 已完成 | 2026-10-02 | 新增 `.gitattributes`（`* text=auto eol=lf`；`*.bat`/`*.cmd`/`*.ps1` = CRLF；常见二进制标 `binary`）与 `.editorconfig`；配套 `git add --renormalize .` 归一存量换行（改造前 `git ls-files --eol` = i/crlf 260 / i/lf 75），归一独立成提交以便回溯 | chore(repo): 统一换行策略与编辑器配置 |
| W0-3 清理绝对路径（活引用 21 处） | ✅ 已完成 | 2026-10-02 | `Select-String -CaseSensitive 'e:\code\@Cjy'` 仅剩本计划自身证据行（§10 已说明计数口径修正）；`architecture.md` 19 处 + `code_rule.md` 2 处改为仓库相对路径，diff 逐行复核通过 | chore(repo): 统一路径引用与陈旧引用 |
| W0-4 security-review 大小写 | ✅ 已完成 | 2026-10-02 | `git ls-files memory-bank` → `memory-bank/security-review.md`；两步 `git mv` exit 0；`ai-checklist` 警示的「改名文件自身自引用」已核查（L95 本就小写） | 同上 |
| W0-5 陈旧引用与 .dockerignore | ✅ 已完成 | 2026-10-02 | `analysis.ts:44` v3→v4；两个 `.dockerignore` `.claude`→`.agent`；3 个分析脚本 4 处硬编码路径改由 `NSH_DB_PATH`/`NSH_ANALYSIS_TS` 覆盖；`python -m py_compile` 三脚本 exit 0 | 同上 |
| W0-6 `.qoder` 登记或忽略 | ✅ 已完成 | 2026-10-02 | 选择「登记」：`architecture.md` 目录树 + §22 + 更新记录三处登记，并标注「非项目权威文档、仅存档」 | docs(deploy): 对齐部署权威源与外部草案登记 |
| W0-7 README 目录树去重 | ✅ 已完成 | 2026-10-02 | `git diff --stat README.md` = 35 行变更（删除 32 行树体，改为引用 `progress.md`/`architecture.md`） | chore(repo): 统一路径引用与陈旧引用 |
| W0-8 tech-stack 部署章对齐 | ✅ 已完成 | 2026-10-02 | `tech-stack.md` §部署方案 重写为 `DEPLOY.md` 摘要 + 引用；`grep -n '多阶段' tech-stack.md` 仅剩前端一处（后端已改单阶段）；`docker-compose.yml` 顶部标注演示拓扑 | docs(deploy): 对齐部署权威源与外部草案登记 |
| W1-1 nginx.conf 入库 | ✅ 已完成 | 2026-10-02 | `frontend/nginx.conf`（49 行，占位符版）入库；`.gitignore` 解除忽略（`git check-ignore` 未命中）；`nginx.conf.example` 收窄为边缘层模板（171→109 行）；两个 Dockerfile 的每个 `COPY` **上下文源**逐个核对存在（`COPY --from=build` 为多阶段来源，非上下文路径）。**未执行**：镜像实构建——本机 Docker 守护进程未运行（见下方备注） | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W1-2 deploy.sh.example | ✅ 已完成 | 2026-10-02 | 新增 `deploy.sh.example`（92 行）：占位符 + 路径锚定排除清单（含 2026-09-07 教训注释）+ `healthy` 轮询 + 域名入口 200 校验 + 失败非零退出并打印日志；`bash -n`（Git for Windows bash）**exit 0**；`DEPLOY.md §三` 补复制步骤与 nginx.conf 入库说明 | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W1-3 配置漂移治理 | ⏳ 待开始 | | 依赖决策 D-5（生产配置可否去敏入库）；未确认时按计划退化为 `scripts/check-config-drift.sh` diff 告警 | — |
| W1-4 依赖锁定 | ⏳ 待开始 | | 推迟：本机 Python 为 3.14，与目标 3.11/3.13 不一致，锁文件须在目标版本环境生成，否则会写入不兼容标记 | — |
| W1-5 基础镜像升级 | ⏳ 待开始 | | 现状已复核仍在：`node:18-alpine`、`python:3.11-slim`；升级需镜像构建验证，而本机 Docker 守护进程不可用，故推迟 | — |
| W1-6 README 引导补全 | ✅ 已完成 | 2026-10-02 | README 新增「数据源模式（`DB_MODE`）」小节（prod 快照 / dev 本地库、缺失回退、`.db` 不入库）与 Docker 部署段的 `nginx.conf` 构建前置说明 | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W2-1 CI 工作流 | ✅ 已完成 | 2026-10-02 | `.github/workflows/ci.yml`：4 个 job（backend 编译+迁移+导入 / frontend `npm ci`+`vue-tsc`+`vite` / repo-hygiene 行数+陈旧路径+换行 / docker-build 双镜像＝F-08 回归护栏）。**本机前置验证**：`npm ci` exit 0、`vue-tsc` 无类型错误、`vite build` 成功（12.27s）、`compileall` exit 0。**CI 本身未运行**（本会话无 GitHub Actions 环境），需 push 后观察首次结果 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-2 测试体系（pytest/Vitest） | ✅ 已完成（`selfcheck_indicators` 改造除外） | 2026-10-02 | **后端**：`backend/pytest.ini`（`python_files` 同时匹配即收集 6 个既有 selfcheck）+ `backend/tests/`（4 模块：安全工具 / 弱密钥门禁 / 权限矩阵 / 姓名规范化）+ CI `python -m pytest` → **78 passed + 57 subtests（24.23s）**。**前端**：`frontend/vitest.config.ts` + 4 个 spec（constants / profession / scheduleSort / analysis，共 **38 用例**）+ `package.json` test/test:watch + CI `npm run test` → **38 passed（1.73s）**；**vitest 须用 3.x**（5.x peer 要求 vite ≥6.4，与项目 vite 5.4 冲突，实测 npm ERESOLVE）。**待办**：`selfcheck_indicators.py` 由模块级断言脚本改造为用例类；组件级/接口级用例（httpx 已装待用） | ci(test): 补齐前端 Vitest 测试体系 |
| W2-3 lint/format/类型检查 | ✅ 已完成（mypy 除外） | 2026-10-02 | **后端 ruff**：`backend/ruff.toml`（E4/E7/E9/F，迁移与 3 个一次性脚本按文件豁免）+ `ruff==0.12.0` + CI 接线；基线 52 → 修复 9 项 → **All checks passed!**。**前端 ESLint/Prettier**：`frontend/eslint.config.js`（vue `flat/essential` + typescript-eslint + skipFormatting；**刻意不用 `flat/recommended`**，避免数百条排版告警）+ `.prettierrc.json` + 5 个 devDependencies + `package.json` 脚本 + CI 接线；基线 14 errors → 修复 4 处 `any`（导出 `SlotDragEvent` 最小结构类型）→ **0 error / 10 warning**；`npm run build`（vue-tsc）exit 0 证明类型改动安全。**未做**：mypy；`E501`/`I`/`UP`/`B`、vue 排版规则与 Prettier 一次性格式化（均需独立大改提交） | ci(lint): 接入前端 ESLint 与 Prettier 配置 |
| W2-4 pre-commit 与提交校验 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_commit_msg.py`（内置 15 条用例自检 **exit 0**；支持消息文件 / `--stdin`；BOM 容错）、`.githooks/commit-msg`（正例 exit 0、反例 exit 1）、`scripts/install_git_hooks.sh`（`bash -n` 通过）、`.github/commit-msg-baseline` 与 CI `commit-msg` job（范围校验 10 个提交 **违规 0**，注入两个反例均 exit 1）；规则文档补 `merge` 类型与「自动校验」小节。**偏离说明**：未引入 pre-commit 框架，改用零依赖的 `core.hooksPath` + 版本化钩子（ruff / 行数门禁已在 CI 中强制） | ci(commit): 提交消息校验与版本化钩子 |
| W2-5 行数规则补全与检查脚本 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_file_length.py`（标记+登记双重校验、清单悬空、增长 ≥20% 提醒）与规则文档「前端 TS」类别；本地实检 211 文件 / 14 条登记 **exit 0**。**偏差记录**：计划原拟 TS 上限 200，实施改为 **300**（composable 与组件同为状态控制器；若设 200，`analysis.ts` 295、`useAttendanceList.ts` 240、`useRecordingList.ts` 223 会在新门禁上线首日即失败，违背「门禁不得先红」原则），已在规则文档写明理由 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-6 出勤率口径收敛 + config 副作用 | ✅ 已完成 | 2026-10-02 | ①**口径收敛（批次 7）**：新增 `frontend/src/utils/attendance.ts` 单一来源（阈值常量 / 低出勤判定 / 进度条颜色 / 百分比格式化 `digits` 参数），收敛 7 处硬编码（阈值 4 + 格式化 3）与组件内本地 `ratePercent()`；两种展示口径作为显式参数保留。②**F-04 修复（批次 8）**：弱密钥门禁由 `config.py` **导入期**移至**应用启动期**——新增 `InsecureSecretKeyError`、`FATAL_SECRET_KEY_MESSAGE`（**原文逐字保留**）、`WEAK_SECRET_KEY_WARNING`、`validate_secret_key()`（抛异常、可断言）、`enforce_secret_key()`（打印 FATAL + 退出码 1），移除模块级调用；`main.py` 新增 `startup_checks()` 并在 `on_startup` 首要位置调用（alembic 与 CI 导入步骤不再继承退出行为）。目录创建刻意保留在导入期（幂等、被 logging/SQLite 路径依赖，理由见 `config.py` 末尾）。实测：`ruff check .` **All checks passed!**、`compileall` exit 0、`pytest tests/test_config_gate.py` **15 passed + 2 skipped**（跳过项需 FastAPI，CI 执行），子进程回归证明「仅导入 config → exit 0 无 FATAL」「调用门禁 → 非零退出 + FATAL」。**语义保持**：文案逐字不变、拒绝启动不变；退出码在 uvicorn lifespan 路径由 uvicorn 以「启动失败」收尾（非零），直接调用 `enforce_secret_key()` 恒为 1。另修复 `tests/test_permissions.py` 未使用的 `unittest` 导入（否则 CI ruff 会红） | refactor(core): 弱密钥门禁改为启动期校验并补齐回归 |
| W2-7 Dependabot | ✅ 已完成 | 2026-10-02 | `.github/dependabot.yml`：pip / npm 周更分组各限 5、docker 双目录周更、github-actions 月更；依据 OpenSSF Scorecard 与 OWASP A06 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-8 修复 props 变更债（10 处） | ⏳ 待开始 | | 实测清单（ESLint warn 输出）：`match-data/SquadCardsGrid.vue:32`（compareChecked）、`members/MemberTablePanel.vue:78,79`（query）、`members/MemberToolbar.vue:5,13,16`（query）、`logs/LogFilterBar.vue:4,10,18,21`（filters）；修法为 emit 更新 + 父组件 v-model，完成后解除 `frontend/eslint.config.js` 中的 warn 降级 | — |
| W3-1 /health 与探活 | ✅ 已完成 | 2026-10-02 | 新增 `backend/app/api/v1/health.py`：`GET /health`——数据库可查询 → `200 {status:ok,database:ok}`；库不可用 → `503 {status:degraded,database:error}`（**刻意不抛 500**：否则对外表现为「应用崩溃」而非「依赖不可用」）。`docker-compose.yml` 的 healthcheck 由根路径 `http://127.0.0.1:8000/` 改探 `/health`（原方案只能证明进程存活，数据库挂掉仍报健康）；同一端点另挂 `/api/v1/health`，经既有 `/api/*` 反代对外可达，供外部 uptime 探活（不需要时可在边缘 Nginx 拦掉）。`DEPLOY.md §二` 新增「健康检查与在线 API 文档」小节（含 backend 无宿主端口映射时的手动探活命令）。验证：`pytest tests/test_health.py` → **5 passed**（200/503 语义 + 双路径路由可达 + 文档开关子进程断言）；全量 **93 passed + 67 subtests passed（27.90s）**。**待办**：`/version` 端点未加（与 D-4 版本联动耦合）；`app.on_event("startup")` 已被 FastAPI 弃用，迁移 lifespan 列为后续 | feat(ops): 新增健康检查端点并关闭生产 API 文档 |
| W3-2 备份自动化与演练 | ⏳ 待开始 | | | |
| W3-3 制品版本化与回滚 | ⏳ 待开始 | | | |
| W3-4 CHANGELOG 与版本联动 | 🔄 进行中 | 2026-10-02（CHANGELOG 部分） | `CHANGELOG.md` 已建立（Keep a Changelog 1.1.0 + SemVer 2.0.0）：`[未发布]` 段按新增/变更/修复/安全四类汇总本轮合规化改动；`[1.2.0] - 2026-10-02`、`[1.1.0] - 2026-09-16`、`[1.0.0] - 2026-08-27` 三段**依据 `git log <旧标签>..<新标签>` 归并并在文件内标注依据**（不逐条回溯）；比较链接指向真实仓库 URL（`github.com/yyyyyyyy-cco/nsh-management`）；文件内记录 `frontend/package.json` 版本 `0.1.0` 与标签 `v1.x` 不一致（对应 F-16）。**待办**：按 D-4 落地版本联动（调整 package.json 或改为运行时注入）并在 `GIT-GUIDE.md §8` 发布清单加入「更新 CHANGELOG」条目 | docs(changelog): 新增更新日志与社区政策文档 |
| W3-5 分支治理 | ⏳ 待开始 | | | |
| W3-6 远端策略落地 | ⏳ 待开始 | | | |
| W4-1 关闭生产 API 文档 | ✅ 已完成 | 2026-10-02 | `core/config.py` 新增 `api_docs_enabled()`（生产 False / 开发 True，复用既有 `_is_production()`）；`app/main.py` 按该开关设置 `docs_url` / `redoc_url` / `openapi_url`（生产为 `None` → 404），本地开发保留。**未采用 `DEBUG` 作判据**：`DEBUG` 控制异常详情脱敏，与「部署环境」语义不同，用 `APP_ENV`/容器特征更贴合本任务原意。验证（子进程断言，因开关在 import 时求值）：`APP_ENV=production|prod` → 三者均 `None`；`development` → `/docs`、`/redoc`、`/openapi.json` 均在。文档同步 `DEPLOY.md §二`。`security-review.md` 的 ASVS/Top10 逐项对照仍由 W4-2 完成 | feat(ops): 新增健康检查端点并关闭生产 API 文档 |
| W4-2 ASVS/Top10 对照补审查 | ⏳ 待开始 | | | |
| W4-3 CORS 外置与依赖审计 | ⏳ 待开始 | | | |
| W4-4 SECURITY/CONTRIBUTING/CoC | ✅ 已完成 | 2026-10-02 | 按 D-1（公开仓库）补齐三份根文档：`SECURITY.md`（支持版本范围 / GitHub 私有安全公告为首选渠道 / 备用邮箱占位符 / 处理时限目标 / 已知接受风险指向 `security-review.md` 权威源）、`CONTRIBUTING.md`（协作约定摘要 + 权威源链接 + 与 `.github/workflows/ci.yml` 对应的本地门禁命令，**未复制**权威源内容）、`CODE_OF_CONDUCT.md`（Contributor Covenant 2.1 官方简体中文译本逐字采用，保留 CC BY-SA 4.0 署名）。验证：三文件与 `CHANGELOG.md` 均入库、互相引用链接有效、`scripts/check_file_length.py` 通过。**未完成**：SECURITY.md 与 CoC 的备用联系邮箱为占位符（需用户提供后填写） | docs(changelog): 新增更新日志与社区政策文档 |

状态图例：⏳ 待开始 / 🔄 进行中 / ✅ 已完成 / ⛔ 阻塞（写明阻塞项与所需决策）

> **环境备注（2026-10-02）**：本机 `docker --version` = 28.1.1，但**守护进程未运行**（`docker info` 无输出；`docker build` 报 `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`）。因此一切依赖镜像构建的验收（W1-1 的实构建、W1-5 的升级验证）在本环境**无法执行**；已改用「Dockerfile `COPY` 上下文源逐个存在性核对 + 配置入库状态 + `bash -n`」作为替代证据，真正的镜像构建门禁由 W2-1 的 CI 补齐。此外本机无 WSL/`sh`，`bash -n` 使用 Git for Windows 的 `C:\Program Files\Git\bin\bash.exe`。

---

## 8. 回归命令清单

> 以下命令为本计划的验收依据；实施时逐条执行并记录输出结论。

```bash
# 1. 仓库卫生与文档一致性
git status --porcelain                          # 期望：干净
git ls-files --eol | awk '{print $1}' | sort | uniq -c   # 期望：单一 eol
grep -rn 'e:\\code\\@Cjy' --include='*.md' .    # 期望：无输出
git ls-files memory-bank | grep -i security     # 期望：全小写 security-review.md

# 2. 换行归一后复核
git diff --stat                                 # 期望：归一提交单独成组

# 3. 文档引用与索引一致性
grep -rn 'security-review\.md' --include='*.md' memory-bank | wc -l   # 引用数应与实体匹配

# 4. 前端构建（含类型检查）与镜像构建
cd frontend && npm ci && npm run build
docker compose build                            # 期望：双镜像构建成功（当前会因缺 nginx.conf 失败）

# 5. 部署链路
bash -n deploy.sh.example                       # 语法检查
grep -n 'nginx.conf' DEPLOY.md README.md        # 期望：说明构建前置

# 6. 后端门禁与测试
cd backend && python -m compileall -q app
alembic upgrade head                            # 临时库
python -m pytest -q                             # W2-2 之后
ruff check . && mypy app                        # W2-3 之后

# 7. 运行时验证
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health   # 期望 200
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/docs     # 生产期望 404
```

---

## 9. 风险登记

| 风险 | 触发条件 | 影响 | 缓解 |
|------|---------|------|------|
| 换行归一整仓 diff 淹没代码评审 | 执行 W0-2 归一 | PR 不可读 | 独立提交、单独 review、不与逻辑改动混合 |
| 基础镜像升级引入不兼容 | W1-5 升 Node 22 / Python 3.13 | 构建或运行失败 | 先本地双镜像构建 + 冒烟，再进 CI；保留旧 Dockerfile 于分支 |
| 依赖全量锁定后装不出（旧版本被 yank） | W1-4 | CI 失败 | 锁定时立即跑 CI；必要时回退到范围约束并记录 |
| 打包排除清单被误改导致覆盖服务器配置 | 触碰 `deploy.sh.example` | 生产宕机 | 保留 `DEPLOY.md:65-75` 的「严禁移除 + 路径锚定」警示原文 |
| 回滚演练影响生产 | W3-3 | 短时不可用 | 先在非生产环境演练，生产侧选低峰窗口 |
| 删分支/改远端误操作 | W3-5/W3-6 | 丢历史引用 | 删前 `git branch -r --merged` 逐支核对；保留 reflog；需显式授权 |

---

## 10. 附：审查方法与限制

- **方法**：静态只读审查（文件读取、内容检索、目录枚举、Git 元数据），覆盖 338 个跟踪文件、27 份 Markdown 文档、2 个 Dockerfile、1 个 compose、110 个后端 `.py`、164 个前端 `.vue/.ts`。
- **限制**：
  - 未运行构建、类型检查、测试与迁移（`npm run build`/`pytest`/`alembic upgrade` 均未执行），故 F-13/F-27/F-29/F-30 的「是否已通过」属**待验证**；
  - 未访问生产服务器，F-10/F-11 的漂移程度只能定性；
  - 仓库可见性、协作者规模、生产配置敏感度未知，对应 §3 D-1/D-5；
  - 行业规范版本以官方站点为准（ASVS 5.0.0、OWASP Top 10:2025、Keep a Changelog 1.1.0、SLSA v1.2 已于 2026-10-02 核对）。
- **门禁与历史引用约定（2026-10-02）**：CI 的 `repo-hygiene` job 用 `grep -F` 严格拦截「旧仓库绝对路径」字面量（完整形式＝`e:\code\@Cjy\` 接仓库目录名；模式串在 workflow 内拆开书写以避免自命中，`node_modules`/`dist`/`.git` 已排除）。因此**引用历史旧路径一律写作 `e:\code\@Cjy\...`（省略号形式）**——落地时曾发现两条更新记录与本说明含完整字面量会让门禁首发即红，故统一改为省略号形式；本计划 §4/§7 均按此约定书写。
- **计数口径**：行数使用 `(Get-Content $f).Count`（含空行），与仓库既有文档的统计口径可能不同，故豁免清单中的登记行数与本计划实测值并列展示（见 F-02）。
- **计数口径修正（2026-10-02）**：首次统计陈旧绝对路径时只检索 `*.md`，且 `Select-String` 默认**不区分大小写**，导致 ① 漏计 3 个分析脚本中的 4 处硬编码路径；② 误将 `progress.md` 中对同期另一项目 `E:\code\@Cjy\B` 的历史引用计入本仓库路径。§4 的 F-06/F-37 已按 `-CaseSensitive` + 全后缀复核结果更正。该项修正本身即为「审查结论必须可复核」的示范：凡计数结论都应记录所用命令与匹配选项。

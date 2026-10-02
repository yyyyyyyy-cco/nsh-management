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
| F-15 |\1| **W1-4 🔄（2026-10-02 部分修复：范围约束已改精确锁定 + 门禁接线；哈希锁文件待 3.11 环境生成）** | P1 |
| F-16 | 无 `/health`、`/metrics`、错误追踪；健康检查直接探根路径 `/` | 全仓 `grep '/health|/metrics|prometheus|sentry'` 无命中；`docker-compose.yml:22-27` | 12-Factor XI / SRE | W3-1 | P2 |
| F-17 | 备份/恢复全手工，无自动化、无演练记录 | `DEPLOY.md:120-149`；全仓无备份脚本命中 | 运维基线 | W3-2 | P2 |
| F-18 | 生产默认暴露 `/docs`、`/redoc`、`/openapi.json`，且安全审查未覆盖 | `backend/app/main.py:36`（未设 `docs_url`）；`SECURITY-REVIEW.md` 无 `/docs|openapi|redoc` 命中 | OWASP Top 10:2025 A02 | **W4-1 ✅（2026-10-02 已关闭）** | P1 |
| F-19 | `CORS_ORIGINS` 硬编码，未外置 | `backend/app/core/config.py:36` | 12-Factor III | **W4-3 ✅（2026-10-02 已外置）** | P3 |
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
| F-43 | CSP 过宽：`script-src` 含 `unsafe-inline` / `unsafe-eval`，削弱 XSS 防护（另 `X-XSS-Protection` 为已被 CSP 取代的历史头） | `frontend/nginx.conf.example:71`；安全审查 §十五 15.4-1/6 | OWASP Top 10:2025 A02 / ASVS 配置域 | **W4-5 ✅（2026-10-02 已收紧：`script-src 'self'`，去 `unsafe-inline`/`unsafe-eval`；页面级验收未做）** | {m.group(3)} |
| F-44 | 无告警通道：审计日志已落库，但异常/错误率上升无人被告知（日志与告警只做了前者） | `backend/app/main.py` AuditLogMiddleware；安全审查 §十五 15.4-2 | OWASP Top 10:2025 A09 | **W4-6 ✅（2026-10-02 已实现：阈值告警循环 + webhook 可选，未配置时写 WARNING 不静默）** | P2 |
| F-45 | 无威胁建模留痕（STRIDE/攻击面分析）：有权限矩阵与设计文档，但缺建模记录 | `memory-bank/design-document-v2.md`；安全审查 §十五 15.4-4 | OWASP Top 10:2025 A06 | W4-7 | P3 |
| F-46 | ASVS 5.0.0 仅做**域级**对照，未做条目级逐条核对（编号格式 `v5.0.0-x.y.z`） | 安全审查 §十五 15.3；官方编号格式实取自 owasp.org/projects/asvs | OWASP ASVS 5.0.0 | W4-8 | P3 |
| F-47 | **导出文件公式注入**：成员姓名/备注等用户输入以 `=`/`+`/`-`/`@` 开头时，openpyxl 会写成公式（`data_type='f'`），管理员打开导出的 xlsx 时 Excel 可能求值（可构造 `HYPERLINK`/`DDE` 对外请求）| 威胁建模 §十六 | **W4-7（2026-10-02 已修复：导出统一 `_text_cell` 显式声明文本单元格 + 往返回归 5 用例）** | P2 |
| F-48 | **依赖版本陈旧**：`python-jose==3.3.0`（2021 年发布）长期未升，而上游 3.4.0 即为修复 JWT 相关 CVE 而发布；同类「固定版本是否已陈旧」本轮只核实了这一项，其余未核对 | PyPI 元数据 + 上游发布史 | **W1-8（2026-10-02 已升级到 3.5.0 并跑通全量套件）** | P1 |
| **F-49** | **容器降权不完整（2026-10-02 更正，仅前端成立）**：`frontend/Dockerfile` 创建了 `appuser/appgroup` 并 chown 了 `/usr/share/nginx/html`、`/var/cache/nginx`、`/var/log/nginx`、`/var/run/nginx.pid`，**却从未 `USER appuser`** → nginx 实际以 root 运行（准备非 root 的痕迹在，接线没做）。**原结论「后端也以 root 运行」有误**：`backend/entrypoint.sh` 第 9 行 `exec gosu appuser "$@"` 已把权限降为 appuser，`backend/Dockerfile` 亦安装 gosu 并注释说明（证据：两文件逐行核对）。 | `frontend/Dockerfile`、`frontend/nginx.conf`（`listen 80` 需改非特权端口）、`docker-compose.yml`/`DEPLOY.md §二`（上游端口联动） | **W1-9（范围已收窄为前端）**；改 `USER` 属加固增强（CIS Docker 4.1） | P2 |
| F-50 | **授权失败的读操作未审计**：审计中间件只覆盖写方法，GET 的 403 不落库（ASVS 16.3.2） | `app/main.py` `AUDIT_METHODS` | **W4-9 ✅（2026-10-02 已修复：读方法+带凭证+401/403 也留痕）** | P2 |
| F-51 | **审计详情未转义换行/控制字符**（ASVS 16.4.1 日志注入面） | `app/services/log_service.py` | **W4-9 ✅（2026-10-02 已修复：控制字符转义 + 端到端回归）** | P2 |
| F-52 | **口令策略偏离 ASVS**（**2026-10-02 更正**：原判「可设 1 位口令」有误——schema 层已有 `min_length=8`；实为：强制字母+数字**违反 6.2.5**、无上下文词表、**策略零测试**、无泄露口令集比对） | `app/schemas/config.py`、`app/core/password_policy.py` | **W4-10 ✅（2026-10-02 已修复；6.2.12 泄露口令比对为取舍）（残留判定：6.2.4、6.2.12）** | P1 |
| F-53 | **无用户自助改密；管理员重置时可直接设定新口令**（ASVS 6.2.2/6.2.3/6.4.6） | `app/api/v1/auth.py`、`app/services/auth_service.py` | **W4-10 🔄（自助改密已实现；6.4.6 管理端设定口令仍为取舍）** | P2 |
| F-54 | **前后端口令口径分叉（本轮规范复核发现）**：后端按 ASVS 6.2.5 放开字符组成后，`ConfigGuildPanel.vue` 仍内联「必须同时含字母和数字」的校验，**前端会拦住纯字母/纯数字口令而 API 会接受**（属用户可见不一致；schema 描述文案也仍写旧规则） | `frontend/src/views/config/ConfigGuildPanel.vue`、`backend/app/schemas/config.py` | **W4-12 ✅（2026-10-02 已修复）** | P2 |
| F-55 | **前端构建上下文的秘密文件处理不一致**：`backend/.dockerignore` 排除 `.env`，而 `frontend/.dockerignore` 未排除 → 前端构建上下文可能带入游离的 `.env*`（Vite 会自动读取）；另 `.gitignore` 漏 `.env.development` 一类变体 | `.dockerignore`、`.gitignore` | **W4-18 ✅（2026-10-02 已修）** | P3 |
| F-56 | **图像导出路径无测试覆盖**：`app/utils/image_export.py` 的 `draw_members_png`（常驻库导出图）在 `tests/` 中无任何引用，升级 Pillow 后只能给「导入级 + 字体加载」证据，缺像素级断言 | `backend/tests/` | **W1-11 ✅（2026-10-03 已补 6 个用例，全量 164 passed）** | P3 |
| F-57 | **bcrypt 只使用口令前 72 字节且静默截断**：实测「前 72 字节相同、后缀不同」的两个口令互相通过校验；口令策略上限为 **128 字符**（中文可达 384 字节）→ 边界可达 | `backend/app/core/password_policy.py`、`backend/app/core/security.py` | **W1-12 ✅（2026-10-03 已修：新哈希先 `base64(SHA-256(口令))` 预哈希，任意长度完整参与；旧哈希登录时惰性升级）** | P2 |
| F-58 | **`bcrypt` 4.x 对截断/非法哈希会 Rust panic**（`pyo3_runtime.PanicException`，MRO `PanicException → BaseException → object`，**非 `Exception` 子类**）：直接调用会让库中损坏哈希导致登录 500；passlib 时代返回 `False` | `backend/app/core/security.py` | **W1-10 ✅（2026-10-03 已修）** | P2 |
| F-59 | **前端开发期工具链存在 6 条公告**（vite 5.4.21 ×3、esbuild 0.21.5 ×2〔1 条已撤回〕、vitest 3.2.7 ×1）：均为 **dev-only**（dev server / 测试运行时），且 `vite.config.ts` 未设 `host` → 默认仅绑 localhost；修复需跨大版本（vite 6/7、esbuild ≥0.25、vitest ≥4） | `frontend/package-lock.json`、`frontend/vite.config.ts` | **W1-13 ✅（2026-10-03 已升级：vite 6.4.3 / vitest 4.1.11 / esbuild 0.25.12；6 条中 5 条清除，剩余 1 条经 API 实证为上游已撤回）** | P3 |
| F-60 | **构建产物被提交入库**：`frontend/tsconfig.node.tsbuildinfo`（`vue-tsc -b` 生成）经 `git add -A` 一并提交，且 `.gitignore` 未覆盖 `*.tsbuildinfo` | `.gitignore`、`frontend/` | `.gitignore` **已补**（2026-10-03）；**移出版本库（`git rm --cached`）属删除操作，按 `AGENTS.md §5` 需用户单独授权 → 待授权（W2-13）** | P3 |
| F-61 | **默认管理员口令是应用自身黑名单里的弱口令**：文档与 `.env.example` 的 `admin123` 同时出现在 `password_policy.CONTEXT_WORDS` 中 ✗——系统发布了「自己认为太弱」的默认口令（现由「首登后改密」要求缓解） | `.env.example`、`README.md`、`DEPLOY.md` | **待决策（W1-14）** | P2 |
| F-62 | **弱密钥门禁的 hex 豁免通道放过了零熵密钥**：`_secret_key_is_weak` 对「≥64 字符纯 hex」恒判为强，于是 CI 里的 `0123456789abcdef…`（顺序十六进制、零熵）**能通过生产门禁** ✗ | `backend/app/core/config.py` | **已修（2026-10-03）**：豁免前增加 `_hex_is_low_entropy`（周期性 + 不同字符数 <8）+ 显式封禁该字面量 + `HexEntropyTest` 4 用例 | P2 |
| F-63 | **计划出现重复的顶层章节号（两个 `## 9.`）**：`9. 风险登记` 与 `9. 验收清点` 同号（第 46 轮追加时未检查唯一性）；且**验收清点里的数字已过时**（后端 158→178、前端 lint 10 warning→0、构建 ≈19s→≈8.4s、扫描 353→360 个文件）——执行类文档的数字最易腐坏 | `.agent/plans/compliance-remediation-plan.md`、`scripts/check_plan_integrity.py` | **已修（2026-10-03）**：验收清点改为 **§11**（编号 1–11 唯一且单调）、数字按实测刷新、复跑清单补到 7 道；并给 `check_plan_integrity` 增加**章节编号唯一性检查**（含 2 条自检样例 + 反向验证） | P3 |
| F-64 | **技术栈权威源未随依赖升级回填**（AGENTS §2.1 规定技术栈版本权威源为 `tech-stack.md` + `requirements.txt`）：文档仍写 `Vite 5.x`（实际 **6.4.3**）、`Pillow 11.x`（实际 **12.3.0**，W1-8 升级时漏回填）、`Vitest 3` 并附「**版本须为 3.x**（5.x 需 vite ≥6.4，与 vite 5.4 冲突）」的**已失效约束**（实际 4.1.11；已核实 peer：4.1.11 → `vite ^6\|\|^7\|\|^8`、5.0.0 → `vite ^6.4\|\|^7\|\|^8`）、lint 仍写 `10 warning`（实际 **0**） | `memory-bank/tech-stack.md`、`scripts/check_doc_numbers.py` | **已修（2026-10-03）**：四处按实测回填（另修 passlib 残留表述与 `；；`）；并给 `check_doc_numbers` 增加**「tech-stack ↔ 清单实际版本」交叉核对**（`real_pins()` + `check_tech_stack()`，含反向验证） | P2 |
| F-65 | **两份 `.env.example` 均未说明自身作用域与权威关系**：根目录是**容器/Compose 部署权威模板**（`docker-compose.yml` → `env_file: .env`，且为 `check_env_docs.py` 的校验对象），`backend/.env.example` 是**本地直接运行时的参考**（口令为占位值）——但两处都没有写明，读者（含本次审计）会把**预期差异误读为漂移**；`ai-checklist §3.1` 的对应检查项自 2026-08-26 起一直**未勾选** | `.env.example`、`backend/.env.example`、`memory-bank/ai-checklist.md` | **已修（2026-10-03）**：两份模板头部互相注明作用域/权威关系（**不改任何值**）；`ai-checklist §3.1` 悬空项按核实结论结清 | P3 |
| F-66 | **§8 回归命令清单未随实现回填，且含过时/不可运行的命令**：缺 `npm run lint`、`npm run test`、`check_commit_msg.py`、`check_doc_refs.py`；`docker compose build` 注释仍写「当前会因缺 nginx.conf 失败」（W1-2 已补齐）；`python -m pytest -q`/`ruff check .` 仍标「W2-2/W2-3 之后」；`mypy app` **从未引入**（tech-stack 明写「尚未引入」）→ 清单里躺着跑不通的命令 | `.agent/plans/compliance-remediation-plan.md` | **已修（2026-10-03）**：补齐缺失项（含 `check_doc_refs.py` 标注**仅报告**）、删除过时说明、声明 §8 为**权威清单**（CONTRIBUTING 与 CI 同款）、登记 `mypy` 未引入 | P3 |
| F-67 | **「记录在案的待办」没有登记为任务**：`W2-3` 完成说明含「待收紧：E501 / `ruff format` / `I`·`UP`·`B` / vue `flat/recommended` / Prettier 一次性格式化；后端 mypy 尚未引入」，`F-29` 指向的 W2-3 已 ✅ 且注明「mypy 除外」，但全仓**没有**承接这些剩余项的任务 → 计划作为合规台账出现「已知未做但不在清单」的缺口 | `.agent/plans/compliance-remediation-plan.md` | **已补登记（2026-10-03）**：新增 **W2-14**（§5/§7 成对）承接全部剩余项 | P3 |
| F-68 | **CI 与文档不一致 + 过时注释**：`repo-hygiene` 里 7 道门禁中**只有 `check_file_length` 未跑 `--self-test`**（其余 6 道 + `check_commit_msg` 均跑 ✓，而计划 §8/§11.4 与 CONTRIBUTING 写的都是「自检 + 实跑」两步）→ 该门禁的 9/9 内置自检**从未在 CI 执行**；`ci.yml` 头部仍保留「后续扩展：W2-2 之后加 pytest / W2-3 之后加 ruff·mypy·eslint」的**已满足前置条件**的设想 | `.github/workflows/ci.yml` | **已修（2026-10-03）**：补 `--self-test`（并本地等价复跑通过 ✓）；过时注释改为**现状说明**（含「仍未接入：mypy（W2-14）」「Node/Python 基座待 W1-5/W1-7 统一」）| P3 |

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
| W0-9 | **（2026-10-02 新增）** 环境变量文档联动门禁：`scripts/check_env_docs.py` —— 校验「代码 `os.getenv` 读取的变量」与「`.env.example` 文档化的条目」一致（AGENTS §3.3 第 7 条固化）；注释掉的示例条目也算已文档化，行内注释不误判 | `backend/app/**`、`.env.example`、`.github/workflows/ci.yml` | 命令 9 + CI `repo-hygiene` | W0-2 | 低：门禁本身有 11 条自检 | S |

### Wave 1 —— 交付链路可复现（解除 P0）

| 任务 | 动作 | 涉及文件 | 验收 | 依赖 | 风险/回滚 | 估算 |
|------|------|---------|------|------|----------|------|
| W1-1 | 将 `nginx.conf.example` 的 A 段落为入库的 `frontend/nginx.conf`（保留占位符，B 段留在 `.example` 供边缘层使用）；`.gitignore` 移除 `frontend/nginx.conf` 并说明「服务器实际文件另有其版本，入库版仅保证构建可复现」 | `frontend/nginx.conf`、`.gitignore`、`frontend/nginx.conf.example`、`DEPLOY.md` | 命令 4 | — | 低；注意与服务器版差异需记录 | M |
| W1-2 | 新增 `deploy.sh.example`（含打包排除清单、路径锚定告警、健康检查失败即非零退出），`DEPLOY.md §三` 补「复制为 `deploy.sh` 并填占位符」 | `deploy.sh.example`、`DEPLOY.md` | 命令 5 | — | 低；不覆盖现有 `deploy.sh` | M |
| W1-3 | ①`docker-compose.yml` 顶部注释定性；②按 D-5 把服务器侧 `docker-compose.yml`/`nginx-proxy` conf 去敏后入库为模板，或提供 `scripts/check-config-drift.sh` | `docker-compose.yml`、`deploy/server/*.example`、`scripts/` | 命令 5 | D-5 | 中；服务器不改动，仅新增模板 | L |
| W1-4 | 后端依赖全量锁定：`pip-compile --generate-hashes` 或 `uv lock`；同步修正 `tech-stack.md:55` 表述 | `backend/requirements*.txt`、`pyproject.toml`（可选）、`tech-stack.md` | 命令 6 | — | 中；锁定后需重建镜像验证 | M |
| W1-5 | 基础镜像升级：`node:22-alpine`、`python:3.13-slim`；统一 8 处文档版本声明（**2026-10-02 口径调整**：镜像升级拆分到 W1-7；文档已按**现状**统一为 3.11，见 §7 W1-5 说明） | `backend/Dockerfile`、`frontend/Dockerfile`、`README.md`、`AGENTS.md`、`tech-stack.md` | 命令 6 | W1-4 | 中：基座升级需镜像构建验证 | M |
| W1-6 | `README.md` 补「构建前置（复制 nginx.conf）」与「数据源模式（`DB_MODE`）」小节；快照文件名改为可配置 | `README.md`、`start.bat` | 命令 1 | — | 低 | S |
| W1-7 | **（2026-10-02 拆分自 W1-5）** 基础镜像升级：`node:18-alpine` → `node:22-alpine`、`python:3.11-slim` → `python:3.13-slim`；升级后按新基座把文档运行时版本再次统一（3.11 → 3.13），并复核依赖 wheel 可用性 | 两个 `Dockerfile`、`README.md`、`AGENTS.md`、`tech-stack.md` | 命令 6 + CI `docker-build` job | W1-5 | 中：需可用 Docker 回归构建与运行；**升级完成前不得把文档写成 3.13** | M |
| W1-8 | **（2026-10-02 新增）** 依赖版本陈旧治理：对已固定版本做「是否已落后于上游安全修复」的核对，升级需附**上游发布依据 + 全量套件回归**；本轮已完成 `python-jose` 3.3.0 → 3.5.0，并把测试客户端换成 `httpx2` 以清零告警 | `backend/requirements*.txt`、`memory-bank/security-review.md` | 命令 2 + 全量 pytest | W1-4 | 中：升级须有回归证据；**网络不可用时不得声称审计已跑完** | M |
| W1-9 | **（2026-10-02 范围收窄）** 前端容器非 root：`frontend/Dockerfile` 增 `USER appuser` + `frontend/nginx.conf` 监听非特权端口（如 8080）+ 联动 `docker-compose.yml` 与 `DEPLOY.md §二` 的上游端口描述。**后端无需改动**——`entrypoint.sh` 已 `exec gosu appuser` 降权（本轮核实）。**需 Docker 方可验收** | `frontend/Dockerfile`、`frontend/nginx.conf`、`docker-compose.yml`、`DEPLOY.md` | 命令 4（镜像构建）+ 容器内 `id` | Docker 守护进程 | 中：端口联动会影响边缘反代 upstream，必须构建验证 | M |
| W1-10 | **改用 `bcrypt` 直连、移除未维护的 `passlib`**（并解除 `bcrypt==4.0.1` 钉死）：`passlib` 自 2020 年无发布，且被 bcrypt ≥4.1 破坏；改造点 `core/security.py` / `services/auth_service.py`；**必须附哈希向后兼容测试**（passlib `$2b$` 既有哈希须能用 `bcrypt.checkpw` 校验） | `backend/app/core/security.py`、`backend/app/services/auth_service.py`、`backend/requirements.txt` | 全量 pytest + 兼容性用例 | W1-8 | 中：触及认证代码，先有兼容性用例 | M |
| W1-11 | **补 `image_export` 覆盖**（F-56）：对 `draw_members_png` 断言输出为合法 PNG、尺寸随人数与职业区块线性变化（高度按模块常量独立重算）、空列表不抛异常、正式/替补/副职业分支可跑、人数上限守卫抛 `ValueError` | `backend/tests/` | 全量 pytest | W1-8 | 低；恰好 800 人的成功路径不在覆盖内 | S |
| W1-12 | **口令字节边界与 bcrypt 5.0 决策**（F-57）：①决定修法——策略按**字节**收紧，或先 SHA-256 预哈希并为哈希加版本前缀（为将来迁移 Argon2 铺路）；②评估 bcrypt `5.0.0` 对 >72 字节的行为（可能改为报错），与①**同批**实施 | `backend/app/core/password_policy.py`、`backend/app/core/security.py`、`backend/tests/` | 全量 pytest + 边界用例 | W1-10 | 中：涉及口令语义与潜在迁移 | M |
| W1-13 | **前端工具链跨大版本升级**（F-59）：`vite` 5→6/7、`@vitejs/plugin-vue` 5→6、`esbuild` ≥0.25、`vitest` ≥4；须附上游发布依据 + 前端 build/test/lint 与后端全量回归证据 | `frontend/package.json`、`frontend/package-lock.json`、`frontend/vite.config.ts` | `npm run build` + `npm run test` + `npm run lint` + 后端 pytest | W1-8 | 中：跨大版本牵动构建/插件/测试链 | M |
| W1-14 | **默认口令与首次登录强制改密**（F-61）：决定默认口令策略——改为随机生成 / 换用不在黑名单中的占位值，并评估「首次登录强制改密」的实现（需接口与前端配合） | `.env.example`、`README.md`、`DEPLOY.md`、`backend/app/init_db.py`、前端改密入口 | 全量 pytest + 前端 build/test | W0-1 | 中：使用者可见的行为变更 | M |

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
| W2-9 | 整改计划**结构一致性门禁**：校验 §4/§5/§7 的编号唯一性、任务↔进度**一一对应**、行内 `F-xx` 引用有定义、§7 行状态词合法（本轮真实事故：给 §5 加了任务却漏加 §7 进度行，直到记录脚本锚点报错才发现） | `scripts/check_plan_integrity.py`、`.github/workflows/ci.yml` | 门禁自检 + 实跑 | W2-2 | 低 | S |
| W2-10 | 陈旧绝对路径检查**落地为本地可跑门禁**：原实现只写在 CI YAML（bash `grep -F`），本地无法执行，本轮手搓临时检查时模式串用成「旧前缀」而非 CI 实际拦截的「旧前缀 + 仓库名」完整形式，产生 9 处假阳性 | `scripts/check_stale_paths.py`、`.github/workflows/ci.yml`、本计划 §8 | 门禁自检 + 实跑 | W2-9 | 低 | S |
| W2-11 | **文档数字/版本一致性门禁**（AGENTS §3.3 第 5 条的固化）：校验「N 张表」「N 个 Alembic 迁移」「database-design vX.Y」三类声明——真值取自**代码**（`models/__tablename__` 计数、`alembic/versions` 文件数、该文档自身版本），并要求所有当前态声明彼此一致；历史更新记录行（日期开头）不参与判定 | `scripts/check_doc_numbers.py`、`.github/workflows/ci.yml`、本计划 §8 | 门禁自检 + 实跑 | W2-10 | 低 | S |
| W2-12 | **部署文档环境变量覆盖门禁**：现有 `check_env_docs.py` 只校验「代码读取的变量都在 `.env.example`」，未校验运维实际照做的 `DEPLOY.md`——本轮实测其 §六 表格漏了多个键 | `scripts/check_env_docs.py`、`DEPLOY.md §六`、`.github/workflows/ci.yml` | 门禁自检 + 实跑 | W2-11 | 低 | S |
| W2-13 | **把构建产物移出版本库**（F-60）：`git rm --cached frontend/tsconfig.node.tsbuildinfo` 后提交；属 git 删除操作，需用户授权 | `frontend/tsconfig.node.tsbuildinfo` | `git status` 确认不再跟踪 + 7 道门禁 | W2-8 | 低：仅索引清理，不动磁盘文件 | S |
| W2-14 | **lint/format/类型检查收紧**（F-67：W2-3 完成说明里的「待收紧」一直未登记为任务）：①前端 `eslint.config.js` 引入 vue `flat/recommended` 排版规则并跑 Prettier 一次性格式化；②后端 `ruff.toml` 启用 `I`/`UP`/`B` 与 `E501` 行长、`ruff format`；③评估引入 `mypy`（F-29 的剩余部分，W2-3 明确「mypy 除外」） | `frontend/eslint.config.js`、`frontend/.prettierrc.json`、`backend/ruff.toml`、`backend/requirements-dev.txt`、全仓源码格式化 | 全量 pytest + 前端 lint/test/build + 7 道门禁；格式化为**独立提交**（勿与逻辑改动混合） | W2-3 | 中：一次性格式化会产生大 diff，需要单独评审 | M |
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
| W4-5 | 收紧安全响应头：CSP 改为外部脚本 + nonce/hash（先评估 Element Plus 与内联脚本依赖），`X-XSS-Protection` 置 `0` 或移除 | `frontend/nginx.conf.example`、`frontend/index.html`、`frontend/vite.config.ts` | 命令 7 + 浏览器验收 | W4-2 | 中：CSP 收紧可能误伤前端功能，需逐页验收 | M |
| W4-6 | 告警通道：异常/错误率阈值触发通知（webhook 或邮件），或在日志界面增加阈值提示 | `backend/app/services/log_service.py`、`DEPLOY.md` | 命令 7 | — | 低：先仅记录不阻断 | M |
| W4-7 | 威胁建模留痕：按 STRIDE 对关键资产（JWT/账号体系/帮会隔离/文件上传）建模并归档 | `memory-bank/security-review.md`、`backend/docs/README.md` | 命令 3 | — | 低 | M |
| W4-9 | **（2026-10-02 新增，来自 ASVS 条目级核对）** 审计与日志加固：①审计中间件扩展覆盖 401/403（含读方法），避免「越权尝试无痕」；②审计详情与日志值做换行/控制字符转义（防日志注入）；两项均可本地验证 | `app/main.py`、`app/services/log_service.py`、`backend/tests/**` | 命令 2 + 全量 pytest | W4-2 | 低 | S |
| W4-10 | **（2026-10-02 新增，来自 ASVS V6 域核对）** 认证加固：①口令强度下限（≥8，建议 15）+ 上下文词表/弱口令拦截（F-52）；②新增用户自助改密（校验当前口令）并收紧管理端重置语义（F-53）；均可本地验证（Pydantic 校验 + 服务层用例） | `app/schemas/**`、`app/services/account_service.py`、`app/api/v1/accounts.py`、`backend/tests/**` | 命令 2 + 全量 pytest | W2-2 | 中：改校验会影响既有账号创建路径，需回归 | M |
| W4-8 | ASVS 5.0.0 条目级核对：按官方 CSV/JSON 逐条标注结论（`v5.0.0-x.y.z`），先覆盖配置/认证/会话/访问控制/日志五个域 | `memory-bank/security-review.md` | 命令 3 | W4-2 | 低 | L |
| W4-11 | 自助改密的**前端入口**（W4-10 的收尾）：头部用户菜单新增「修改密码」+ 对话框组件；**校验闸门用纯函数**（`utils/passwordForm.ts`）而非 `el-form.validate()`；改密成功后清本地凭证并回登录页 | `frontend/src/components/account/**`、`frontend/src/utils/passwordForm.ts`、`frontend/src/layouts/AppHeader.vue`、`frontend/src/api/{auth,http}.ts`、`frontend/vitest.config.ts`、`frontend/package.json`（新增 devDependency `@vue/test-utils`，`jsdom` 原本已在） | 命令 3（类型检查 + 构建）+ `npm run test` | W4-10 | 中：**无浏览器即无页面验收**，不得声称已验证交互 | M |
| W4-12 | **规范复核（AGENTS §3.3 第 5 条「grep 旧值」）**：修复 F-54 前后端口径分叉——帮会面板改用 `utils/passwordForm` 的共用谓词（只校验长度、不限制组成）；同步修正 `GuildCreate` 两个字段描述；补历史决策行的修订说明；并把 5 道本地门禁命令、`@vue/test-utils`、自助改密功能登记到对应权威源 | `frontend/src/views/config/ConfigGuildPanel.vue`、`frontend/src/utils/passwordForm.ts`、`backend/app/schemas/config.py`、`CONTRIBUTING.md`、`memory-bank/{security-review,tech-stack,design-document-v2}.md`、`frontend/docs/README.md`、`backend/docs/README.md` | 命令 3 + 命令 6 + 5 道门禁 | W4-11 | 低 | S |
| W4-13 | **容器与拓扑声明核实**（只读复核）：`frontend/nginx.conf`（内层）与 `frontend/nginx.conf.example`（边缘模板）职责是否重复、compose 声明与 `DEPLOY.md §二` 是否矛盾、`.gitignore` 对 `nginx.conf` 的处理 | `frontend/Dockerfile`、`backend/{Dockerfile,entrypoint.sh}`、`docker-compose.yml`、`DEPLOY.md`、`.gitignore` | 只读核对 + 门禁复跑 | W1-9 | 低 | S |
| W4-14 | **威胁模型与部署声明逐条复核**：用代码核对 `security-review.md §十六`（STRIDE）的「现有控制」数字与 `DEPLOY.md §二` 关于内层 Nginx 的四项声明；发现过时即改 | `memory-bank/security-review.md`、`frontend/nginx.conf`、`backend/app/utils/{image_export,excel_import}.py`、`backend/app/schemas/recording.py` | 只读核对 + 门禁复跑 | W4-13 | 低 | S |
| W4-15 | **ASVS 判定行抽样复核**：`§17.1~§17.8` 的结论是本会话最早产出的一批（错误率最高），抽样核对「引用 F 编号 / 写「未做」」的判定行，发现修复漂移即更正 | `memory-bank/security-review.md` | 只读核对 + 门禁复跑 | W4-14 | 中：抽样而非全量，未抽到的行仍可能有漂移 | M |
| W4-16 | **「已修复但判定未更新」检查**：从计划 §4 取已修复的 `F-<n>`，扫描 `security-review.md §17` 判定行，判定非 ✅ 却引用已修复编号即报告；计划行可用「（残留判定：…）」显式豁免未做部分 | `scripts/check_verdict_sync.py`、`.github/workflows/ci.yml`、本计划 §8 | 门禁自检 + 严格模式 | W4-15 | 低 | S |
| W4-17 | **抽样复核 `§17.6~17.8`（V6 认证 / V7 会话 / V9 令牌，共 73 条；此前一条未抽）**；并给判定检查器补**反向方向**：判定行自称「已修复」而计划未标修复时报矛盾 | `memory-bank/security-review.md`、`scripts/check_verdict_sync.py` | 关键词筛选 + 代码核对 + 门禁自检/严格模式 | W4-16 | 低（抽样，非全量） | S |
| W4-18 | **关键秘密清单与轮换手册**（对应 ASVS 13.1.4 / 13.3.4）：在 `DEPLOY.md §六` 成文秘密清单（存放位置/访问边界/泄漏影响 + 「不入库」验证命令）与轮换处置；并修 F-55（`frontend/.dockerignore` 补 `.env*`、`.gitignore` 补 `.env.development` 并显式保留 `.env.example`） | `DEPLOY.md`、`frontend/.dockerignore`、`.gitignore`、`memory-bank/security-review.md` | 只读核对 + 门禁复跑 | W4-17 | 低；轮换步骤未在真实服务器演练 | S |
| W4-19 | **成文三份「清单型」控制**（对应 ASVS 13.1.1 / 16.1.1 / 16.3.3）：通信需求清单（含用户外链与「服务端不抓取」的检索证据）、逐层日志清单（五层各自的载体/格式/留存/检索）、安全事件清单（11 类事件 +检测自动化状态 + 改进优先级） | `memory-bank/security-review.md §15.5/§十八`、`DEPLOY.md §四` | 门禁复跑 + 只读核对 | W4-18 | 低 | S |
| W4-20 | **CSP `connect-src` 收窄**：`frontend/nginx.conf.example` 由 `connect-src 'self' https:` → `'self'`，移除「XSS 后可向任意 HTTPS 主机外泄」的能力；依据是「前端无任何跨域 XHR/fetch/WS」的可验证事实 | `frontend/nginx.conf.example`、`memory-bank/security-review.md` | 只读核对 + 门禁复跑（响应头级需服务器/浏览器验收） | W4-19 | 低-中：**边缘模板不参与本地构建**，无法在本机验证响应头 | S |
| W4-21 | **内层 nginx 静态资源扩展名白名单**（ASVS 13.4.7）：`/assets/` 只服务构建产物实测存在的类型（js/mjs/css/map/图片/字体），非白名单一律 404 | `frontend/nginx.conf`、`memory-bank/security-review.md` | 只读核对 + 门禁复跑（**nginx 语法/行为需容器或服务器侧确认**） | W4-20 | 低 | S |
| W4-22 | **文档引用的「存活核对」**（新增检查，**仅报告不设门禁**）：抽取文档中反引号内的文件引用（含 `:行号`），核对存在性与行号越界 | `scripts/check_doc_refs.py` | `--self-test` + 人工复核分类 | W4-20 | **高误报**：被引用对象可能是故意不存在项（见下方结论）| S |

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
| W0-9 环境变量文档联动 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_env_docs.py`（含 11 条内置自检）：扫描 `backend/app/**/*.py` 的 `os.getenv("KEY")` 与 `.env.example` 的条目（`KEY=` 或注释 `# KEY=`），**代码会读但未文档化的变量即失败**；反向（文档有、代码未用）只提示。**实跑发现并修复 7 个缺口**：`DEBUG`、`DATABASE_URL`、`LOG_RETENTION_DAYS`、`DEVELOPER_USERNAME`、`ADMIN_USERNAME`、`MEMBER_USERNAME`、`DEFAULT_GUILD_NAME`（此前部署者只能读源码才知道这些键）——已按「运行时」与「首次初始化账号」两组补入 `.env.example`；门禁接入 CI `repo-hygiene` job（自检 + 实跑）。自检同时暴露并修正门禁自身一个问题：整行注释里的 `os.getenv` 会被误统计（现按第一个 `#` 截断） | chore(config): 补全环境变量文档并新增联动门禁 |
| W1-1 nginx.conf 入库 | ✅ 已完成 | 2026-10-02 | `frontend/nginx.conf`（49 行，占位符版）入库；`.gitignore` 解除忽略（`git check-ignore` 未命中）；`nginx.conf.example` 收窄为边缘层模板（171→109 行）；两个 Dockerfile 的每个 `COPY` **上下文源**逐个核对存在（`COPY --from=build` 为多阶段来源，非上下文路径）。**未执行**：镜像实构建——本机 Docker 守护进程未运行（见下方备注） | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W1-2 deploy.sh.example | ✅ 已完成 | 2026-10-02 | 新增 `deploy.sh.example`（92 行）：占位符 + 路径锚定排除清单（含 2026-09-07 教训注释）+ `healthy` 轮询 + 域名入口 200 校验 + 失败非零退出并打印日志；`bash -n`（Git for Windows bash）**exit 0**；`DEPLOY.md §三` 补复制步骤与 nginx.conf 入库说明 | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W1-3 配置漂移治理 | ⏳ 待开始 | | 依赖决策 D-5（生产配置可否去敏入库）；未确认时按计划退化为 `scripts/check-config-drift.sh` diff 告警 | — |
| W1-4 依赖锁定 | 🔄 进行中 | 2026-10-02（范围约束与门禁部分） | **已完成**：`fastapi>=0.115.0` → `==0.142.2`、`python-multipart>=0.0.18` → `==0.0.32`，并显式锁定传递引入的 `starlette==1.7.0`（均为**已实测通过**的组合：pytest 93 用例 + 6 个既有 selfcheck；3.11 兼容性依据 PyPI 元数据 `requires_python >=3.10`，三包均实取）；新增门禁 `scripts/check_requirements_pins.py`（12 条自检、注释内的范围符号不误报、支持 `# range-ok:` 豁免），接入 CI `repo-hygiene` job；`tech-stack.md` 依赖清单表述同步修正。**待完成**：`pip-compile --generate-hashes` 生成的**哈希锁文件**必须在 **3.11** 环境生成（本机仅 3.12/3.14/2.7，在 3.12 生成会锁到错误 wheel，故刻意未生成）；建议用 CI 的 3.11 步骤或 `docker run --rm python:3.11 …` | chore(deps): 锁定依赖范围并接入门禁，按现状统一 Python 版本表述 |
| W1-5 基础镜像升级 + 文档版本统一 | 🔄 进行中 | 2026-10-02（文档部分） | **文档部分已完成（按现状统一）**：8 处「Python 3.13」按**代码事实**改为 3.11——`AGENTS.md §1`、`README.md`（技术栈行 + 版本说明段）、`backend/docs/README.md`、`memory-bank/ai-context.md`、`memory-bank/tech-stack.md` ×4。**口径调整（如实记录）**：本任务原文要求「先把基础镜像升到 `python:3.13-slim` 再统一文档」，但本机 Docker 守护进程不可用、无法构建验证；按 `AGENTS.md §3.2`（文档与代码不一致时**以代码为准**）先把文档改为现状 3.11，镜像升级拆分为 **W1-7**——既不长期保留未落地的目标值，也不用文档掩盖「镜像仍是 3.11」的事实 | chore(deps): 锁定依赖范围并接入门禁，按现状统一 Python 版本表述 |
| W1-6 README 引导补全 | ✅ 已完成 | 2026-10-02 | README 新增「数据源模式（`DB_MODE`）」小节（prod 快照 / dev 本地库、缺失回退、`.db` 不入库）与 Docker 部署段的 `nginx.conf` 构建前置说明 | fix(build): 入库 nginx.conf 与部署脚本模板 |
| W1-7 基础镜像升级（拆分自 W1-5） | ⏳ 待开始 | | 需要可用的 Docker 守护进程做镜像构建与运行验证（本机不可用）；**升级完成前文档保持 3.11**（与当前镜像一致，禁止先改文档） | — |
| W1-8 依赖版本陈旧治理 | ✅ 已完成 | 2026-10-03 | ①**已升级并附依据**：`python-jose` 3.3.0→3.5.0、`httpx`→`httpx2`、`Pillow` 11.1.0→**12.3.0**、移除 `passlib` 且 `bcrypt` 4.0.1→**4.3.0**（各项均见 §14.7 与提交记录）。②**本轮完成全量公告核对**（GitHub Advisory API `affects=<包>`，逐包与本地实际版本程序化比对）：**后端 12 个固定依赖受影响 0 条** ✓——其中 Pillow 有 **78 条历史公告而每条修复版都 ≤ 12.3.0** ✓、`starlette` 13 条最新上限 `< 1.3.1` ✓、`python-jose` 的 critical 修复于 3.4.0 ✓、`python-multipart` 9 条全部 ≤0.0.31 ✓。③**前端 19 个包**：运行期依赖 0 条受影响 ✓；开发期工具链 **6 条**（vite/esbuild/vitest）均为 **dev-only** ✓，且 `vite.config.ts` **未设 `host`** → 默认仅绑 localhost ✓（配置级缓解证据）→ 登记 **F-59 / W1-13** 规划跨大版本升级。④**方法边界**：未查询成功的包不算已核对（本轮 12+19 个包全部查询成功）| docs(deps): 完成全量依赖公告核对并登记前端工具链升级计划 |
| W1-9 容器非 root（范围收窄为前端） | ⏳ 待开始（**需 Docker**） | | **已核实**：后端 `backend/entrypoint.sh` 用 `exec gosu appuser "$@"` 降权并 chown 卷目录 → **后端已满足**；前端 `frontend/Dockerfile` 建了 `appuser` 且 chown 了 html/cache/log/pid，却**没有 `USER`** → nginx 以 root 运行。改动需同时改监听端口（`listen 80` → 非特权端口）并联动 compose/DEPLOY/边缘 upstream，**本机无 Docker 守护进程，无法构建验证**，故刻意不做（避免提交未验证的基础设施改动） | — |
| W1-10 改用 bcrypt 直连（移除 passlib） | ✅ 已完成 | 2026-10-03 | ①**先证兼容**：实测 passlib 1.7.4 生成的 `$2b$12$…`（60 字符）可被 `bcrypt.checkpw` 校验、错误口令为 False，`bcrypt.gensalt()` 默认同为 `$2b$12$` → **既有库内哈希无需迁移** ✓。②**改代码**：`app/core/security.py` 去掉 `CryptContext`，改用 `bcrypt.hashpw/checkpw`。③**测试先行**：新增 `tests/test_password_hash_compat.py`（5 用例，含 passlib **真实历史哈希**看护「老用户仍能登录」）。④**用例当场抓到真实缺陷（F-58）**：`bcrypt` 4.x 对截断哈希 `pyo3_runtime.PanicException` 穿透原 `except (ValueError, TypeError)` ✗——实测 MRO `PanicException → BaseException → object`、`isinstance(e, Exception)` **False**；passlib 时代返回 False → **本次改动会引入的回归** ✗（生产中=登录 500）。⑤**修法**：格式预校验 + 宽捕获，显式重抛 `KeyboardInterrupt`/`SystemExit`。⑥**依赖**：移除 `passlib[bcrypt]==1.7.4`、`bcrypt==4.0.1` → **`4.3.0`**（同族最新 4.x；**有意不取 5.0.0**，见 W1-12）；`tech-stack.md` 同步。⑦**易漏点**：`test_core_security.py` 的模块级跳过守卫原本 import passlib → 不同步改会**整模块静默跳过** ✗（已改 bcrypt）。⑧**环境踩坑**：pip 仍挂起 → 「清华源取 wheel → 下载 → `--no-index --no-deps` 离线装」；首次选错 wheel（`cp313-cp313t` 自由线程 ✗，应为 `cp38-abi3` ✓），安装失败但环境无损 ✓。⑨**证据**：bcrypt **4.0.1 与 4.3.0 两个版本下**兼容性用例 5 passed、全量 pytest **169 passed + 89 subtests exit 0**、`ruff` 通过。⑩登记 F-57/F-58 与 W1-12 | fix(auth): 移除未维护的 passlib 改用 bcrypt 直连并修复非法哈希 panic |
| W1-11 补 image_export 覆盖（F-56） | ✅ 已完成 | 2026-10-03 | 新增 `backend/tests/test_image_export.py`（**6 用例**，0.30s 全过）：PNG 合法性（魔数 + `Image.open` 的 format/size）｜宽度恒为 `WIDTH`｜**高度按实现公式独立重算**（引用模块常量）｜同职业 1 人 vs 5 人差恰为 `CELL_H`｜多职业区块差恰为 `SECTION_TITLE_H + CELL_H + SECTION_GAP`｜**空列表不抛异常**（0 人时公式含 `(groups-1)*SECTION_GAP` 负项）｜正式/替补/副职业分支｜人数上限守卫抛 `ValueError` 且消息含上限数字。**不断言字形**（`_load_font` 有 Linux wqy → Windows 雅黑 → glob → `load_default` 回退链，CI 无中文字体也能过）。**覆盖边界（有意）**：恰好 800 人成功路径未执行（约 26MB 位图）。**证据**：`ruff` 通过；全量 pytest **158 → 164 passed**（+6）、84 subtests、exit 0 | test(backend): 补 image_export 的 PNG 导出回归用例并收口 F-56 |
| W1-12 口令字节边界与 bcrypt 5.0 决策（F-57） | ✅ 已完成 | 2026-10-03 | ①**先实测再决策，结果推翻了我的初步方案**：原计划「把策略按 72 字节收紧」——实测 72 字节对中文仅 **24 个字符**，会**违反 ASVS 6.2.9**（须允许 ≥64 字符）✗，故**放弃收紧**。②**实测 bcrypt 5.0.0**：对 >72 字节 `hashpw`/`checkpw` **均报 ValueError** ✗ → 此刻升级会**锁死**库内既有超长口令用户 → **不升级**（记录在 `requirements.txt` 与 §14.7）。③**落地 OWASP 标准做法**：新哈希先 `base64(SHA-256(口令))`（44 字符 < 72 字节）再 bcrypt，哈希形如 `sha256$<bcrypt>`；`verify_password` 按前缀分派，**旧哈希（无前缀）仍走直连** → 既有用户不受影响。④**惰性升级**：`auth_service.authenticate` 在登录成功后，若哈希仍为旧方案则用新方案重写（用户无感，库内逐步迁移；迁移完成后才可安全评估 5.0.0）。⑤**测试**：兼容性用例扩展为「新方案带前缀且校验 ✓ / **两个前 72 字节相同的口令互不通过** ✓（F-57 回归看护）/ 中文 300 字节口令完整可用 ✓ / 旧哈希仍截断（特征化旧行为 ✓）」；新增 `tests/test_password_hash_migration.py`（3 用例：旧哈希登录后被升级且仍可校验 ✓ / 已是新方案则不重写 ✓ / 登录失败不改动哈希 ✓）。⑥**过程缺陷（如实记录）**：新迁移用例引入 `F841`（未使用变量）✗，而 `ruff check` 的最后一行是「No fixes available (1 hidden fix…)」——**这不是通过** ✗，我一度按「取最后一行」当结果，差点漏判；已修并把断言具体化（`AuthError` 而非 `Exception`）。⑦**证据**：`ruff` All checks passed；全量 pytest **174 passed + 89 subtests exit 0**（169 → 174：兼容性用例净 +2、迁移用例 +3）| fix(auth): 口令预哈希修复 72 字节截断并支持旧哈希惰性升级 |
| W1-13 前端工具链跨大版本升级（F-59） | ✅ 已完成 | 2026-10-03 | ①**先探源**：本机 `registry.npmjs.org` **超时**，`registry.npmmirror.com` 可达 → 按命令传 `--registry` 完成安装（不改全局配置、不把镜像写进仓库）。②**选最小修复版本**（非最新大版本）：`vite` 5.4.21 → **6.4.3**（3 条 vite 公告的修复版即 6.4.2/6.4.3，且其依赖 `esbuild ^0.25.0`）、`vitest` 3.2.7 → **4.1.11**（该公告的修复版）、`@vitejs/plugin-vue` 5.2.4 的 peer 为 `^5.0.0 || ^6.0.0` → **无需升级** ✓。③**一次只动一个变量 + 先备份**：先升 vite（含 esbuild 被动升到 0.25.12）并全量复跑，再单独升 vitest；每步都有回滚备份。④**实际版本以 `npm ls` 为准**：`vite@6.4.3`、`esbuild@0.25.12`、`vitest@4.1.11` ✓。⑤**升级后复核公告**（同一 API 再查）：vite/vitest/vue/axios/element-plus/echarts/plugin-vue **均 0 条** ✓；仅 `esbuild 0.25.12` 仍被列出 1 条 → 经 API 的 **`withdrawn_at` 字段实证上游已撤回** ✓（非风险；消除它需 vite 7 + esbuild 0.28，收益不足）。⑥**回归证据**：`npm run build` exit 0、`npm run test` **60 passed / 7 文件 exit 0**、`npm run lint` **0 error**（10 既有 warning）。⑦**环境记录（与 pip 同类）**：npm 上游 registry 本机不可达、镜像可达；npm 11 另有 `allow-scripts` 警告（esbuild postinstall 未执行）——因 esbuild 二进制经可选依赖分发，构建与测试均正常 ✓，故不阻断。⑧`CONTRIBUTING.md` 环境准备补充「换源」指引 | fix(deps): 前端工具链升级至 vite 6.4.3 / vitest 4.1.11 并清除 6 条公告 |
| W1-14 默认口令与首次登录强制改密（F-61） | ⏳ 待开始（**待决策**） | — | **登记原因**：默认 `admin123` 在应用自身弱口令黑名单内；改法（随机生成 / 换占位值 / 强制首登改密）会改变使用者可见行为，需用户决策后实施 | — |
| W2-1 CI 工作流 | ✅ 已完成 | 2026-10-02 | `.github/workflows/ci.yml`：4 个 job（backend 编译+迁移+导入 / frontend `npm ci`+`vue-tsc`+`vite` / repo-hygiene 行数+陈旧路径+换行 / docker-build 双镜像＝F-08 回归护栏）。**本机前置验证**：`npm ci` exit 0、`vue-tsc` 无类型错误、`vite build` 成功（12.27s）、`compileall` exit 0。**CI 本身未运行**（本会话无 GitHub Actions 环境），需 push 后观察首次结果 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-2 测试体系（pytest/Vitest） | ✅ 已完成（**含 `selfcheck_indicators` 改造，2026-10-02 收尾**） | 2026-10-02 | **后端**：`backend/pytest.ini`（`python_files` 同时匹配即收集 6 个既有 selfcheck）+ `backend/tests/`（4 模块：安全工具 / 弱密钥门禁 / 权限矩阵 / 姓名规范化）+ CI `python -m pytest` → **78 passed + 57 subtests（24.23s）**。**前端**：`frontend/vitest.config.ts` + 4 个 spec（constants / profession / scheduleSort / analysis，共 **38 用例**）+ `package.json` test/test:watch + CI `npm run test` → **38 passed（1.73s）**；**vitest 须用 3.x**（5.x peer 要求 vite ≥6.4，与项目 vite 5.4 冲突，实测 npm ERESOLVE）。**待办**：`selfcheck_indicators.py` 由模块级断言脚本改造为用例类；组件级/接口级用例（httpx 已装待用） | ci(test): 补齐前端 Vitest 测试体系 | **收尾（2026-10-02）**：`scripts/selfcheck_indicators.py` 由模块级断言脚本改造为 3 个用例类（8 用例），`pytest.ini` 移除 `--ignore=scripts/selfcheck_indicators.py`；同时**首次真正执行全套件**（Python 3.12 + 锁定依赖）时发现并修复 `tests/test_alerting_service.py` 的缺陷——同步 `setUp()` 早于 `DbTestCase.asyncSetUp()`，`self.engine` 尚不存在 → 改为 `asyncSetUp()` + `await super()`。**完整基线：124 passed + 72 subtests，exit 0** **接口级补齐（2026-10-02）**：新增 `backend/tests/test_api_endpoints.py`（10 用例 / 2 subtests，经 TestClient 打完整链路）——登录成功与失败、登录失败锁定（含**锁定后正确密码仍被拒**与 `data.remaining_seconds`）、未知账号内存锁定、缺/坏令牌、**令牌版本吊销**、角色越权 403（member→admin/developer、admin→developer）、CORS 预检（允许 dev 来源/拒绝未知来源）、`/health`；**完整基线更新为 134 passed + 74 subtests，exit 0，0 warnings** |
| W2-3 lint/format/类型检查 | ✅ 已完成（mypy 除外） | 2026-10-02 | **后端 ruff**：`backend/ruff.toml`（E4/E7/E9/F，迁移与 3 个一次性脚本按文件豁免）+ `ruff==0.12.0` + CI 接线；基线 52 → 修复 9 项 → **All checks passed!**。**前端 ESLint/Prettier**：`frontend/eslint.config.js`（vue `flat/essential` + typescript-eslint + skipFormatting；**刻意不用 `flat/recommended`**，避免数百条排版告警）+ `.prettierrc.json` + 5 个 devDependencies + `package.json` 脚本 + CI 接线；基线 14 errors → 修复 4 处 `any`（导出 `SlotDragEvent` 最小结构类型）→ **0 error / 10 warning**；`npm run build`（vue-tsc）exit 0 证明类型改动安全。**未做**：mypy；`E501`/`I`/`UP`/`B`、vue 排版规则与 Prettier 一次性格式化（均需独立大改提交） | ci(lint): 接入前端 ESLint 与 Prettier 配置 |
| W2-4 pre-commit 与提交校验 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_commit_msg.py`（内置 15 条用例自检 **exit 0**；支持消息文件 / `--stdin`；BOM 容错）、`.githooks/commit-msg`（正例 exit 0、反例 exit 1）、`scripts/install_git_hooks.sh`（`bash -n` 通过）、`.github/commit-msg-baseline` 与 CI `commit-msg` job（范围校验 10 个提交 **违规 0**，注入两个反例均 exit 1）；规则文档补 `merge` 类型与「自动校验」小节。**偏离说明**：未引入 pre-commit 框架，改用零依赖的 `core.hooksPath` + 版本化钩子（ruff / 行数门禁已在 CI 中强制） | ci(commit): 提交消息校验与版本化钩子 |
| W2-5 行数规则补全与检查脚本 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_file_length.py`（标记+登记双重校验、清单悬空、增长 ≥20% 提醒）与规则文档「前端 TS」类别；本地实检 211 文件 / 14 条登记 **exit 0**。**偏差记录**：计划原拟 TS 上限 200，实施改为 **300**（composable 与组件同为状态控制器；若设 200，`analysis.ts` 295、`useAttendanceList.ts` 240、`useRecordingList.ts` 223 会在新门禁上线首日即失败，违背「门禁不得先红」原则），已在规则文档写明理由 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-6 出勤率口径收敛 + config 副作用 | ✅ 已完成 | 2026-10-02 | ①**口径收敛（批次 7）**：新增 `frontend/src/utils/attendance.ts` 单一来源（阈值常量 / 低出勤判定 / 进度条颜色 / 百分比格式化 `digits` 参数），收敛 7 处硬编码（阈值 4 + 格式化 3）与组件内本地 `ratePercent()`；两种展示口径作为显式参数保留。②**F-04 修复（批次 8）**：弱密钥门禁由 `config.py` **导入期**移至**应用启动期**——新增 `InsecureSecretKeyError`、`FATAL_SECRET_KEY_MESSAGE`（**原文逐字保留**）、`WEAK_SECRET_KEY_WARNING`、`validate_secret_key()`（抛异常、可断言）、`enforce_secret_key()`（打印 FATAL + 退出码 1），移除模块级调用；`main.py` 新增 `startup_checks()` 并在 `on_startup` 首要位置调用（alembic 与 CI 导入步骤不再继承退出行为）。目录创建刻意保留在导入期（幂等、被 logging/SQLite 路径依赖，理由见 `config.py` 末尾）。实测：`ruff check .` **All checks passed!**、`compileall` exit 0、`pytest tests/test_config_gate.py` **15 passed + 2 skipped**（跳过项需 FastAPI，CI 执行），子进程回归证明「仅导入 config → exit 0 无 FATAL」「调用门禁 → 非零退出 + FATAL」。**语义保持**：文案逐字不变、拒绝启动不变；退出码在 uvicorn lifespan 路径由 uvicorn 以「启动失败」收尾（非零），直接调用 `enforce_secret_key()` 恒为 1。另修复 `tests/test_permissions.py` 未使用的 `unittest` 导入（否则 CI ruff 会红） | refactor(core): 弱密钥门禁改为启动期校验并补齐回归 |
| W2-7 Dependabot | ✅ 已完成 | 2026-10-02 | `.github/dependabot.yml`：pip / npm 周更分组各限 5、docker 双目录周更、github-actions 月更；依据 OpenSSF Scorecard 与 OWASP A06 | ci(quality): 新增 CI 门禁与行数检查脚本 |
| W2-8 修复 props 变更债（10 处） | ✅ 已完成 | 2026-10-03 | ①**10 处告警集中在 4 个文件**（`SquadCardsGrid` 1、`MemberTablePanel` 2、`MemberToolbar` 3、`LogFilterBar` 4），模式统一：模板里 `v-model` 直接绑到 **prop 的嵌套字段**（`query.keyword` / `filters.level` / `compareChecked[name]` / `query.page`）。②**改法**：把四处 prop 改为 `defineModel('…', { required: true })`——这是 Vue 3.4+ 对「子组件需要写这份状态」的官方声明方式 ✓；`LogFilterBar` **本来就在用 defineModel**（`dateRange`）→ 与既有写法一致 ✓。③**关键取舍（父组件一行未动）**：`defineModel` 返回 ref，模板中就地写入的是**父组件共享的同一对象**（父组件用 `reactive`，`v-model:x` 反而无法编译）→ 行为与改前**完全一致** ✓，因此不触碰 3 个父组件，把改动面压到最小 **4 个文件** ✓。④**验证（静态与单测）**：`npm run lint` **10 warnings → 0** ✓；`npx vue-tsc -b --force` exit 0 ✓（类型全过）；`npm run build` exit 0 ✓；`npm run test` **60 passed / 7 文件 exit 0** ✓。⑤**诚实边界**：`AGENTS.md §7.4` 未获浏览器授权 → **页面级交互验收未做** ✗（筛选/分页/勾选的视觉效果需人工确认）；另「就地改共享对象」仍是设计层面的折中，若要彻底改为**每次变更 emit 新对象**，属可选后续改进（未单列任务）| fix(frontend): 用 defineModel 消除 10 处 props 变更告警 |
| W2-9 整改计划结构一致性门禁 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_plan_integrity.py`（8 条内置自检）：①编号唯一性（§4 发现 / §5 任务 / §7 进度各自不得重复）；②**任务↔进度一一对应**（§5 有任务必有 §7 行、§7 有行必有 §5 任务）；③行内 `F-xx` 引用必须在 §4 有定义；④§7 行必须含 ✅/🔄/⏳/⛔ 状态标记。已接入 CI `repo-hygiene`（先自检再实跑）。**实战价值已兑现两次**：其一，最初版本正则不认**加粗编号**（计划里 `| **F-08** |`、`| **W2-8** |`），报出「§7 有进度但 §5 无任务：W2-8」——我据此**误给 §5 补了一行**，修好正则后门禁立刻报「§5 任务编号重复：W2-8」（那行本来就有，见 ai-checklist 第 42 条）；其二，修好后实跑即为 PASS（52 发现 / 42 任务 / 42 进度一一对应），并把 §8 回归命令补齐 | ci(quality): 新增整改计划结构一致性门禁 |
| W2-10 陈旧绝对路径门禁脚本化 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_stale_paths.py`（5 条自检，纯标准库，只扫描 git 跟踪文件）：拦截「旧前缀 + 仓库名」的**完整字面量**，约定允许的省略号形式不拦截；CI 的内联 grep 与 §8 组 1 的本地命令**都改为调用该脚本**，使本地与 CI 口径完全一致。**动机**：该检查原先只在 CI 里，本地跑不了——本轮我手搓临时检查时把模式串写成「旧前缀」，9 处**省略号形式的说明性引用**被误报为违规（复核后确认仓库对 CI 模式 **0 命中**，因此未据此改动任何文档——第二次靠「先验证检测器」避免改错文档）。验证：自检 5/5；实跑扫描 353 个跟踪文件 0 命中 PASS | ci(quality): 陈旧绝对路径检查落地为本地可跑门禁并补验收清点 |
| W2-11 文档数字/版本一致性门禁 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_doc_numbers.py`（8 条自检）：真值取自代码——模型 `__tablename__` 计数、`alembic/versions` 文件数、`database-design.md` 自身版本；校验各文档**当前态**声明（`N 张表`/`N 个 Alembic 迁移`/`database-design vX.Y`）彼此一致且与真值相符，日期开头的更新记录行按 §3.4 排除。**产出两处旧值并修正**：（a）`backend/docs/README.md` 引用 `database-design v1.9`（实际 v1.9）——**人工普查没发现，是门禁上线后抓到的**；（b）`memory-bank/tech-stack.md` 摘要行仍写 `Python 3.13`（同文件正文已按代码事实写 3.11）——人工普查发现，门禁不覆盖（Python 版本声明含「3.11–3.13 可用」等范围写法，机器判定易假阳性，故暂不纳入）。训练要点：**人工 grep 与门禁不是重复劳动**（各抓到一处）。验证：自检 8/8；实跑 PASS（真值 12 表 / 15 迁移 / v1.9，扫描全部当前态行）| ci(quality): 新增文档数字/版本一致性门禁并修正两处旧值 |
| W2-12 部署文档环境变量覆盖门禁 | ✅ 已完成 | 2026-10-02 | 扩展 `check_env_docs.py`：在原有「代码 ↔ `.env.example`」之外，新增「`.env.example` 的每个键必须在 `DEPLOY.md` 出现」——**两份清单缺一不可**（模板是给开发者看的，部署文档是运维照做的）。**实测证据**：用 `git show HEAD:DEPLOY.md` 取修复前内容并用**同一取键函数**比对，修复前有 **7 个键**（ADMIN_USERNAME、DATABASE_URL、DEBUG、DEFAULT_GUILD_NAME、DEVELOPER_USERNAME、LOG_RETENTION_DAYS、MEMBER_USERNAME）在部署文档中未出现；已补入 §六 表格，现为 **17/17 均已提及**。自检由 11 条增至 **14 条**（新增部署文档提及判定样例）。教训记入 ai-checklist 第 50 条（校验了 A↔B 不等于 A↔C 也一致）| ci(quality): 扩展环境变量门禁覆盖部署文档并补全 §六 表格 |
| W2-13 构建产物移出版本库（F-60） | ⏳ 待开始（**待授权**） | — | **登记原因**：`git add -A` 把 `vue-tsc` 产物 `frontend/tsconfig.node.tsbuildinfo` 一并入库；`.gitignore` 已补 `*.tsbuildinfo`，但**已被跟踪的文件不会因忽略而自动移出** ✗；移出索引是 git 删除操作，按 §5 需用户授权 | — |
| W2-14 lint/format/类型检查收紧（F-67） | ⏳ 待开始 | — | **登记原因**：W2-3 的完成说明里写有「待收紧：E501 行长、`ruff format`、`I`/`UP`/`B` 规则、vue `flat/recommended` 排版规则与 Prettier 一次性格式化；后端 mypy 尚未引入」，但**没有对应任务**（F-29 指向的 W2-3 已 ✅ 且明确「mypy 除外」）→ 按台账约定补齐登记 | — |
| W3-1 /health 与探活 | ✅ 已完成 | 2026-10-02 | 新增 `backend/app/api/v1/health.py`：`GET /health`——数据库可查询 → `200 {status:ok,database:ok}`；库不可用 → `503 {status:degraded,database:error}`（**刻意不抛 500**：否则对外表现为「应用崩溃」而非「依赖不可用」）。`docker-compose.yml` 的 healthcheck 由根路径 `http://127.0.0.1:8000/` 改探 `/health`（原方案只能证明进程存活，数据库挂掉仍报健康）；同一端点另挂 `/api/v1/health`，经既有 `/api/*` 反代对外可达，供外部 uptime 探活（不需要时可在边缘 Nginx 拦掉）。`DEPLOY.md §二` 新增「健康检查与在线 API 文档」小节（含 backend 无宿主端口映射时的手动探活命令）。验证：`pytest tests/test_health.py` → **5 passed**（200/503 语义 + 双路径路由可达 + 文档开关子进程断言）；全量 **93 passed + 67 subtests passed（27.90s）**。**待办**：`/version` 端点未加（与 D-4 版本联动耦合）；`app.on_event("startup")` 已被 FastAPI 弃用，迁移 lifespan 列为后续 | feat(ops): 新增健康检查端点并关闭生产 API 文档 |
| W3-2 备份自动化与演练 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/backup-db.sh.example`：把 `DEPLOY.md §五` 的「方式一（SQLite 在线 backup API）」自动化——**默认 dry-run**（`DRY_RUN=1` 只打印命令）、快照先在容器内生成并执行 `PRAGMA integrity_check`（**校验通过才拷出**，避免把坏库当备份）、产物 `nsh-YYYYmmdd-HHMMSS.db` 默认保留 30 天、cron 示例写在脚本头部；`DEPLOY.md §五` 新增「自动化备份」与「恢复演练记录（每季一次）」两小节（含演练要求与模板首行）。**实证设计理由**（本机 Python 3.14 实测）：WAL 模式且连接打开时，直接复制主库文件得到的副本报 `no such table: t`（表结构与数据仍在 `-wal` 中），而 backup API 快照读到 2000 行且 `integrity_check = ok`——该对比已写入 §五，作为「禁止直接 cp」⚠️ 警告的依据。验证：`bash -n` exit 0；dry-run 实跑 exit 0；非法参数路径 non-zero。**未验证**：`DRY_RUN=0` 真实全流程（需 Docker 守护进程与命名卷，本机不可用）；恢复演练本身未执行 | feat(ops): 新增备份与归档脚本模板并补齐回滚章节 |
| W3-3 制品版本化与回滚 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/release-archive.sh.example`：本项目**不使用镜像仓库**，故以带版本号的 tar 归档（`docker save`）+ `nsh-<version>.manifest.txt`（记录版本 / 提交号 / 镜像引用 / 归档时间）。**版本权威为 git 标签**：脚本校验 `vX.Y.Z` 格式、核对标签是否存在、工作区是否干净（不满足时**告警而非静默通过**）。`DEPLOY.md` 新增 **§九 版本归档与回滚**：9.1 发布前归档；9.2 回滚七步（停服 → `docker load` → 打 compose 期望的本地 tag → `up -d` → `ps` 需 healthy → 入口 200）；**9.3 数据库迁移不可逆警示**——容器每次启动执行 `alembic upgrade head` 且只前进不回退，若版本含破坏性迁移则**仅回滚镜像会与库不兼容**，必须先用 W3-2 的备份回退数据库；并把「先归档 + 先备份，再 `up -d --build`」写成发布纪律；9.4 归档保留建议。**实现位置偏差（如实记录）**：计划原文提到改 `deploy.sh.example`，实际另建独立脚本——`deploy.sh` 含服务器专属内容且已被忽略，把归档职责拆开更清晰。验证：`bash -n` exit 0；dry-run 实跑 exit 0 且正确识别标签 `v1.2.0` 与当前提交；非法版本号返回 **2**（双向验证）。**未验证**：真实 `docker save` / `docker load` 全流程（需 Docker 守护进程，本机不可用） | feat(ops): 新增备份与归档脚本模板并补齐回滚章节 |
| W3-4 CHANGELOG 与版本联动 | 🔄 进行中 | 2026-10-02（CHANGELOG 部分） | `CHANGELOG.md` 已建立（Keep a Changelog 1.1.0 + SemVer 2.0.0）：`[未发布]` 段按新增/变更/修复/安全四类汇总本轮合规化改动；`[1.2.0] - 2026-10-02`、`[1.1.0] - 2026-09-16`、`[1.0.0] - 2026-08-27` 三段**依据 `git log <旧标签>..<新标签>` 归并并在文件内标注依据**（不逐条回溯）；比较链接指向真实仓库 URL（`github.com/yyyyyyyy-cco/nsh-management`）；文件内记录 `frontend/package.json` 版本 `0.1.0` 与标签 `v1.x` 不一致（对应 F-16）。**已完成**：`GIT-GUIDE.md §8` 发布检查清单已加入「更新 CHANGELOG」「**发布前**归档制品」「**发布前**做数据库备份」三项（2026-10-02，与 `DEPLOY.md §九` 的发布纪律对齐）。**待办**：按 D-4 落地版本联动（调整 `package.json` 或改为运行时注入） | docs(changelog): 新增更新日志与社区政策文档 |
| W3-5 分支治理 | ⏳ 待开始 | | | |
| W3-6 远端策略落地 | ✅ 已完成 | 2026-10-02 | 按 D-2（「单远端为准 + 可选镜像」）改写 `GIT-GUIDE.md`：§1 文首与仓库概览表（`gitee` 行改为「可选镜像远端」）、§1 策略段（原文「任何推到 main 的提交和 tag 都要同步推送到两个远程」→「`origin` 为唯一权威远端；镜像可选、非发布前置条件」，并给出配置镜像命令）、§4.4、§5.2、§6「镜像远端（可选）」（必做命令与可选命令分列）；历史事实备注按 §3.4 **保留不回改**，仅调整其结论句。同步权威源：`AGENTS.md §5`、`memory-bank/ai-context.md`、`memory-bank/progress.md` 代码树说明。**同时修一处文档与代码矛盾**：`GIT-GUIDE.md §7.1` 原写「禁止提交 `frontend/nginx.conf`」，而该文件自 2026-10-02 起已入库（容器构建输入，占位符版）——已按代码事实更正并补变更说明。事实依据：`git remote -v` 仅有 `origin` | docs(git): 远端策略改为单远端为准并同步发布清单 |
| W4-1 关闭生产 API 文档 | ✅ 已完成 | 2026-10-02 | `core/config.py` 新增 `api_docs_enabled()`（生产 False / 开发 True，复用既有 `_is_production()`）；`app/main.py` 按该开关设置 `docs_url` / `redoc_url` / `openapi_url`（生产为 `None` → 404），本地开发保留。**未采用 `DEBUG` 作判据**：`DEBUG` 控制异常详情脱敏，与「部署环境」语义不同，用 `APP_ENV`/容器特征更贴合本任务原意。验证（子进程断言，因开关在 import 时求值）：`APP_ENV=production|prod` → 三者均 `None`；`development` → `/docs`、`/redoc`、`/openapi.json` 均在。文档同步 `DEPLOY.md §二`。`security-review.md` 的 ASVS/Top10 逐项对照仍由 W4-2 完成 | feat(ops): 新增健康检查端点并关闭生产 API 文档 |
| W4-2 ASVS/Top10 对照补审查 | ✅ 已完成 | 2026-10-02 | `memory-bank/security-review.md` 新增 **§十五 暴露面清单与 OWASP 对照**：①**15.1 暴露面清单**（读配置得出，非推测）：仅边缘 Nginx 443 对外（TLS 1.2/1.3）、:80 仅跳转与 ACME 校验；frontend/backend 容器端口与 SQLite 文件均不对外；路径级处置表含 `/api/v1/auth/login` 独立限流 5r/m、`/api/*` 20r/s、生产 `/docs` 等 404。②**15.2 Top 10:2025 条目级对照**（依据官方 `top10.owasp.org/2025/` 本轮实取清单，含 2025 新增 A03/A10）：A01/A05/A07 已覆盖；A02/A03/A04/A06/A08/A09/A10 部分满足并逐条给出证据与缺口。③**15.3 ASVS 5.0.0 域级对照**（配置/认证/会话/访问控制/日志与错误处理）：ASVS 5.0.0 为当前稳定版、官方编号格式 `v5.0.0-x.y.z`、V1 为 Encoding and Sanitization——三项均本轮实取核实；**条目级未做**（已登记 W4-8）。④**15.4 新识别 6 项不足**（CSP 过宽、无告警通道、供应链完整性、无威胁建模、ASVS 条目级缺口、历史响应头），已登记为差距 F-43~F-46 与任务 W4-5~W4-8。**边界**：结论基于仓库内配置与代码证据，**未做**渗透测试或动态扫描 | docs(security): 补齐暴露面清单与 OWASP 对照 |
| W4-3 CORS 外置与依赖审计 | ✅ 已完成 | 2026-10-02 | ①**CORS 外置**（F-19）：`core/config.py` 新增 `_parse_cors_origins()`（逗号分隔、去空白与空项）与 `CORS_ORIGINS` 环境变量（未设置回退本地开发来源）；`.env.example` 与 `DEPLOY.md §六` 同步说明（生产由 Nginx **同源**反代，通常无需配置；**禁止 `*`**，因 `allow_credentials=True`）。②**依赖审计结论**写入 `memory-bank/security-review.md` §十四——前端 `npm audit`：初始 7 项（4 high）→ 非破坏性修复后 **4 项（1 high）**（`nanoid` high 已消除；lockfile 变更后 lint 0 error / test 44 passed / build exit 0）；剩余 `vite 5.4`(high)、`esbuild`(mod)、`vitest 3`(mod)、`@vitest/mocker`(mod) 均需 semver-major（vite 8 / vitest 5），**可达性判定：全部属开发/构建工具链，生产运行时（Nginx 静态资源 + 同源反代）不受影响**；后端 `pip-audit`：`pillow 11.1.0`（多条 PYSEC）与 `ecdsa 0.19.2`（PYSEC-2026-1325）——**均不可达**（全仓无 `Image.open`，Pillow 只用 `Image.new`/`ImageDraw` 生成图片；`ecdsa` 仅服务 ECDSA 而本项目 `ALGORITHM=HS256`）。③后续项（需回归，本次不升级）：vite8+vitest5 升级通道、Pillow 12.x + 图像导出回归、`python-jose`→`PyJWT` 评估、依赖审计是否接入 CI。验证：`ruff check .` All checks passed（另按 CI pin `ruff==0.12.0` 复核）；`compileall` exit 0；`pytest tests/test_config_gate.py tests/test_member_names.py` 全通过（新增 4 条 CORS 用例，含子进程端到端生效断言） | chore(deps): 外置 CORS 白名单并完成依赖漏洞审计 |
| W4-4 SECURITY/CONTRIBUTING/CoC | ✅ 已完成 | 2026-10-02 | 按 D-1（公开仓库）补齐三份根文档：`SECURITY.md`（支持版本范围 / GitHub 私有安全公告为首选渠道 / 备用邮箱占位符 / 处理时限目标 / 已知接受风险指向 `security-review.md` 权威源）、`CONTRIBUTING.md`（协作约定摘要 + 权威源链接 + 与 `.github/workflows/ci.yml` 对应的本地门禁命令，**未复制**权威源内容）、`CODE_OF_CONDUCT.md`（Contributor Covenant 2.1 官方简体中文译本逐字采用，保留 CC BY-SA 4.0 署名）。验证：三文件与 `CHANGELOG.md` 均入库、互相引用链接有效、`scripts/check_file_length.py` 通过。**未完成**：SECURITY.md 与 CoC 的备用联系邮箱为占位符（需用户提供后填写） | docs(changelog): 新增更新日志与社区政策文档 |
| W4-5 安全响应头收紧（CSP） | ✅ 已完成 | 2026-10-02 | `frontend/nginx.conf.example`（唯一落点）把 CSP 的 `script-src` 由 `'self' 'unsafe-inline' 'unsafe-eval'` 收紧为 **`'self'`**，并补 `object-src 'none'`、`base-uri 'self'`、`form-action 'self'`；`X-XSS-Protection` 由 `1; mode=block` 改为 **`0`**。**依据（构建级证据，非推测）**：①`npm run build` 产出的 `dist/index.html` 内联 `<script>`/`<style>` 计数均为 **0**（仅 1 个外部 module script + 1 个外链 CSS）→ 不需要 `'unsafe-inline'`；源码无 `v-html`/`eval`/`new Function`；②产物中唯一一处 `new Function("return this")` 来自 **core-js 全局对象探测，自带 try/catch 回退到 `window`**，被 CSP 拦截时走回退分支 → 不需要 `'unsafe-eval'`。**保留** `style-src 'unsafe-inline'`（Element Plus/ECharts 运行时注入内联样式，去掉会白屏）。**未验证**：本机无浏览器，**未做页面级验收**；回滚=把两个 token 加回 `script-src` | fix(nginx): 收紧 CSP 并停用 X-XSS-Protection |
| W4-6 告警通道 | ✅ 已完成 | 2026-10-02 | 新增**错误率告警**：`app/core/alerting.py`（纯策略层：`decide_alert` 阈值判定 / `build_payload` 稳定负载契约 / `post_json` 标准库发送，**不引入新依赖**）与 `app/services/alert_service.py`（`count_recent_errors` 窗口统计 + `run_alert_check` 编排 + 进程内去重）；`app/main.py` 启动时挂后台循环（启动即查一次，之后每 `ALERT_CHECK_INTERVAL_MINUTES` 分钟）。**语义选择**：最近 `ALERT_WINDOW_MINUTES`（默认 30）分钟内 `level=error` 达 `ALERT_ERROR_THRESHOLD`（默认 20）条即触发；**未配置 `ALERT_WEBHOOK_URL` 时仍写 WARNING 日志（不静默）**；阈值为 0 表示禁用；统计/推送失败只记异常、绝不影响主服务（与 `clear_old_logs` 同风格）。环境变量与运维说明已同步 `.env.example`、`DEPLOY.md §四/§六`。测试：`tests/test_alerting_policy.py`（策略层，**无需依赖即可本地运行**：阈值边界、负载字段契约与 JSON 可序列化、POST 行为用桩替换 urlopen、网络错误上抛）+ `tests/test_alerting_service.py`（窗口/级别过滤、未达阈值不通知、未配置 webhook 仅写日志、去重窗口内不重复推送、阈值禁用、库故障不外抛）。**同时修复测试收集期的依赖硬失败**：原先 `from support import DbTestCase` 等第三方 import 留在 try 之外，无依赖环境会 `ERROR collecting`（pytest 退出码 2）而非跳过——现已把 `tests/test_core_security.py`、`tests/test_permissions.py`、`tests/test_alerting_service.py` 与 7 个 `scripts/selfcheck_*.py` 改为**模块级 SkipTest**；本地全量 `pytest`（Python 3.14 无第三方依赖）实测 **exit 0 / 0 error / 依赖模块干净跳过**。教训记入 ai-checklist 第 32 条 | feat(ops): 新增错误率告警并修复测试收集期的依赖硬失败 |
| W4-7 威胁建模留痕 | ✅ 已完成 | 2026-10-02 | 新增 `security-review.md` **§十六 威胁建模（STRIDE）**：7 类资产（JWT / 账号凭据 / 帮会数据 / 导入导出文件 / SECRET_KEY / 库与备份 / 审计日志）+ 5 个信任边界 + **18 条 STRIDE 核对**（每条给出威胁场景、现有控制及 `文件:行` 证据、残余风险、处置）。建模产出：①**发现并修复 F-47 导出文件公式注入**（`utils/excel_export.py` 统一 `_text_cell`，对 `=`/`+`/`-`/`@` 开头的值显式置 `data_type='s'`；新增 `tests/test_excel_export_formula.py` 往返验证 5 用例，另以独立脚本直接读回单元格类型复核）；②**修正一处耦合**：该工具原在运行时 import ORM，致纯格式化逻辑无法脱库测试，改为 `TYPE_CHECKING` + `from __future__ import annotations`（行为不变）；③记录 6 项已接受的残余风险（localStorage 令牌且登出不吊销、`plain_password` 明文列、共享账号不可归因、日志无防篡改、备份未加密、无口令复杂度/MFA）与 4 项待决策建议（口令策略/MFA、审计日志外发、备份加密、CSP 收紧）；④§15.3/§15.4 对应结论已同步更正 | docs(security): 补威胁建模并修复导出文件的公式注入 |
| W4-8 ASVS 条目级核对 | ✅ 已完成（6/6 域） | 2026-10-02 | **通道**：`raw.githubusercontent.com` 本机阻断、jsdelivr 超 50MB 拒绝、镜像站失败、`github.com` 曾 503、`api.github.com` 由 **web 工具**取回只进上下文；最终两条可用路径——① **git over HTTPS + 稀疏检出**（首轮 V13/V8/V16）；② **`api.github.com` 内容接口 + PowerShell 本地 base64 解码落盘**（`Invoke-RestMethod` + `[Convert]::FromBase64String`，须用 `-f` 拼 URL、避免 `$f?ref=` 被插值吃掉）。**共 124 条**：V13 21 / V8 13 / V16 17 / **V6 47 / V7 19 / V9 7**（`security-review.md §十七`，逐条结论与证据），统计 49✅ / 29🟡 / 18❌ / 28⚪。**产出发现**：F-49 容器以 root（W1-9）、F-50 读操作 403 未审计、F-51 日志未转义（W4-9）、**F-52 无口令强度下限/弱口令校验**、**F-53 无自助改密且管理端可直接设口令**（后两项为 W4-10）。**已接受取舍**（记录于 §十六/§17.9）：无 MFA、无空闲超时、无异常登录通知、无 `aud` 声明 | docs(security): 完成 ASVS 5.0.0 条目级核对（V6/V7/V9）并登记认证缺口 |
| W4-10 认证加固（口令策略 + 自助改密） | ✅ 已完成（6.2.12 为取舍） | 2026-10-02 | ①**口令策略对齐 ASVS**：抽出 `app/core/password_policy.py`（纯逻辑）——**删除**原「必须同时含字母和数字」规则（**违反 6.2.5**），改为长度 8–128、上下文词表与常见弱口令拦截、不得含登录名、不得为单一重复字符；`schemas/config.py` 改调策略，`schemas/auth.py` 增 `PasswordChangeRequest`。②**自助改密**：`POST /api/v1/auth/password` → `auth_service.change_own_password`（校验当前口令 + 新口令策略 + **`token_version += 1`** 使其他会话旧令牌失效 + 清空失败计数与锁定）。③**测试**：`tests/test_password_policy.py`（13 用例 / 8 subtests，**纯标准库、无依赖即可真跑**）覆盖长度边界、64 位、**纯字母/纯数字/纯符号（6.2.5 关键证据）**、词表、含登录名、重复字符；`test_api_endpoints.py` 增 5 条接口级用例。④**更正审计误判**：首轮 6.2.1 误判未满足、6.2.5 误判满足（均因只审 service 未审 schema），已在 §17.6/§17.9 更正，统计重算为 **52✅ / 29🟡 / 15❌ / 28⚪**。⑤**剩余**：6.2.12 泄露口令比对；6.4.6 管理端设定口令；**前端自助改密入口待做**。**基线 158 passed + 84 subtests、0 warnings** | feat(auth): 口令策略对齐 ASVS 并新增自助改密 |
| W4-11 自助改密前端入口 | ✅ 已完成（**页面交互未验收**） | 2026-10-02 | ①新增 `components/account/PasswordChangeDialog.vue`（当前/新/确认三字段，成功后清空表并通知父组件）+ `AppHeader.vue` 菜单项「修改密码」；成功后 `auth.clear()` 并回登录页（后端已使所有旧令牌失效，主动登出优于等下一个请求 401）。②**三处真实发现并修复**：（a）**拦截器把改密的 401 误判为登录过期**——后端用 401 表示「当前密码不正确」，而 `http.ts` 对非登录接口一律清凭证并跳登录页，会让输错一次密码就被强制登出，已把凭证校验类接口（`/auth/login`、`/auth/password`）一并排除；（b）**组件内 `await` 未 catch** 使接口拒绝逃逸成未处理的 Promise 拒绝（lint / build 都发现不了，组件用例以 unhandled error 抓出）；（c）`el-form.validate()` 实测**校验失败仍放行到提交**，故提交闸门改用纯函数。③**测试基建**：`vitest.config.ts` 补 `@vitejs/plugin-vue`——原先配置只服务纯逻辑用例，**任何 `.vue` 用例都无法加载**（这正是此前没有组件测试的原因）；新增 `utils/passwordForm.spec.ts`（9 用例，纯逻辑）与`components/account/PasswordChangeDialog.spec.ts`（7 用例，jsdom + Element Plus 真跑表单）。④**验证**：`npm run test` → **60 passed / 7 文件、exit 0、无 unhandled error**（此前 44/5 文件）；`npm run lint` 0 error / 10 warning（10 个均为既有 `vue/no-mutating-props` 债，见 W2-8）；`npm run build`（`vue-tsc` + vite）exit 0。⑤**边界（必须明说）**：本机**未开浏览器**（`AGENTS.md §7.4`），因此对话框的实际交互/视觉**未经页面验收**，仅完成类型检查、构建与组件级 DOM 用例 | feat(auth): 前端新增自助改密入口并修正凭证类接口的 401 处理 |
| W4-12 规范复核与前后端口径统一 | ✅ 已完成 | 2026-10-02 | 按 `AGENTS.md §3.3` 第 5 条（grep 旧值）做**只读复核**，产出并修复 **F-54**：①`ConfigGuildPanel.vue` 仍内联「必须同时含字母和数字」的校验与文案，**前端拦、后端收**（后端已按 ASVS 6.2.5 放开组成限制）——改为复用 `utils/passwordForm` 的共用谓词（只校验长度；弱口令词表不在前端复制，口径只维护在服务端），并修正两处 placeholder 与说明文案；②`GuildCreate.admin_password`/`member_password` 的 `description` 仍写旧规则（会误导 OpenAPI 读者）→ 已更新；③`security-review.md` M-3 的历史决策行按 AGENTS §3.4 **保留原文**，另加「修订说明」指向现行策略与 §17.6/§17.9。**权威源同步**：`tech-stack.md` 开发工具表登记 `@vue/test-utils`；`CONTRIBUTING.md` 本地门禁命令由 1 道补全为 5 道（与 CI `repo-hygiene` 一致）；`design-document-v2.md` 权限矩阵与 §4.7 登记「修改本人密码」；`frontend/docs/README.md`、`backend/docs/README.md` 补功能与更新记录。**验证**：前端 test 60 passed / 7 文件、lint 0 error、`npm run build`（vue-tsc）exit 0；后端 pytest 158+84；ruff/compileall 通过 | fix(auth): 统一帮会初始口令的前端口径并同步受影响的权威源 |
| W4-13 容器与拓扑声明核实 | ✅ 已完成（只读复核） | 2026-10-02 | ①**`nginx.conf` vs `nginx.conf.example` 无重复**：两个文件**职责不同且各自写明**——前者是 frontend 容器**内层**（静态资源 + SPA 回退 + 缓存头 + `/api` 反代，明文 :80），是镜像构建输入；后者是**边缘** nginx-proxy 模板（TLS/限流/安全头/默认 server 444），不入部署包，且其头部明确「本文件**不再重复维护内层段**——同一配置两处副本必然漂移」。实测差异 162 行中**无内层指令副本**（无 `server_tokens`/`gzip`/`set_real_ip_from` 等）✓ ②**compose 与 `DEPLOY.md §二` 的差异是设计意图**：仓库内 compose 是**本地/单机演示拓扑**（frontend 映射宿主 80/443 并挂卷挂证书），生产服务器使用**单层 TLS**（frontend 无宿主端口、不挂证书），两者的区别写在 compose 文件头与 §二正文 ✓ ——因此**不新增「compose 必须等于 §二」的门禁**（会把设计意图判成缺陷）。③`.gitignore` 第 99 行是**注释**（说明 `frontend/nginx.conf` 自 2026-10-02 入库），无残留忽略规则 ✓（F-08 修复无副作用）。④**更正一条我自己的旧结论 F-49**：本轮逐行核对 `backend/Dockerfile` 与 `backend/entrypoint.sh`，发现后端**已降权**（`exec gosu appuser "$@"` + chown 卷目录），原结论「后端也以 root 运行」**有误**；前端成立（建了 appuser、chown 了 html/cache/log/pid，但**无 `USER`**）→ W1-9 范围已收窄为**前端**（含监听非特权端口与 compose/DEPLOY 联动，需 Docker 验证）。教训记入 ai-checklist 第 51 条（容器降权要看 entrypoint/exec 全链路，不能只 grep Dockerfile） | docs(security): 更正容器降权结论并登记三项已核实一致项 |
| W4-14 威胁模型与部署声明复核 | ✅ 已完成（只读复核） | 2026-10-02 | ①**`DEPLOY.md §二` 对内层 Nginx 的四项声明全部为真**（逐行核对 `frontend/nginx.conf`）：gzip ✓、`/assets/` 一年 `immutable` ✓、`location = /index.html` 三头 `no-store` ✓、`client_max_body_size 20m` ✓；另 `index.html` 内嵌 meta 缓存标签也与 §二 描述一致 ✓；XFF 为原样透传（未用 `$remote_addr`/`$proxy_add_x_forwarded_for` 覆盖）✓。②**§十六「现有控制」抽查 6 条，数字全对**：长图 800 人上限（`MAX_IMAGE_MEMBERS = 800`）✓、Excel 导入 5000 行（`MAX_IMPORT_ROWS = 5000`）与 5MB（`MAX_FILE_SIZE`）✓、录屏链接 `pattern=r"^https?://"` ✓、日志保留读 `settings.LOG_RETENTION_DAYS` ✓、登录限流 5 次 / 5 分钟（`LOGIN_MAX_FAILURES = 5` / `LOGIN_LOCK_MINUTES = 5`）✓、`plain_password` 按角色脱敏 ✓。③**抓到一条过时的「残余风险」并更正**：STRIDE 第 4 行的「无口令复杂度要求、无 MFA」——口令策略已于 W4-10（2026-10-02）实施（`app/core/password_policy.py`），故改为「**无 MFA**」并在现有控制里补上口令策略；同步更正 16.3 的「残余风险」与「建议」两处。**这条属于「修复完成后忘了回头改风险清单」**——高风险位置是把「残余风险/待决策」写成清单的地方。④教训记入 ai-checklist 第 52 条 | docs(security): 更正威胁模型中过时的口令策略声明并登记复核结果 |
| W4-15 ASVS 判定行抽样复核 | ✅ 已完成（抽样） | 2026-10-02 | **抽样口径（诚实声明）**：§17 共 124 条判定，本轮抽 **8 条**——优先挑「引用 F 编号」或「写着未做/未落库/未转义」的行（修复漂移最可能藏在这里），再抽 5 条 ✅ 行做反向验证。**产出三处过时判定并更正**：①`13.3.2` 原判 ❌「容器实际以 root 运行」——继承自 F-49 的旧结论，后端实为 `gosu` 降权 → 改判 **🟡 部分**（仅前端）；②`16.3.2` 原判 🟡「授权失败的读操作未落库（F-50）」——F-50 已于 W4-9 修复 → **✅ 满足**；③`16.4.1` 原判 🟡「未对换行/控制字符转义（F-51）」——F-51 已修复 → **✅ 满足**。**✅ 行反向验证**：`autoindex` 在两份 nginx 配置中均不存在 ✓、边缘配置 `server_tokens off`（L63，与引用行号一致）✓、两份 `.dockerignore` 均排除 `.git` ✓、`selfcheck_security_fixes.py` 含跨帮会拦截用例 ✓、`DEBUG` 默认 false ✓ —— 5 条全部为真。统计按更正重算为 **54✅ / 28🟡 / 14❌ / 28⚪（124 条）**。**结论**：§17 判定表的失效模式是**「修复落地后没回头改判定」**（至此同类已累计 5 处：6.2.1/6.2.5 在 W4-10 更正，13.3.2/16.3.2/16.4.1 本轮更正）——因此约定规则：**判定行引用的 F 编号一旦标记为已修复，必须重访该行**。教训记入 ai-checklist 第 54 条 | docs(security): 更正 ASVS 三处过时判定并按抽样复核重算统计 |
| W4-16 判定与修复状态同步检查 | ✅ 已完成 | 2026-10-02 | 新增 `scripts/check_verdict_sync.py`（自检 **10 条**，纯标准库；`analyze()` 为纯函数便于历史验证）：从计划 §4 解析已修复的 `F-<n>`，扫描 `security-review.md §17` 判定行，**判定非 ✅ 却引用已修复编号**即报告；`--strict` 有发现即 exit 1。**假阳性处理**：首轮报 `6.2.4`/`6.2.12`（引用 F-52，而 F-52 的「泄露口令集比对」本就未做=取舍）——没有用模糊启发式，而是引入**显式豁免标记**「（残留判定：6.2.4、6.2.12）」（已标注在 F-52 行）。**真实历史反向验证**：喂入 `HEAD~1` 的计划与审查文档，**精确报出第 38 轮修掉的 `16.3.2`/`16.4.1`**，且 `13.3.2` 未被误报（F-49 为「范围收窄」而非「已修复」→ 规则正确不报）。**过程缺陷**：豁免标记最初被自己的 `[:80]` 截断吃掉 → 检查仍误报；已修并补「标记在 80 字符之外」的回归样例。**上线纪律**：接线脚本内先跑 `--strict`，exit 0 才继续接门禁与提交 | ci(quality): 新增「已修复但判定未更新」检查并接为第 7 道门禁 |
| W4-17 V6/V7/V9 抽样复核 + 检查器反向方向 | ✅ 已完成 | 2026-10-02 | ①**抽样方式**：用关键词（已修复/已实现/已加/未做/待/无 MFA）在 §17.6~17.8 的 73 行判定里筛出 10 条易漂移候选，再逐条对代码核实；**诚实边界**：这是抽样，非全量复核。②**抓到一处过时判定**：`6.1.2` 原判 ❌「未维护上下文相关词表用于口令」——W4-10 已建 `app/core/password_policy.py` 的 `CONTEXT_WORDS`（项目名/角色名/常见弱口令）并在设口令时拒绝 → 改判 **🟡 部分**（词表存在于代码、未成文为策略文档，与 6.2.11 同口径）。③**一处措辞自相矛盾**：`9.2.3` 原写「登记为**待办**」，而 §17.9 已把它登记为**取舍** → 改为「登记为取舍（见 §17.9）」。④**其余抽样行核实为准确**：6.2.2 自助改密 ✓、6.2.9 64 位回归用例 ✓、6.2.11 词表在代码未成文 ✓、6.2.12 泄露比对未做 ✓、6.3.3 无 MFA ✓、7.1.1 仅绝对过期 ✓、7.4.1 登出仅前端丢弃/改密经 token_version 失效 ✓、9.2.2 未校验 typ ✓。⑤统计重算为 **54✅ / 29🟡 / 13❌ / 28⚪（124 条）**。⑥**检查器补反向方向**（自检 10→**13** 条）：判定行自称「已修复」却引用一个**未被计划标记修复**的编号 → 报矛盾；与正向规则合成同一 `analyze()`。⑦过程缺陷（如实记录）：我写的一条反向样例同时触发了正向规则（🟡 判定引用了已修复编号），样例自相矛盾 → 自检 12/13；已把该样例判定改为 ✅ 以隔离反向规则（教训见 ai-checklist 第 56 条）。⑧验证：自检 13/13、严格模式 PASS（0 处）、7 道门禁全通过 | docs(security): 抽样复核 V6/V7/V9 判定并给检查器补反向方向 |
| W4-18 秘密清单与轮换手册 | ✅ 已完成（轮换未在真实服务器演练） | 2026-10-02 | ①**先取证再写**：从代码确认 `SECRET_KEY` 的唯一用途是 JWT 签发/校验（`core/security.py:24,30`）→ 因此轮换影响面是**全部登录态失效**，不影响 bcrypt 口令与审计；环境变量清单由 `os.getenv` 全量扫描得出。②**成文**：`DEPLOY.md §六` 新增「关键秘密清单」（7 类秘密的存放位置/访问边界/泄漏影响 + `git check-ignore -v` 验证命令）与「秘密轮换与泄漏处置」（周期建议、6 类秘密的逐步命令与验证、泄漏处置四步）。③**顺带修 F-55**：`frontend/.dockerignore` 补 `.env*`（原先只有 backend 排除 → 两处不一致，且 Vite 会自动读取 `.env*`）；`.gitignore` 补 `.env.development` 并显式 `!.env.example`。④**一次假发现的自我纠正（如实记录）**：我原以为 backend 的 `.dockerignore` 未排除 `.env`，核实后发现**已排除**（`*.db`/`data/`/`logs/`/`tests/` 也已排除）→ **未据此改动任何文件**，真正的缺口只在 frontend ✓。⑤ASVS 判定更新：`13.1.4` 🟡→**✅**（清单与策略已成文）、`13.3.4` ❌→**🟡**（手册已成文，仍无自动化轮换/密钥管理服务）；统计重算为 **55✅ / 29🟡 / 12❌ / 28⚪（124 条）**。⑥**验证边界**：轮换步骤**未在真实服务器演练**（本机无 Docker 守护进程、无生产 `.env`），故只声称「手册已成文且命令可核」 | docs(security): 成文关键秘密清单与轮换手册并修秘密文件处理 |
| W4-19 三份清单型控制成文 | ✅ 已完成 | 2026-10-02 | ①**先取证**（避免又一次「单遍阅读」错误）：读 `core/logging_config.py` 确认滚动文件参数（10MB×5）与日志格式；全仓检索出站调用（`urllib|requests|httpx|socket|aiohttp`）得到**唯一出站是告警 webhook**（`core/alerting.py`）→ 「服务端不抓取用户外链」由**检索证据**支撑（此前只是推断）。②**§15.5 通信需求清单**（security-review）：入站（唯一边缘 80/443）/容器间（proxy→frontend:80→backend:8000，明文容器网）/卷/出站（仅 webhook）/构建期（镜像源）/宿主运维面（certbot、NTP/DNS）/**用户可提供外链**（浏览器直连、服务端不抓取）七类，并写明否定性结论的检索方式（将来若加「服务端截图/预览」必须重评）。③**§四 逐层日志清单**（DEPLOY）：边缘 nginx / 内层 nginx / backend（stdout + 卷内 `app.log`）/ 审计表 `operation_logs` / 告警通道五层，各列记录内容、载体、格式与级别、留存、**检索方式**；并标注两条已接受边界（16.4.2 无防篡改、16.4.3 未外发）。④**§十八 安全事件清单**（security-review）：11 类事件（登录锁定、未知账号探测、越权 401/403、令牌吊销、错误率告警、弱密钥拒绝启动、秘密泄漏、依赖公告、备份损坏、磁盘将满、外链点击）各配检测信号（含证据位置）、影响、响应动作，并**如实标注自动化状态**（6 类 ⏳ 需人工）与改进优先级。⑤判定更新：`13.1.1`/`16.1.1`/`16.3.3` 🟡→**✅**；统计重算为 **58✅ / 26🟡 / 12❌ / 28⚪（124 条）**。⑥验证：7 道门禁复跑全部 exit 0 | docs(security): 成文通信需求、逐层日志与安全事件三份清单 |
| W4-20 CSP connect-src 收窄 | ✅ 已完成（**响应头级未在本机验证**） | 2026-10-02 | ①**先找反证再改配置**：收紧 CSP 前全仓检索前端绝对 URL 与可能触发 `connect-src` 的 API——绝对 URL 仅 3 处（`useRecordingList.ts` 的 URL 正则不发请求、`LoginView.vue` 两个备案号 `<a href>` 属**顶层导航、不受 connect-src 约束**）；`sendBeacon`/`EventSource`/`WebSocket`/`new XMLHttpRequest` 计数**全为 0**；axios `baseURL='/api/v1'` 同源相对路径；vite 的 `127.0.0.1:8000` 代理属**开发服务器**行为、与生产 CSP 无关 → 收窄**不打断功能** ✓。②**改动**：`connect-src 'self' https:` → `'self'`，并在 `nginx.conf.example` 头部写入依据/收益/边界注释。③**判定更新**：`13.2.4` 🟡→**✅**、§15.4-1 标注完成；统计重算为 **59✅ / 25🟡 / 12❌ / 28⚪（124 条）**。④**验证边界（必须明说）**：边缘模板不参与本地镜像构建 → CSP **响应头级效果无法在本机验证** ✗（需服务器/浏览器验收）；本机可验证的是「配置文本已正确收窄」与「前端无反证」。⑤过程缺陷：首次脚本的写入断言拦住了我——我按**假设的措辞**匹配 §15.4-1 行，实际措辞不同 → 该行未改而断言失败（未提交、无半截状态）；已改为按真实文本追加标注。⑥教训记入 ai-checklist 第 59 条。⑦验证：7 道门禁复跑全部 exit 0 | fix(security): 收窄 CSP connect-src 并更新对应判定 |
| W4-21 静态资源扩展名白名单 | ✅ 已完成（**nginx 层未在本机验证**） | 2026-10-02 | ①**白名单依据来自构建产物实测**（非猜测）：`npm run build` 后 `dist/` 扩展名集合 = `.js`×55、`.css`×19、`.html`×1（后者是**根目录** `index.html`，不在 `/assets/` 下）；据此设定 `js|mjs|css|map|png|jpe?g|gif|svg|webp|avif|ico|woff2?|ttf|eot`，其余一律 `return 404`。②**nginx 语义已核对**：内层 location 未定义 `add_header` → 仍继承父层 `immutable` 缓存头（官方语义：仅当本层无 add_header 时才继承）。③**主动放弃一处改动（如实记录）**：原计划顺带给 `frontend/Dockerfile` 加 `RUN nginx -t` 以便 CI 构建即校验配置——但 nginx 在**配置加载期**就解析 `proxy_pass http://backend:8000` 的主机名，构建期无法解析 `backend`（它在 compose 网络里），加了会**弄坏原本可用的镜像构建** ✗；本机无 Docker 无法验证，故**不做**，改为把「nginx 配置无任何自动校验」这一缺口登记在下表。④判定更新：`13.4.7` 🟡→**✅**；统计重算为 **60✅ / 24🟡 / 12❌ / 28⚪（124 条）**。
| W4-22 文档引用存活核对（报告模式） | ✅ 已完成（**不接入门禁**） | 2026-10-03 | ①新增 `scripts/check_doc_refs.py`（自检 **18/18**）：抽取 `memory-bank/*`、`AGENTS/README/DEPLOY/CONTRIBUTING/SECURITY/CHANGELOG`、`.agent/**` 共 **26 个文档**中反引号内的文件引用（支持 `:12`、`:12-34`、`:15,18`；排除 URL、glob、裸扩展名、以 `/` 开头的路由/容器路径、含空格者），核对「文件是否存在」与「行号是否越界」。②**实测结果**：引用 **942 处**，有效 **860**、缺失 **44**、行号越界 **0**、歧义 **38**。③**44 条缺失逐类复核：37 条是「故意不存在」** ✓——运维脚本 16（`deploy.sh`/`backup-db.sh` 等由 `.example` 复制）、运行时数据 10（`nsh.db`/`backend/data/nsh.db`）、改名历史 7（`CLAUDE.md`/`SECURITY-REVIEW.md`/`DATA_ANALYSIS_COMPLETE.md`）、忽略目录 2（`.qoder/plans/*`）、容器/服务器路径 1、占位符 1。④**两条真引用已修**：`styles/medals.css` 与 `verify_e2e.py` 经全仓检索确认**确实不存在** → 已在原文档标注「已移除/历史记录」✓。⑤**结论（有意为之）**：**不接入门禁** ✗——误报率过高（37/44 为故意项），按 ai-checklist 第 55/65 条的口径，**不用堆白名单去救启发式检查**；脚本默认**报告模式（exit 0）**，需要失败语义时显式 `--strict`。⑥**工具自身的 3 个缺陷（如实记录）**：`path.lstrip("./")` 把 `.env.example` 剥成 `env.example` 致误报 ✗、`rest.lstrip("-")` 遇 `-` 得空串致 `int("")` 崩溃 ✗、glob 与裸扩展名误抽 ✗——**均为 `str.lstrip`/字符串裁剪 API 的语义误用**（与早期 `[:80]` 截断同族），已修并各补一条回归样例。⑦已知限制：**无扩展名文件**（如 `.gitignore`/`Dockerfile`）不在覆盖范围。⑧教训记入 ai-checklist 第 69 条 | docs(meta): 新增文档引用存活核对（报告模式）并记录高误报结论 |
| 缺口 | 说明 | 建议 |
|---|---|---|
| nginx 配置无自动校验 | 本地无 nginx、镜像构建期不能跑 `nginx -t`（主机名解析问题）、CI 目前也不校验 | 在服务器/CI 加一步 `docker run --rm -v $PWD/frontend/nginx.conf:/etc/nginx/conf.d/default.conf:ro nginx:alpine nginx -t` 并在条目里用真实容器名替换 upstream；或引入 `nginx -t` 的静态替代（如配置 lint 工具） |

**本轮全量回归复跑结果（2026-10-02，批次 24）**：后端 `ruff` All checks passed / `compileall` exit 0 / `pytest` **158 passed + 84 subtests, exit 0**；前端 `npm run build`（vue-tsc + vite）exit 0 / `npm run test` **60 passed / 7 文件, exit 0** / `npm run lint` 0 error / 10 warning（既有 `vue/no-mutating-props` 债）；7 道门禁自检与实跑全部 exit 0 | fix(security): 内层 nginx 加静态资源扩展名白名单并复跑全量回归 |
| W4-9 审计与日志加固 | ✅ 已完成 | 2026-10-02 | ①**F-50 读接口拒绝留痕**：审计中间件对「非写方法 + 携带 Authorization + 401/403」也落库（匿名 401 不记，避免探测刷日志）；**该路径改为 `await` 落库**——授权失败属罕见路径，且审计不应在进程崩溃时丢失；写操作热路径仍 `create_task`。②**F-51 控制字符转义**：`log_service.escape_control` 把换行/制表等转成 `\x0a` 形态的可见转义，应用于 `username`/`path`/`ip` 与 `sanitize_detail` 的字符串分支（原先该分支只截断不转义）。新增 `backend/tests/test_audit_denials.py`（6 用例，文件库 + stdlib sqlite3 断言）：失效令牌读 401 留痕、帮众读管理员接口 403 留痕（含用户名）、匿名 401 不留痕、写请求拒绝只落一条、含换行用户名落库无真实换行、转义函数本体。**完整基线 140 passed + 74 subtests、exit 0、0 warnings**（该模块与接口级模块连跑 3 次均绿，验证竞态已消除）| feat(security): 审计覆盖带凭证的拒绝请求并转义日志控制字符 |

状态图例：⏳ 待开始 / 🔄 进行中 / ✅ 已完成 / ⛔ 阻塞（写明阻塞项与所需决策）

> **环境备注（2026-10-02）**：本机 `docker --version` = 28.1.1，但**守护进程未运行**（`docker info` 无输出；`docker build` 报 `open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified`）。因此一切依赖镜像构建的验收（W1-1 的实构建、W1-5 的升级验证）在本环境**无法执行**；已改用「Dockerfile `COPY` 上下文源逐个存在性核对 + 配置入库状态 + `bash -n`」作为替代证据，真正的镜像构建门禁由 W2-1 的 CI 补齐。此外本机无 WSL/`sh`，`bash -n` 使用 Git for Windows 的 `C:\Program Files\Git\bin\bash.exe`。

---

## 8. 回归命令清单

> 以下命令为本计划的验收依据；实施时逐条执行并记录输出结论。

```bash
# 1. 仓库卫生与文档一致性
git status --porcelain                          # 期望：干净
git ls-files --eol | awk '{print $1}' | sort | uniq -c   # 期望：单一 eol
python scripts/check_stale_paths.py --self-test && python scripts/check_stale_paths.py   # 期望：PASS（口径与 CI 完全一致）
git ls-files memory-bank | grep -i security     # 期望：全小写 security-review.md

# 2. 换行归一后复核
git diff --stat                                 # 期望：归一提交单独成组

# 3. 文档引用与索引一致性
grep -rn 'security-review\.md' --include='*.md' memory-bank | wc -l   # 引用数应与实体匹配

# 4. 前端静态检查、单测、构建（含类型检查）与镜像构建
cd frontend && npm ci
npm run lint                                    # 期望：0 error / 0 warning（ESLint 干净时不打印 problems 行）
npm run test                                    # 期望：60 passed / 7 文件
npm run build                                   # vue-tsc 类型检查 + vite 生产构建；期望 exit 0
# Windows 本地跑 build 需把 TEMP/TMP 指向工作区，否则 esbuild 临时文件会被拒（见 ai-checklist 第 67 条）
docker compose build                            # 期望：双镜像构建成功（frontend/nginx.conf 已于 W1-2 补齐）

# 5. 部署链路
bash -n deploy.sh.example                       # 语法检查
grep -n 'nginx.conf' DEPLOY.md README.md        # 期望：说明构建前置

# 6. 后端门禁与测试
cd backend && python -m compileall -q app
alembic upgrade head                            # 临时库
python -m pytest -q                             # 期望：178 passed + 89 subtests（含 selfcheck_*.py 改造后的用例类）
ruff check .                                    # 期望：All checks passed（CI 门禁同款）

# 7. 运行时验证
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/health   # 期望 200
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/docs     # 生产期望 404
```

```bash
# 8. 仓库级门禁脚本（均为「自检 + 实跑」两步；CI `repo-hygiene` 同款）
python scripts/check_file_length.py --self-test && python scripts/check_file_length.py
python scripts/check_requirements_pins.py --self-test && python scripts/check_requirements_pins.py
python scripts/check_env_docs.py --self-test && python scripts/check_env_docs.py
python scripts/check_plan_integrity.py --self-test && python scripts/check_plan_integrity.py   # 计划 §4/§5/§7 结构一致性
python scripts/check_stale_paths.py --self-test && python scripts/check_stale_paths.py   # 陈旧绝对路径（原仅在 CI 内联）
python scripts/check_doc_numbers.py --self-test && python scripts/check_doc_numbers.py   # 文档数字/版本一致性
python scripts/check_verdict_sync.py --self-test && python scripts/check_verdict_sync.py --strict   # 判定与修复状态同步
```

```bash
# 9. 其它仓库脚本（同样「自检 + 用法」）
python scripts/check_commit_msg.py --self-test   # 提交消息规范（规则源：.agent/rules/git-commit-message.md）
python scripts/check_commit_msg.py --stdin       # CI 逐个提交校验用法；本地由 .githooks/commit-msg 钩子调用
python scripts/check_doc_refs.py --self-test     # 文档引用存活核对（自检 18/18）
python scripts/check_doc_refs.py                 # **仅报告，非门禁**：误报率高（故意的「不存在」引用），见 §7 W4-22
```

> **权威口径**：本 §8 是回归命令的权威清单；`CONTRIBUTING.md` 与 CI `repo-hygiene` 应与其保持一致（同一批命令）。
> 已知不可运行项：`mypy` **尚未引入**（见 `memory-bank/tech-stack.md` 开发工具表）；如需引入按 W2-3 附录执行。

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

## 11. 验收清点（2026-10-03 全量回归后）

> 目的：把「已在本机真实执行并通过」与「因环境/授权/决策不可执行」分开，避免把未验证当成已验证。
> 下表数字均为**本轮实测**输出（命令见 §8）。环境：Windows PowerShell 5.1（无 WSL/`sh`）、
> Python 3.12（`py -3.12`；3.14 缺 `pydantic-core` wheel）、Node 24 / npm 11。

### 11.1 本机真实执行并通过（可复现）

| 项 | 命令 | 本轮结果 |
|----|------|---------|
| 后端静态检查 | `ruff check .`（0.12.0） | All checks passed（exit 0） |
| 后端字节码编译 | `python -m compileall -q app backend` | exit 0 |
| 后端测试套件 | `python -m pytest`（Python 3.12 + 锁定依赖） | **178 passed + 89 subtests，exit 0**（2026-10-03 实测） |
| 前端测试套件 | `npm run test`（vitest **4.1.11** + jsdom） | **60 passed / 7 文件，exit 0，无 unhandled error**（2026-10-03 实测） |
| 前端 lint | `npm run lint` | **0 error / 0 warning**（W2-8 已于 2026-10-03 用 `defineModel` 清零；ESLint 无问题时**不打印 problems 行**） |
| 前端类型检查 + 构建 | `npm run build`（`vue-tsc` + **vite 6.4.3**；TEMP 指向工作区） | exit 0（≈8.4s，2026-10-03 实测） |
| 门禁 1 行数规则 | `check_file_length.py` | PASS（自检 9/9 + 实跑；自检为 2026-10-02 补齐，此前只有实跑） |
| 门禁 2 依赖锁定 | `check_requirements_pins.py` | PASS（自检 12/12） |
| 门禁 3 环境变量文档 | `check_env_docs.py` | PASS（自检 **14/14**；17/17 已文档化 **且 17/17 已在 `DEPLOY.md` 提及**） |
| 门禁 4 计划结构 | `check_plan_integrity.py` | PASS（自检 8/8；任务↔进度一一对应） |
| 门禁 5 陈旧绝对路径 | `check_stale_paths.py` | PASS（自检 5/5；扫描 **360** 个跟踪文件 0 命中，2026-10-03 实测） |
| 门禁 6 文档数字/版本一致性 | `check_doc_numbers.py` | PASS（自检 8/8；真值 12 表 / 15 迁移 / v1.9，扫描全部当前态行） |
| 门禁 7 判定与修复状态同步 | `check_verdict_sync.py` | PASS（自检 **13/13**；严格模式 0 处） |
| 仓库卫生 | `git status --porcelain` / `git ls-files --eol` | 工作区干净；索引无 CRLF（`i/lf`） |
| 迁移链完整性（CI `backend` job 同款） | `alembic upgrade head`（临时空库，`DATABASE_URL` 指向 `.git/tmp/*.db`） | **exit 0**；落地 **12 张业务表** + `alembic_version`/`sqlite_sequence`，与 `database-design.md` 声明的表数一致（2026-10-03 实测） |
| 应用可导入（CI `backend` job 同款） | `python -c "import app.main"`（`APP_ENV=development`） | exit 0，输出「app.main 导入成功」（2026-10-03 实测） |
| **生产弱密钥启动门禁**（真实启动路径） | 进入 `app.router.lifespan_context`（`APP_ENV=production` + 占位密钥） | `SystemExit 1` + FATAL 提示 ✓；`enforce_secret_key()` / `validate_secret_key()` 亦分别抛 `SystemExit` / `InsecureSecretKeyError` ✓（2026-10-03 实测）。**注意**：该门禁**有意挂在启动期而非导入期**（F-04/W2-6）——用 `import app.main` **测不出来**，须走 lifespan 或直接调用强制函数 |

### 11.2 本机**不可执行**（环境所限，非失败）

| 项 | 任务 | 阻塞原因 | 替代证据 / 后续 |
|----|------|---------|----------------|
| 镜像构建与容器内验收 | W1-1 实构建、W1-5/W1-7 基础镜像升级、W1-9 非 root 运行 | `docker info` exit 1（守护进程未运行） | 已完成 `COPY` 输入存在性核对与 `bash -n` 语法检查；真构建交由 CI `docker-build` job（push 后） |
| 哈希锁文件生成 | W1-4 | 哈希必须由 **3.11** 生成；本机 `py -3.11` 不存在（"No suitable Python runtime found"） | 依赖范围已精确锁定 + 门禁在位；生成建议用 CI 的 3.11 步骤 |
| 页面级交互验收 | W4-11 自助改密入口、W2-8 props 债、既有「F01/F04 交互待验收」 | 按 `AGENTS.md §7.4` 未获浏览器授权 | 已完成类型检查、构建与**组件级 DOM 用例**（W4-11 共 7 条）；获授权后可补 |
| CI 自身运行 | W2-1 | 仓库未 push，GitHub Actions 从未运行 | **7 道**门禁已在本地以脚本形式全部实跑（见 11.1） |

### 11.3 待**决策**（阻塞项均为外部输入）

| 决策 / 输入 | 阻塞任务 | 影响 |
|------------|---------|------|
| `LICENSE` 版权人署名与年份 | W0-1 | Wave 0 唯一未完成项；公开仓库（D-1）下缺失即不合规 |
| 对外联系邮箱（或确认仅走 GitHub 私有渠道） | W4-4 收尾 | `SECURITY.md` / 行为准则的备用渠道仍为占位符 |
| 是否推送本地提交 | — | 提交仅在本地；CI、Release、远端可见性均依赖它 |
| D-4 版本联动（`frontend/package.json` 0.1.0 vs tag v1.2.x） | W3-4 | 影响发布链路一致性 |
| D-5 生产配置去敏入库 | W1-3 | 未确认时按计划退化为 `check-config-drift.sh` diff 告警 |
| 远端分支删除授权 | W3-5 | 3 个已合并分支仍在远端 |
| **默认口令策略**（F-61：`admin123` 在应用自身黑名单内） | W1-14 | 影响首次部署的账号安全与使用体验 |
| **构建产物移出版本库的删除授权**（F-60） | W2-13 | `frontend/tsconfig.node.tsbuildinfo` 仍被跟踪 |

### 11.4 一键复跑顺序

```bash
python scripts/check_file_length.py --self-test       && python scripts/check_file_length.py
python scripts/check_requirements_pins.py --self-test && python scripts/check_requirements_pins.py
python scripts/check_env_docs.py --self-test          && python scripts/check_env_docs.py
python scripts/check_plan_integrity.py --self-test    && python scripts/check_plan_integrity.py
python scripts/check_stale_paths.py --self-test       && python scripts/check_stale_paths.py
python scripts/check_doc_numbers.py --self-test       && python scripts/check_doc_numbers.py
python scripts/check_verdict_sync.py --self-test      && python scripts/check_verdict_sync.py --strict
```

> 另（**仅报告**，非门禁）：`python scripts/check_doc_refs.py`（文档引用存活核对）

> **门禁只写在 CI 里等于本地没有门禁**（本轮实测：陈旧路径检查原先只在 CI YAML，我手搓临时检查时口径不一致，
> 产生 9 处假阳性）——因此本项目现在 **7 道**门禁**全部**是本地可跑的脚本，CI 只是调用它们。另有 1 个**仅报告**的辅助检查 `check_doc_refs.py`（文档引用存活核对；误报率高，**有意不接入门禁**，见 §7 W4-22）。

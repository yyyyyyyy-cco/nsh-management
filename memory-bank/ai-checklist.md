# AI 操作检查清单

> 本文件记录 AI 在本项目中犯过的错误和容易遗漏的联动点与专项检查清单。
> **文档维护规范、权威源映射与同步流程以根目录 `AGENTS.md` 为准（§2–§3）**；本文档保留历史教训与易漏点，两者冲突时以 AGENTS.md 为准。
> **每次修改文档或代码前必读本文件，修改后按清单逐项检查。**

---

## 一、单一权威源规则（核心原则）

每个主题有且仅有一个权威源，其余文件只引用不复制。

> **权威源映射表已迁移至 `AGENTS.md` §2.1**（各文档定位与维护时机见其 §2.2）。

**铁律**：改版本号时，只改权威源。如果其他文件引用了旧值，说明引用写法不够"引用化"，应改为链接。

---

## 二、文档联动规则（血泪教训）

### 2.1 版本号检查

即使有单一权威源，以下位置仍可能直接写死版本号（应逐步改为引用）：

| 版本号 | 权威源 | 可能残留的位置 | 检查方式 |
|--------|--------|---------------|---------|
| 数据库设计版本 | `database-design.md` 头部 | `architecture.md`、`progress.md`、`backend/docs` | `grep "v1\." memory-bank/` |
| 表数量 | `database-design.md` | `architecture.md`、`progress.md`、`backend/docs`、`README.md` | `grep "12 表\|11 表" .` |
| Python 版本 | `tech-stack.md` | `implementation-plan.md`、`README.md` | `grep "Python 3\." .` |

**教训**：2026-08-26 连续三轮才修完版本号散落 — 改了权威源漏了引用方。

重命名任何 `.md` 文件时，必须检查以下位置的引用：

```bash
# 搜索旧文件名的所有引用
grep -r "旧文件名" --include="*.md" --include="*.sh" --include="*.bat"
```

必须检查的位置：
- [ ] `memory-bank/architecture.md`（文档索引，**最容易漏**）
- [ ] `memory-bank/progress.md`（目录树 + 更新记录）
- [ ] `deploy.sh`（tar exclude 列表）
- [ ] 被重命名文件自身的内部自引用（如 `security-review.md` 引用自己的旧名）
- [ ] 更新记录中的历史条目（保留旧名是正确的，不要改）

**教训**：2026-08-26 重命名 `DATA_ANALYSIS_COMPLETE.md` → `data-analysis-complete.md` 和 `SECURITY-REVIEW.md` → `security-review.md` 时，第一轮只更新了 `architecture.md` 和 `progress.md`，漏了 `deploy.sh` 的 exclude 列表和 `security-review.md` 的内部自引用。

### 2.2 新增文件联动

新增任何文件时，必须同步更新：

- [ ] `memory-bank/architecture.md` — 文档索引（目录树 + 文档说明 + 更新记录）
- [ ] `memory-bank/progress.md` — 目录树 + 更新记录
- [ ] `AGENTS.md` — 根目录入口文档，职责变更时更新其文档索引表
- [ ] 上级目录的目录树（如新增 memory-bank 文件要更新 architecture.md 的目录树）

**教训**：2026-08-26 新增 `CLAUDE.md` 和 `ai-context.md` 时，只更新了 `architecture.md` 和 `progress.md` 的更新记录和文档说明，漏了两者的目录树。下一轮才补上。

### 2.3 目录树同步

项目有**两个独立的目录树**，互相不自动同步：

| 目录树 | 位置 | 侧重 |
|--------|------|------|
| 完整项目结构 | `memory-bank/architecture.md` | 文档视角（所有 .md 文件） |
| 代码目录结构 | `memory-bank/progress.md` | 代码视角（前后端源码 + 文档） |

修改时必须**两个都检查**。常见遗漏：
- 根目录新增文件（如 `AGENTS.md`、`GIT-GUIDE.md`）→ 两个目录树都要加
- `.agent/rules/` 新增规则文件 → 两个目录树都要加
- memory-bank 新增文件 → 两个目录树都要加

**教训**：2026-08-26 连续三轮提交都在补目录树遗漏 — 第一轮漏了 `CLAUDE.md`/`GIT-GUIDE.md`/`security-review.md`，第二轮漏了 `.claude/rules/`，第三轮才全部补齐。

---

## 三、配置文件联动

### 3.1 .env.example 与 config.py

`backend/.env.example` 文档的变量必须与 `backend/app/core/config.py` 实际读取的环境变量一致。

**检查项**：
- [ ] config.py 中 `os.getenv()` 的变量是否都在 .env.example 中有说明
- [ ] .env.example 中文档的变量是否真的被 config.py 读取（不是硬编码）
- [ ] 根目录 `.env.example` 与 `backend/.env.example` 的变量是否对齐

**教训**：2026-08-26 审查发现 `backend/.env.example` 文档了 `ALGORITHM` 和 `ACCESS_TOKEN_EXPIRE_MINUTES`，但 `config.py` 硬编码这两个值从不读环境变量 — 文档与代码不一致。同时 `DEBUG` 环境变量在 config.py 中读取但两个 .env.example 都没文档化。

### 3.2 .gitignore 与实际文件

修改 `.gitignore` 后必须验证：
- [ ] `git status` 确认预期忽略的文件确实被忽略
- [ ] `git ls-files` 确认已追踪的文件中没有不该追踪的
- [ ] 新排除的目录如果之前有文件被追踪，需要 `git rm --cached`

**教训**：2026-08-26 将 `.claude/` 改为 `.claude/docs/` 后，`git add .claude/rules/` 被旧缓存拒绝，需要 `-f` 强制添加。

---

## 四、修改后自检流程

> **完整自检清单见 `AGENTS.md` §3.3**（完成后逐项确认）。要点回顾：版本号 / 数量一致性 → 两个目录树完整性 → 路径引用有效性 → 更新记录齐全 → 配置文件联动（.env.example / .gitignore）→ 部署文件联动（deploy.sh / docker-compose）。

---

## 五、已知高频遗漏模式

| # | 模式 | 说明 | 防范 |
|---|------|------|------|
| 1 | 改了权威源，引用方还写着旧值 | 其他文件直接复制了版本号而非引用 | 改权威源后 grep 旧值，残留处改为"详见 xxx.md" |
| 2 | 重命名文件，漏了 deploy.sh | deploy.sh 的 tar exclude 引用文件名 | 重命名后 grep 旧文件名（含 .sh） |
| 3 | 新增文件，漏了目录树 | architecture.md 和 progress.md 各有独立目录树 | 新增后两个目录树都检查 |
| 4 | 改 .gitignore，漏了 git 缓存 | 旧 ignore 规则还在 git 索引中 | 改后 `git add` 验证，必要时 `-f` |
| 5 | .env.example 和 config.py 不同步 | 一边加了变量另一边没跟上 | 改 config.py 时同步检查 .env.example |
| 6 | 更新记录漏写 | 改了内容忘了在 architecture.md/progress.md 记录 | 每次提交前检查两个更新记录 |
| 7 | design-document-v2 的 §2（UI）复制了 ui-style-guide 的内容 | 两个文档主色不一致 | UI 细节只在 ui-style-guide.md 维护 |
| 8 | ui-polish-plan.md 新增动画/变量，但未同步到 ui-style-guide.md §10 | 两个 UI 文档不一致 | 修改 ui-polish-plan.md 后检查 ui-style-guide.md §10 是否需要同步 |
| 9 | UI 优化新增 composable/CSS 动画，未更新 progress.md 和 frontend/docs | 新文件/新功能漏记 | 新增任何 UI 相关代码文件后，检查 progress.md 目录树和 frontend/docs 功能清单 |
| 10 | 同一事实多处复制（公式/目录树/依赖清单/工具链） | 同一内容在 3+ 文档各写一份，改动时只改一处导致互相矛盾（曾出现出勤率公式两版、目录树三份、requirements 失配） | 重复内容一律改为「摘要 + 引用权威源」；2026-09-15 已全量清理，后续新增内容先查权威源表 |
| 11 | 多层反代下 `$remote_addr` 不是客户端 IP | 内层 nginx 用 `limit_req_zone $binary_remote_addr` 时，键是上游代理容器 IP → 所有用户共用一个桶（曾导致登录全站 5 次/分、API 全站 20r/s），日志与审计里的 IP 也全是容器 IP | 内层必须 `set_real_ip_from <代理网段>` + `real_ip_header X-Forwarded-For`，并原样透传 `X-Real-IP`/`X-Forwarded-For`（后端取 XFF 首段）；改反代后实测「外部源第 5 次 429 + 另一源 IP 仍正常」才算通过；边缘层须用 `$remote_addr` **覆盖** XFF（`$proxy_add_x_forwarded_for` 会把客户端伪造值排到首位，污染审计 IP） |
| 12 | 编辑 CRLF 文件被无声改成 LF | 用默认 newline 读写（Python `read_text()`、部分编辑器）会把 CRLF 转 LF，`git diff` 显示整文件变更、掩盖真实改动 | 读写统一 `open(..., newline="")` 保留原行尾；改完用 `git diff --stat` 复核改动行数是否只等于实际改动 |
| 13 | ORM 模型缺 property 导致 `model_validate` 静默丢字段 | 登录接口用 `UserOut.model_validate(user)` 序列化，而 `User` 模型只有 `guild_name` property、缺 `guild_icon` → 登录响应该字段恒取默认值 None（`/me` 手动构造故正常），前端切换账号后表现为"设置被清空"；写入成功但两条序列化路径分叉造成假象 | 给输出 Schema 新增字段时，同步检查 ORM 模型是否有对应属性/property；同一模型存在「`model_validate` 与手动构造」两条序列化路径时，两侧都要覆盖，并用实证脚本逐字段对比 |
| 14 | 数据归属字段可被请求体覆盖（跨帮会越权） | `POST /config/accounts` 原实现 `target_guild_id = body.guild_id or current_user.guild_id`：管理员在请求体附带其他帮会 `guild_id` 即可为目标帮会创建账号（可含 admin 角色）→ 跨帮会接管（同类正确模式见 `update_guild_icon` 的 403 归属校验）；2026-09-18 已修复并加固（管理员仅本帮会，开发者目标需存在） | 数据归属一律取认证上下文（`current_user.guild_id`）；仅确认角色范围后（如 developer）才允许请求体指定，且服务层校验目标归属/存在；新增写接口时对照同资源既有接口的归属校验模式做交叉检查 |
| 15 | 分页响应模型 `items` 声明基类 → 子类额外字段被静默裁剪 | 改名申请审核列表项为 `GameIdRequestAdminOut`（含 `requester_username`），若塞进 `items: list[GameIdRequestMemberOut]` 的 Page 模型，Pydantic 会按基类重建并丢弃快照字段（实测 KeyError: 'requester_username'）；与第 13 条同源——「序列化路径按声明类型收敛」 | 角色相关响应字段不同时，为每种角色各建一个 Page/响应模型（如 MemberPage / AdminPage），不要用基类接收；新增字段后用实证脚本断言响应 JSON 中确实存在该键 |
| 16 | 回滚后访问 ORM 实例属性触发 `MissingGreenlet` | 审核事务在 `session.rollback()` 后拼装错误消息时读取 `record.new_game_id`，实例已过期 → 异步下同步 lazy load 报 `greenlet_spawn has not been called`（表现为 500 而非预期的 409） | 事务内需要的字段在首次读取时先取局部快照（`new, old = record.x, record.y`），rollback 后只用局部变量；同理不要在 rollback/commit 后继续访问已过期实例的属性 |
| 17 | 并发/竞争类回归断言假设单一写者 | 「直接改名 vs 审核通过」并发用例断言「approved ⇒ 成员名 == 新 ID」，但审核通过后管理员再次直接改名是合法交错 → 间歇失败（实测 4 次 1 次失败），文档却据此声称「5 项全部通过」 | 断言业务不变量（无后续写入者才要求名称等于新 ID、改名必留已确认关联、失效后名称必为直接改名结果），不锁定最终值；并发用例定稿前多跑几次 |
| 18 | 将 Vue 模板转义误当作所有 HTML 输出的保护 | ECharts 自定义 formatter 绕过模板，姓名/职业/阵营直接拼接仍可注入 HTML；详见 security-review §十二 | 沿数据流检查每个 HTML 输出入口，只转义动态文本；图表重构后核对所有同类 formatter，不改源数据或 Canvas 标签 |
| 19 | 防抖保存与重载各自执行，旧快照覆盖未保存编辑 | 切回 Tab 会重载，自动保存到执行时才读当前状态；重载可能先覆盖编辑，再把旧内容保存回服务器 | 保存串行化并记录编辑版本；重载先保存，返回时校验请求序号与编辑版本；失败保留本地数据，导入及卸载前处理待保存任务，回归顺序见 frontend/docs |
| 20 | 非 cmd shell 中 `> nul` 重定向误创建 nul 文件 | `nul` 在 cmd 中是空设备，但在 Git Bash / Node / Python 子进程等 POSIX 风格 shell 中按普通文件名处理 → 在 CWD（曾为 backend）生成真实文件 `backend/nul`；曾把一次后端 SECRET_KEY FATAL 报错写入其中并被误认为"文件被更改"，且因 Windows 保留名难以常规删除 | 跨 shell 的输出重定向统一写 `> /dev/null`（Git Bash 兼容），仅在 cmd 脚本（.bat）内使用 `>nul`；发现 nul 文件用 `del "\\?\<绝对路径>\nul"` 或 .NET `File.Delete` 删除（需 `\\?\` 前缀）；.gitignore 已加 nul 防御 |
| 21 | 用命令**输出**而非**退出码**判定静默命令（`git check-ignore -q` 等） | PowerShell 中 `[bool](git check-ignore -q path)` 或 `if(git check-ignore -q path)` 取的是 stdout——`-q` 时恒为空 → 恒为 `False`，与是否命中规则无关。2026-10-02 据此误报「`deploy.sh` 不再被忽略」（实际仍由 `.gitignore:98` 忽略，属错误结论；同一批 `-q` 判定全部不可信） | 静默命令一律判退出码：`git check-ignore -q p; if($LASTEXITCODE -eq 0){…}`；或直接用 `git check-ignore -v p` 查看命中的规则行。审查/验收类结论必须用可复现手段二次确认，并记录所用命令与判定依据 |
| 22 | 计数类结论未记录匹配范围与大小写选项 | 统计「陈旧绝对路径」时只 grep `*.md` 且 `Select-String` 默认不区分大小写 → 漏计 3 个 `.py` 脚本中的 4 处硬编码路径，并把历史记录里**另一项目**的路径计入本仓库（`F-37` 首次记为 23 处，实为活引用 25 处 + 历史 2 处） | 计数结论必须写明命令、匹配范围与选项（`-CaseSensitive`／`--` 分隔的 glob 列表），并在得出「已清零」结论前用不同手段（如按扩展名分桶、`-v` 明细）复核一次；详见 `.agent/plans/compliance-remediation-plan.md` §10 |
| 23 | 门禁的检测模式串被**其自身文件与文档**命中（新门禁首发即红） | W2-1 的 CI 检查以 `grep -F` 拦截旧仓库绝对路径，但 workflow 自身、两条更新记录、以及**描述该门禁的文档**都含该字面量 → 首次运行必然失败（实测：先被更新记录命中 2 处，修好后又被本计划的说明段本身命中） | ① 门禁模式串在脚本内**拆开拼接**（`PREFIX='e:\code\@Cjy'` + `"${PREFIX}\\nsh-management"`），使字面量在文件内不连续；② 文档/记录中引用此类字面量统一用省略号形式（本项目约定 `e:\code\@Cjy\...`）；③ 新门禁上线前必须在本机对全仓实跑，双向确认「现状通过 + 注入违例后失败」——只验证「能报错」或只验证「能通过」都不够 |
| 24 | 提交消息经 PowerShell 传参被拆开；`git commit -F` 时漏写首行主题 | ① `git commit -m $body` 的这段正文含 `"` 与 `|`（技术说明里的类型注解写法）时，PowerShell 原生传参把参数拆成多段，git 将残段当作 pathspec → 报 `pathspec '\|' did not match` 并**提交失败**（实测）；② 改用 `-F <文件>` 后，因文件首行直接写正文，git 取首行作 subject → 整段正文成了主体，不符合 `<type>(<scope>): <中文摘要>`（实测，需 `--amend -F` 重写后才合规） | 多行或含引号的提交消息一律写文件后 `git commit -F <file>`（用 `.git/` 下的临时文件，提交后删除，避免误入库）；`-F` 文件**首行必须是主题**、空一行再写正文；提交后立即 `git log -1 --format='%s'` 复核主题格式与摘要长度（≤50 字符），发现不合规且未推送时用 `--amend -F` 修正；另注意管道到 `Select-Object` 会吞掉退出码（显示为 -1），应以 `git log` 结果为准 |
| 25 | PowerShell 向原生程序传文本会注入 BOM / 重编码 / 数组被空格拼接（导致校验假阴性） | 用 `$msg \| python scripts/check_commit_msg.py --stdin` 模拟 CI 时，**10 个完全合规的提交全被判违规**：① PowerShell 写入管道时加了 UTF-8 BOM（`\ufeff`，因把 `[Console]::OutputEncoding` 设为 `[System.Text.Encoding]::UTF8`——该类是**带 BOM** 的），中文还按控制台编码出现乱码；② 改用文件方式前还有一次误报「摘要 283 字符」，根因是 `WriteAllText($f, $msg)` 收到的是**字符串数组**，PowerShell 默认用空格把多行拼成一行 | ① 向原生程序传文本**优先走文件**（`--stdin` 类接口在 PowerShell 下不可靠），或用 `& git ... \| Out-File`；② 必须用管道时把 `$OutputEncoding` 与 `[Console]::OutputEncoding` 设为无 BOM 的 UTF8（`New-Object System.Text.UTF8Encoding($false)`）；③ 参数需要字符串时显式 `-join "\`n"`，不要依赖数组隐式转换；④ 校验器应容忍 BOM（提交消息校验器已加 `\ufeff` 剥离）；⑤ **验证失败先怀疑传递链路，再怀疑被测对象**——本轮若直接采信，会把 10 个合规提交误判为不合规 |
| 26 | 含中文注释的依赖清单未声明编码 → 中文 Windows 下 pip 直接失败 | `backend/requirements.txt` 为 UTF-8 无 BOM 且含中文注释；pip 读取 requirements 时按 **PEP 263 cookie → BOM → 本地 locale** 顺序判定编码，中文 Windows（cp936）下即报 `UnicodeDecodeError: 'gbk' codec can't decode byte 0x8e`，而这条命令正是 README 的安装第一步。Linux/容器 locale 为 UTF-8，故 CI 与镜像构建**从不暴露**该问题——只有真跑一遍本地安装才会发现 | 凡**由工具按 locale 读取**且含非 ASCII 的文件（`requirements*.txt` 等），首行加 `# -*- coding: utf-8 -*-`，并禁止在后续编辑中删除；把「照 README 原样跑一遍安装」纳入验收习惯——纸面检查与 CI 全绿都不能替代实跑 |
| 27 | `git add -A` 把工具在工作区根目录产生的临时目录一并提交（含二进制 wheel） | W2-2 安装/测试期间，pip 在**仓库根目录**生成 `pip-metadata-*/`、`pip-unpack-*/`（含 `.whl` 二进制）与临时 venv `.tmp-venv312/`；一次 `git add -A` 使提交从 17 个文件膨胀到 55 个（452 行 → 5758 行 + 二进制）。更隐蔽的是：路径已被 `.gitignore` 命中后，`git add -A` **不会**为「已跟踪但已删除」的文件暂存删除，残留项需显式 `git rm -r --cached <path>` 才能清除 | ① 提交前**核对暂存清单本身**（`git diff --staged --name-only` 逐条看，或与预期文件数比对），不要只看 `--stat` 汇总；② 工具中间产物尽量放仓库外，或在 `.gitignore` 明确覆盖（已增补 `.tmp-*/`、`pip-metadata-*/`、`pip-unpack-*/`）；③ 误提交且**未推送**：删目录 → `git add -A` → 若路径被 ignore 则 `git rm -r --cached <path>` → `git commit --amend --no-edit`；④ 已推送：改用「移除 + 新提交」，不重写历史 |
| 28 | 新增文件后只在「改动前验证过的范围」跑门禁 → CI 会红 | 第 7 轮先跑 `ruff check .`（当时通过），**之后**才新增 `backend/tests/*.py`；第 11 轮重跑全仓 `ruff check .` 才发现 `tests/test_permissions.py` 未使用的 `unittest` 导入（F401）。若直接 push，CI 的 ruff 步骤必然失败，而本地「之前跑过绿」的结论会掩盖它——门禁结论有**时效性**，必须绑定到最后一次改动之后 | ① 门禁命令在**最后一次改动之后**、对**全量范围**重跑（不做增量、不复用改动前的结论）；② 每轮交付前按 CI 步骤清单逐条本地执行（`ruff check .` / `compileall` / `pytest` / `npm run lint` / `npm run test` / `npm run build`），顺序尽量与 CI 一致；③ 新增的源码与测试文件同等纳入门禁范围（禁止把 `tests/` 排除在外）；④ 本地无法执行的 CI 步骤（如镜像构建）显式标注「未验证」，不得默认通过 |
| 29 | 工具写文件 / 装包后的**静默失配**：编码 BOM 与重复安装 | ①审计时用 `npm audit --json | Out-File -Encoding utf8` 落盘再交给 Node 解析 → `SyntaxError: Unexpected token '﻿'`：本机是 **Windows PowerShell 5.1**（`utf8NoBOM` 不在其参数集内，会直接报参数验证失败），其 `utf8` **必带 BOM**；②`pip install --target .tmp-py314 ruff` 重复执行时 pip 跳过已存在文件且只给 WARNING，随后 `python -m ruff` 抛 `RuffNotFound`（包装器找不到二进制）——表面像「ruff 没通过检查」 | ①跨程序传数据优先**不走文件**；必须落盘时用 `[System.IO.File]::WriteAllText($p,$s,(New-Object System.Text.UTF8Encoding($false)))`，或在**读侧**剥离 BOM（JS `raw.replace(/^\uFEFF/,'')`、Python `encoding='utf-8-sig'`）；②`pip install --target` 重装需加 `--upgrade`（或先清空目标目录）；③**区分「工具没跑起来」与「工具报错」**：先看是否为 Traceback / 找不到二进制，再下结论——本轮若把 `RuffNotFound` 当成「检查未通过」就会误报结论 |
| 36 | **`pytest -q` 会与 `addopts` 里的 `-q` 叠加成 `-qq`，最终汇总行被抑制** | 我为了“安静”在命令行又加了一个 `-q`，于是 `124 passed, …` 这行**根本不打印**——我连续两次读日志都只看到 warnings summary，误以为是重定向把文件截断了（日志只有 687 字节）。真实原因是 **`-qq` 不输出汇总**，与重定向、编码都无关 | ①取测试结论时要**看清 addopts**（本项目 pytest.ini 已有 `-q`）；②要么不加额外 `-q`，要么用 `-p no:cacheprovider` 之外的显式输出（如 `-rA`）或直接读退出码 + `--junitxml`；③「日志变小/缺行」先怀疑参数叠加，再怀疑重定向 |
| 40 | **审代码时只看了 service 层 → 审计结论出错** | 我把 ASVS 6.2.1 判为「无口令长度下限、管理端可设 1 位口令」，实际 `schemas/config.py` 的 `AccountCreate.password` 有 `min_length=8`；同时 6.2.5 我判为「满足」，而实现**强制字母+数字**恰好违反该条。两处都源于**只读 `account_service` 未读请求 schema** | ①审「输入类」控制要沿**请求入口**走全链路：`schemas/**` → `api/v1/**` → `services/**`，任一层有校验就算覆盖；②下「未满足」结论前先 **grep 全链路**（如 `password`）再判断；③判错要**同步更正文档与统计**，不要留旧结论（本轮已更正 §17.6/§17.9 与统计表） |
| 43 | **把 `el-form.validate()` 当作提交闸门不可靠** | 改密对话框实测：字段已显示「8–128 位」错误提示（校验确实失败了），但 `validate()` 的 Promise 形式仍让流程走到提交、接口被调用（换成回调形式后另一个用例又出现“合法输入未提交”）| ①**提交闸门用纯函数**（本项目落在 `utils/passwordForm.ts`），Element Plus 的 `rules` 只负责界面提示，两者共用同一批谓词避免口径分叉；②纯函数闸门可以脱离 DOM 测试；③不要把组件库的“表单校验返回值语义”当作契约，要以**实测行为 + 用例**固定下来 |
| 44 | **组件里 `await` 异步调用不 catch → 未处理的 Promise 拒绝** | 改密对话框提交处理器用 `try/finally` 包了一次 `await changePassword(...)`；接口拒绝（如当前密码错误）时异常从点击处理器逃逸，Vue 报「Unhandled error during execution of component event handler」，vitest 因 unhandled error **exit 1**（用例本身全绿）。`lint` 与 `vite build` 都发现不了 | ①组件内异步调用一律 `catch`（错误提示交给统一拦截器，`finally` 负责复位 loading）；②**`npm run test` 的退出码要一起看**：全绿但 exit 1 通常就是未处理错误/未处理拒绝；③这正是组件用例的价值——发现它靠的是组件级测试而非静态检查 |
| 66 | **本机 `pip` 与 `npm` 同一个病：上游源不可达、镜像可达；升级要选「最小修复版本」并逐包复核** | npm 配置的是 `registry.npmjs.org`（本机**超时** ✗），`registry.npmmirror.com` 可达 ✓——和 pip 完全同类。升级前端工具链时我先升 `vite`→6.4.3（顺带把 `esbuild` 带到 0.25.12）、再单独升 `vitest`→4.1.11，**一次只动一个变量**并先备份两文件；每一步都复跑 build/test/lint | ①**先探源再装**：`Invoke-WebRequest` 探测 registry，**按命令传 `--registry`**（不改全局配置、不把镜像写进仓库 `.npmrc`）；②**选最小修复版本**：vite 6.4.3 而非 7.x，且它自带 `esbuild ^0.25` 一次清两条；③**实际版本以 `npm ls` 为准**（声明 `^x` ≠ 实装 x）；④**升级后要复核公告**（同一 API 对新版本再查）；⑤**API 会返回上游已撤回的公告** ✗——必须看 `withdrawn_at` 是否为空的**实证**，不能只看摘要里的 “Withdrawn” 字样；⑥**PowerShell 内联中文字符串会被编码弄坏** ✗（本轮解析期失败、脚本没跑）→ 中文一律放进 Python 脚本文件里写 |
| 65 | **依赖安全核对要用「按包 API 查询 + 程序化比对范围」，并区分运行期与开发期** | 本轮用 GitHub Advisory API 的 `affects=<包>` 逐包核对 12 个后端固定依赖 + 19 个前端包：后端**受影响 0 条**（Pillow 78 条公告的修复版都 ≤ 本地 12.3.0；starlette 最新上限 < 1.3.1）；前端 6 条**全部在 dev 工具链**（vite/esbuild/vitest），运行期 0 条 | ①**别用检索摘要判漏洞**：API 返回结构化 `vulnerable_version_range` 与 `first_patched_version`，可程序化比对；②`first_patched_version` 有时是**字符串**有时是对象 ✗——取值要容错（本轮踩过 `AttributeError`）；③**未查询成功的包不得计入「已核对」**（网络/限流失败要显式列出）；④**区分运行期与开发期**：dev-only 公告的处置是「配置级缓解 + 登记升级窗口」，不是紧急升级；⑤缓解要说**配置证据**（本轮核实 `vite.config.ts` 未设 `host` → 默认仅绑 localhost ✓），不能口头声称「开发服务器不外露」；⑥跨大版本升级（vite 5→6/7 等）**必须带全量回归**再动 |
| 64 | **「把上限收紧」这种修法可能违反另一条标准；升级底层库前必须实测其对边界输入的行为** | F-57（bcrypt 只取前 72 字节）我最初定的修法是「策略按 72 字节收紧」——实测**72 字节对中文只有 24 个字符**，而 ASVS **6.2.9 要求允许 ≥64 字符** → **收紧本身就违规** ✗；正解是 OWASP 的 `base64(SHA-256(口令))` 预哈希 ✓。同时实测 **bcrypt 5.0.0 对 >72 字节连 `checkpw` 都报错** ✗ → 此刻升级会**锁死**既有超长口令用户 | ①改策略/限制时，**逐条回看是否与其它条目冲突**（尤其「必须允许 ≥N 字符」这类下限）✗；②升级底层库前**实测边界输入**（超长/空/畸形），不要只看 changelog；③换哈希方案必须**保留旧哈希校验路径** + 写**端到端迁移用例**（登录后升级、失败不动、已新版不重写）；④**`ruff check` 的「No fixes available (1 hidden fix can be enabled with --unsafe-fixes)」表示有违规，不是通过** ✗——别把「取最后一行」当结果，要看退出码或 `Found N errors`；⑤断言异常要具体（`AuthError` 而不是 `Exception`）| 
| 63 | **换底层库时「异常类型集合」会变：passlib 返回 False 的输入，bcrypt 会 Rust panic（且不是 `Exception` 子类）** | 把 `passlib` 换成 `bcrypt` 时我给 `verify_password` 写了 `except (ValueError, TypeError)`；实测 `bcrypt` 4.x 遇**截断哈希**抛 `pyo3_runtime.PanicException`，MRO `PanicException → BaseException → object`，`isinstance(e, Exception)` 为 **False** ✗ → 异常穿透，会把「库中损坏哈希」变成登录 500（passlib 时代返回 False）——**这是改动会引入的回归**，被「先写兼容性用例」挡在提交前 ✓ | ①**换库先列异常契约**：新库在「缺失/损坏/非法输入」上返回什么、抛什么？②只放宽捕获范围不够——**先格式预校验**把非法输入挡在库外（也避免底层 panic 打到 stderr），再宽捕获兜底，并显式重抛 `KeyboardInterrupt`/`SystemExit`；③测试必须覆盖**损坏输入**；④兼容性测试放**真实历史哈希**（passlib 生成的 `$2b$12$…`），不依赖旧库是否安装；⑤**断言别禁止「词」**：我曾要求文件里不出现 `passlib` 字样，而注释里正要写「已移除 passlib」→ 断言误报两次 ✗；应针对**依赖声明/表格行**断言；⑥**改文本前先打印真实字符**：我用 `replace` 改 tech-stack 的旧说明时目标串不匹配而**静默无果** ✗，是断言才发现 → 改用正则并打印 `repr`；⑦**残留检查别按后缀白名单过滤**（本轮漏 `.md`，`tech-stack.md` 的 passlib 行差点漏掉） |
| 62 | **同一个桩对象的字段在不同模块里语义不同：`status="active"` 在 `image_export` 里等同「替补」** | 写 `image_export` 用例时我参照了既有 `test_excel_export_formula.py` 的 `_Member` 桩（默认 `status="active"`）——但该模块用 `m.status != "formal"` 判定替补，并把非正式姓名渲染为「（替）」；Excel 导出并不关心 `status` ✗ | ①**跨模块复用桩对象前，先确认目标模块读了哪些字段、怎么分支**（本轮改为显式传 `formal`/`substitute`）；②写断言时优先**按实现的公式/常量独立重算**（如高度用模块常量算出），比硬编码期望值更抗改动、也更能暴露实现变更；③覆盖边界要**写进文档**（本轮「恰好 800 人的成功路径未执行」如实标注，不假装全覆盖） |
| 61 | **本机 pip 连镜像也会挂起：改为「从同一镜像取 wheel + `--no-index` 离线装」** | 升 Pillow 时 `pip install`（显式 `-i` 阿里云 / 已配置清华源 / `--only-binary`）**四次全部挂起无输出** ✗，而同机 `Invoke-WebRequest` 取清华索引**只要 0.7s**（status 200，且索引里确有目标 wheel）→ 网络没问题，是 pip 的问题 | ①**先分清「网络坏」还是「工具坏」**：用另一条独立通道（PowerShell 取同一 URL）对照，别一味换源；②可行做法：从镜像页正则出目标 wheel → `Invoke-WebRequest` 下载 → `pip install --no-index --no-deps <本地文件>`；③**不要把手拼的带 `#sha256=` 片段当路径**（我第一次直接用了锚文本，pip 报 Invalid requirement ✗）；④用户说「需要换源」时先看 `pip config list`——本机其实**已配置清华源**，我显式传 `-i` 反而覆盖了它 ✗ |
| 60 | **汇报/收口时的进度数字必须从权威源现场解析，不能凭记忆复述** | 我连续十几轮在汇报里写「Wave 2 12/12 ✅」，而计划 §7 的真实记录一直是 **11/12**——`W2-8`（10 处 props 变更债）**始终是 ⏳ 待开始** ✗。同类还有「Wave 1 状态」等，我都是凭记忆拼的 | ①**进度数字唯一来源是计划 §7 / progress.md**，汇报前现场解析（一条命令即可）；②复述型错误**不会报错、也不会被门禁抓到**（门禁校验的是计划自身一致性 ✓ 而非我的叙述 ✗）——这正是它最容易长期存活的原因；③同理，凡「我一直在说的结论」都要定期回权威源复核；④写解析脚本时**注意同一编号在两个表里都出现**（§5 任务表与 §7 进度表），正则必须限定到目标表，否则会像我本轮一样把 57 条数成 113 条 ✗ | ⑤**事故升级（2026-10-03）**：我用 `^\| W1-11 ` 去改 §7 进度行，结果**先匹配到 §5 的任务行**（同编号前缀相同）→ 把 §5 任务行**覆盖成了进度行** ✗，被 `check_plan_integrity` 以「§7 有进度行但 §5 无任务」拦下（提交未发生）。**规则**：按编号定位计划行时，必须**先确定所属表格**（§5 任务表 / §7 进度表），或用「第一处=§5、最后一处=§7」这类结构假设并**打印上下文复核**，绝不用裸前缀正则直接替换 |
| 59 | **收紧安全策略（CSP/权限/校验）前，先系统找「会不会破坏功能」的反证** | 本轮把 CSP `connect-src` 由 `'self' https:` 收窄为 `'self'`——若前端其实有跨域调用，改了就会静默坏掉。先做反证检索：前端绝对 URL 仅 3 处（URL 正则 + 两个备案号 `<a href>`，后者是**顶层导航、不受 connect-src 约束**），`sendBeacon`/`EventSource`/`WebSocket`/`XMLHttpRequest` 计数全为 0，axios baseURL 为相对路径 `/api/v1` | ①**先证伪、再改**：安全策略改动最容易「看起来更安全、实际打断功能」；②区分**同类但不同机制**：`<a href>` 属导航（`form-action`/`navigate-to`），不是 `connect-src` 管的 fetch/XHR；③把**改动依据**写进被改文件注释，下一个人不必重新推导；④明确**本机无法验证的那一层**（边缘模板不参与本地构建 → 响应头级需服务器/浏览器验收）；⑤**改文档行前先打印目标行**：我按假设措辞去匹配 §15.4-1，实际措辞不同 → 该行没改到而写入断言失败（所幸未提交）；⑥**反复犯的脚本错误要用结构消除**：我第 40/41/44 轮三次写成 `str.replace(a, b, text, 1)`（多传参数）——现改为**共用一个 `insert_row(rel, anchor, row, ensure)` 辅助函数**，并让它在写入后断言 |
| 58 | **写「无某类行为」的否定声明时，必须用全仓检索给出证据** | 从第 26 轮起我在威胁模型里一直写「录屏外链服务端不抓取」——那只是**读了一个 service 后的推断** ✗；本轮为写通信需求清单，全仓检索出站调用（`urllib|requests|httpx|socket|aiohttp`），得到**唯一出站是告警 webhook**（`core/alerting.py`），才把这句话变成有证据的声明 ✓ | ①否定性结论（「无出站」「不抓取」「未使用」）比肯定性结论更容易**凭印象写下**，必须配检索命令与结论；②在文档里同时写明**结论的时效条件**（本轮写了「若将来新增服务端截图/预览类功能必须重评」）；③检索要覆盖同义实现（`requests`/`httpx`/`urllib`/`socket`/`aiohttp`），不要只搜一种写法的库名 |
| 57 | **不要从「A 处是某状态」推断「B 处也是」——要逐个核** | 我发现 `backend/.dockerignore` 排除了 `.env` 后，**先假定** `frontend/.dockerignore` 也有（因为“两处应一致”），据此准备报一个「backend 漏排除」的发现；逐个核对后事实相反：**backend 已排除**（还排了 `*.db`/`data/`/`logs/`/`tests/`），真正的缺口在 **frontend** ✗ | ①「两处应一致」的正确用法是**分别核对后比较**，而不是看一处推另一处；②同类已发生多次（F-52 只看 service、F-49 只看 Dockerfile、本条只看 backend），**共同点都是「抽样推断全量」**；③一旦发现自己准备写一个未核实的发现，先停下来把两个对象都读一遍——本轮因此避免了一次假发现，并把修复落到了真正有缺口的那一侧 |
| 56 | **写用例要「隔离被测规则」——一条样例同时触发多条规则时，样例会自相矛盾** | 我给判定检查器加「反向方向」时写的样例是「判定 🟡 + 自称已修复 + 引用已修复编号」，期望『不报』；但它同时满足**正向**规则（非 ✅ 且引用已修复编号）→ 实际报出 → 自检 12/13 ✗ | ①测规则 A 时必须排除规则 B 的触发条件（本例把判定改成 ✅，正向规则即不触发）；②**一个输入命中多条规则**是常见陷阱，尤其在「同一函数里叠加多个检查」之后；③自检失败先怀疑**样例**而不是实现——本轮实现是对的，错的是我的期望；④扩展既有检查器时要**重跑全部自检**（旧样例也可能因新规则而语义变化）；⑤同一轮里我还写过一次 `str.replace(a, b, tc, 1)`（多传参数）——**脚本报错中止但未产生半截提交**，这得益于提交前的硬门禁与「记录脚本先写完再提交」的顺序 |
| 55 | **自建检查的首批输出必须逐条判真/假阳性；修假阳性要用「显式豁免」而非模糊启发式** | 我为「已修复但判定未更新」写的检查器首轮报 2 条：`6.2.4`/`6.2.12` 引用 `F-52`，但 F-52 的「泄露口令集比对」本就未做（取舍），是**假阳性** ✗。另有一个我自己造的 bug：`fixed_findings()` 把行文本 `[:80]` 截断，而豁免标记在长行**末尾**被截掉 → 仍误报 | ①新检查器首批输出**默认可疑**，逐条判真伪再动手；②修假阳性首选**让规则可显式标注**（本轮「（残留判定：…）」标记），不要堆模糊文本启发式；③用**真实历史版本**（`git show HEAD~1:…`）反向验证——本轮据此确认它能精确报出先前修掉的两处、且不误报第三处；④**解析长行文本别截断**（豁免/标记类信息常在行尾），并为「信息在 80 字符之外」补回归样例；⑤接线脚本内建「先严格模式、exit 0 才继续」的前置断言——本轮它确实拦住了我「先接门禁、后发现仍误报」的顺序错误；⑥**多处编辑的脚本要给每处写入加断言**：本轮 CONTRIBUTING 的锚点假设错了，脚本在 CI/计划已改后中止（部分完成）——锚点要选**稳定且唯一**的行（如「最后一条 `python scripts/check_` 命令」），不要依赖两行相邻 |
| 54 | **判定/结论表在「修复落地」后不会自动更新——到今天累计 5 处过时判定** | 我对 ASVS §17 的 124 条判定是本会话最早做的，本轮抽样 8 条即抓到 **3 处过时**：`13.3.2` 仍写「容器以 root 运行」（后端早已 gosu 降权）、`16.3.2` 仍写「读操作未落库（F-50）」（第 28 轮已修）、`16.4.1` 仍写「未转义（F-51）」（第 28 轮已修）；加上 W4-10 更正的 6.2.1/6.2.5，同类累计 **5 处** | ①**规则**：判定行/结论表里一旦引用了某发现编号（F-xx），该发现被标记「已修复」时**必须重访这一行**（不是只改发现表本身）；②修复提交里除了改动代码与发现表，还要 **grep 该发现的编号在全文的其它引用**（本轮漏掉的正是 §17.1/§17.3 的判定单元格）；③抽样复核要**偏向「引用编号」和「写着未做/未落库」的行**——错误几乎都藏在那里，✅ 行的准确率很高（本轮 5/5 为真） |
| 53 | **PowerShell 里 `"$name: 文本"` 会被当成「盘符限定变量」直接解析失败** | 我在提交脚本里写 `"  $name: $($rt)"` 输出门禁结果，PowerShell 5.1 报 `InvalidVariableReferenceWithDrive`，**整条命令在解析阶段就失败**（门禁没跑、提交没发生）；同一坑本轮前（第 32 轮）已踩过一次 | ①变量后紧跟冒号时一律写 `${name}:`；②**解析错误的特征是「命令什么都没做」**——我的批次脚本、门禁、commit 全部未执行，排查时应先看「有没有产生副作用」而不是去看业务逻辑；③把「脚本没跑」与「脚本跑了但失败」区分开：前者连临时文件、暂存区都不变（本轮正是靠这点确认可原样重跑） |
| 52 | **修复做完了，却忘了回头改「残余风险 / 待决策」清单** | 第 29 轮实施了口令策略（W4-10），但威胁模型 §十六 的 STRIDE 第 4 行仍写「残余风险：**无口令复杂度要求**、无 MFA」，16.3 的残余风险与建议两处同样留着「无口令复杂度」——**文档里最容易被修复漂移甩掉的就是这类清单** | ①任何一次修复落地后，要 grep 的不仅是「旧值/旧版本号」，还包括**「无 X」「缺少 X」「待决策」这类否定式清单**（本轮即按此 grep 找到三处）；②威胁模型/风险登记类文档，建议在「残余风险」列里写清**日期**或指向条目编号，便于判断是否已被后续修复覆盖；③抽查时优先核对**带具体数字的声明**（本轮 6 条数字全对——数字型声明的准确率明显高于清单型声明） |
| 51 | **容器是否降权，不能只 grep Dockerfile 的 `USER`——要看 entrypoint/exec 全链路** | 我在威胁建模阶段把 F-49 写成「容器以 root 运行，Dockerfile 建了 appuser 但从未 USER」，只读了两个 Dockerfile；本轮核对 `backend/entrypoint.sh` 才发现第 9 行就是 `exec gosu appuser "$@"`（配合 `RUN useradd` + chown 卷目录），**后端早已降权**——原结论对后端是错的，只有前端成立（它 chown 了 html/cache/log/pid 却没 `USER`） | ①「运行身份」这类事实要看**运行时入口链**：`Dockerfile`（ENTRYPOINT/CMD）→ `entrypoint.sh`（gosu/su/exec）→ 进程；②只 grep 一个文件就下结论，与本项目第 40 条（审代码漏了 schema 层）是同一类错误；③纠正结论时要**同时**更新发现表、任务范围与相关文档（本轮更正 §4 F-49、§5/§7 W1-9 与 security-review §17.4）；④`USER` 仍未设置，属**加固增强**（CIS Docker 4.1），但把「已经降权」说成「以 root 运行」是失实 |
| 50 | **校验了 A↔B 一致，不等于 A↔C 也一致——同一事实有多份清单时，门禁必须逐个覆盖** | `check_env_docs.py` 一直在校验「代码读取的变量 ↔ `.env.example`」并显示 17/17 通过；但运维实际照做的是 `DEPLOY.md §六` 的表格，它是**第二份清单**——本轮用取键函数比对修复前内容，发现其中 **7 个键**根本没在部署文档出现（模板全绿 ≠ 运维有据可依） | ①凡是「同一个事实被多处罗列」的地方，都要问一句「别处那份谁在管」；②门禁要覆盖**每一个面向不同读者的落点**（开发者看模板、运维看部署文档）；③验证「修复前是否真的不一致」时用 `git show HEAD:<file>` 取旧内容 + **同一套函数**比对，不要凭半截 grep 断言数量 |
| 49 | **门禁为红时仍然提交，且提交信息写了「全部通过」** | 新增数字门禁后我跑了一次六道门禁，输出里 `check_doc_numbers` **exit=1**（报 ai-checklist 的一处旧版号引用），我却在同一命令里继续 `git commit`，消息写成「6 道门禁自检与实跑全部通过」——**当时为假**。这是第 46 条的同类问题（那条是「预先写数字」），但更严重：这次我**看到了红的结果** | ①提交脚本必须**硬门禁**：任一门禁非 0 立即中止并打印是哪一道（本轮已把该守卫写进提交脚本）；②「验证通过」这类句子不要手写进消息——手写就一定会与事实脱钩；③看到失败先修再提交，**永远不要在同一命令里「跑检查 → 无视结果 → 提交」**；④发现已提交的不实声明时按不重写历史原则补更正 |
| 48 | **「人工 grep 旧值」与「门禁自动校验」不是重复劳动——各能抓到对方抓不到的** | 本轮做全仓易腐值普查：人工 grep 抓到 `tech-stack.md` 摘要行仍写 `Python 3.13`（同文件正文已写 3.11）；随后新写的数字门禁一上线，又抓到 `backend/docs/README.md` 引用了**过期的 database-design 版本号**（1.8，实际已是 1.9）——**人工那遍没发现它** | ①AGENTS §3.3 第 5 条的「grep 旧值」要**同时**做两件事：人工按语义查（能发现措辞类漂移）+ 脚本按事实查（能发现数字类漂移）；②门禁的**真值必须来自代码**（`__tablename__` 计数、`alembic/versions` 文件数、文档自身版本），不要来自另一个文档；③历史行（日期开头）与范围写法（如「3.11–3.13 可用」）要显式排除，否则门禁会因历史证据与合法表述误报；④新门禁**上线前先自检**，上线后**先看它报什么再改**（本轮两处旧值都是门禁/普查报出来后才动手的） |
| 47 | **用宽泛子串判断「是否已存在」→ 幂等保护自己被自己打败** | 我给 `ConfigGuildPanel.vue` 补 import 时写了 `if "utils/passwordForm" not in t:`；但**同一次改动插入的注释里已经提到** `utils/passwordForm`，于是判断为「已存在」而**跳过插入 import** → `vue-tsc` 报 `Cannot find name 'requiredError'`。值得注意的是：`npm run test`（60 passed）与 `npm run lint`（0 error）**都没报**——只有类型检查/构建报 | ①幂等判断要用**精确模式**（这里是 `from '@/utils/passwordForm'` 整句），别用会出现在注释/文案里的宽泛词；②**同一脚本内先插入文档性文本、再用文本判断存在性**尤其危险，顺序上应先判断后写入；③前端改动必须跑 `npm run build`（含 `vue-tsc`）——lint 与用例都覆盖不到未定义标识符 |
| 46 | **提交信息里预先写入「未经实测的数字」** | 我给行数门禁补自检时，在同一条命令里先跑门禁、后提交，却在**提交信息中先写了「自检 9/9」**——实际输出的自检结果是 **7/9**（两条自检的期望子串是我凭空想的，与实现文案不符）。于是已提交的 message 含**当时为假**的验证数字 | ①提交信息中的任何数字（用例数、通过率）**只能在看到输出之后**填写，否则改成不含数字的表述（如「自检与实跑均通过」）；②发现已提交的不实数字时**不重写历史**，用后续提交 + 清单/进度如实更正，并把更正写清楚；③自检的期望值要用**实现里确实存在的片段**或完整匹配，别按想象写——本轮两处失败全部源于此；④「工具输出与叙述不一致」时以**输出**为准，这条与第 37 条（工具没跑完不得当作没问题）是一对 |
| 45 | **`vitest.config.ts` 不加载 `@vitejs/plugin-vue` 时，`.vue` 用例根本无法运行** | 首个组件用例报 「Failed to parse source for import analysis … Install @vitejs/plugin-vue to handle .vue files」。此前“没有组件级用例”并非没时间写，而是**配置从未支持过** | ①测试配置要按“将来会测什么”准备（插件/环境），别只满足当下的纯逻辑用例；②jsdom 下驱动 Element Plus 表单用**真实 DOM 节点 + 具体事件类型**（`input` 事件改值、`FocusEvent` 触发 blur）——普通 `new Event('blur')` 会触发组件库的事件参数校验告警；③`el-dialog` 内容经 teleport 且组件多根节点，VTU 的 `findAll('input')` 不可靠，直接查 `document.body` 更稳（用例间清空 body） |
| 42 | **检测器报错时先修检测器、再按结果动手；否则会用检测器的缺陷反推出错误结论** | 我写的计划门禁因正则不认加粗编号（计划里 `| **F-08** |`／`| **W2-8** |`）而报「§7 有进度、§5 无任务：W2-8」，我**当成真缺口给计划补了一行**，结果修好正则后门禁立刻报「§5 任务编号重复：W2-8」——那行本来就有 | ①门禁/脚本首次报错，先**确认它没冤枉事实**（本轮 F-08 就是加的）；②**修正检测器后必须重跑一次**，只用重跑后的结果作为行动依据；③对「文档结构」这类自建门禁，正则要容忍真实排版（加粗、空格、全角括号）并**为每种容忍写自检样例**；④自建门禁的假阳性会造成真实的错误修改，比没有门禁更危险 |
| 41 | **TestClient 的请求可能在新事件循环里执行 → `:memory:` 库就是空库** | 接口级用例从内存库改文件库前，大面积 `no such table: users`；根因是 aiosqlite 的 `:memory:` 是 **per-connection**，新循环/新连接=空库。另一次是在**同步上下文里**`asyncio.run(...)` 查内存库，同样拿到空库 | ①需要跨请求共享数据的测试**一律用临时文件库**（放 `.git/tmp`，避免残留在仓库树内被 `.gitignore` 掩盖）；②在同步上下文断言就用 **stdlib `sqlite3`** 直接读该文件，别从同步代码调异步库；③引擎按需新建（`NullPool` + `fresh_factory()` 返回 session），避免跨循环复用连接 |
| 39 | **`asyncio.create_task` 的异步副作用会泄漏到后续用例，造成「每次失败点都不同」的假故障** | 我给审计中间件加了「读接口被拒也留痕」后，`test_api_endpoints.py` 出现 4 处 `no such table: users` 失败，且**三次运行的失败用例不一样**；单跑那条又通过。根因是中间件用 `create_task` 异步落库，任务会延后到**后续用例**执行——那时测试的 session 工厂/依赖覆盖已被切换 | ①**失败点不固定 ⇒ 先怀疑并发/竞态，而不是逻辑错误**（逻辑错通常每次都错在同一处）；②长驻进程里的 `create_task` 副作用在测试里会跨用例泄漏，要么在用例中排空任务，要么把该路径改成 `await`；③本项目取舍：**罕见路径直接 `await`**（授权失败 + 审计不宜丢失），热路径保持 `create_task`；④验证手段是**连跑多次**（本轮连跑 3 次全绿）而非一次通过 |
| 38 | **写入脚本的「判重键」太宽松 → 整行被静默跳过** | 我给「追加更新记录行」的脚本写了幂等保护：`if key in 文件全文: skip`，而 key 用了 `W2-2` / `W4-5` 这类**宽泛 token**——文件里早先的记录本来就含这些字样，于是本轮要追加的行被**静默跳过**（两次：第 21 轮 architecture、本轮 architecture），提交后才发现记录缺失 | ①判重键必须**取自被写入内容本身**（如取新行前 60 字符），而不是话题编号/关键词；②写入函数应打印「已存在则 SKIP」并**回读校验**插入后的行数或首 60 字符；③幂等保护的目标是防重复，不是防写入——发现 SKIP 时要先确认「是真的重复，还是键撞车」 |
| 37 | **安全/合规工具没跑完时，不得把“没报问题”当成“没问题”** | 我早期把一次 `pip-audit` 的结果记成依赖审计结论；本轮复核发现 `python-jose==3.3.0`（2021 年，上游 3.4.0 就是为修 JWT CVE 发布）**并不在那次结果里**，而本轮再跑 `pip-audit` 又因网络不可达**根本没跑完** | ①结论必须标注工具版本 + 是否**正常结束**（退出码/耗时/原始输出），「没输出」不等于「无漏洞」；②工具的结论要能被独立证据复核（本轮改用 PyPI 元数据 + 上游发布史）；③发现历史结论不可复核时，**主动更正文档里的适用范围**，而不是继续沿用 |
| 35 | **`IsolatedAsyncioTestCase` 的同步 `setUp()` 早于基类 `asyncSetUp()`**：在 `setUp` 里访问基类在 `asyncSetUp` 创建的资源必崩 | 我在 `tests/test_alerting_service.py` 写了 `def setUp()` 并在其中用 `self.engine` 建 `async_sessionmaker`；`DbTestCase.asyncSetUp()` 才是创建引擎的地方，而同步 `setUp` 先执行 → `AttributeError: 'RunAlertCheckTests' object has no attribute 'engine'`，**5 个用例一起失败**。更值得记的是它为何能藏这么久：该模块在无依赖环境是**跳过**的，直到本轮用 Python 3.12 装齐依赖跑完整套件才第一次真正执行 | ①要访问基类在 `asyncSetUp` 建立的资源，就覆盖 `async def asyncSetUp()` 并先 `await super().asyncSetUp()`；②同步 `setUp` 只做与事件循环无关的准备（如重置模块级状态）；③**「跳过」不是「通过」**——被跳过的用例必须找机会在完整依赖环境跑一次（本轮正是如此才发现 5 个失败；若 CI 曾运行过也会红）；④新增用例后至少要能回答「这条用例在哪个环境真的执行过」 | **`config.py` ↔ `.env.example` 靠人工核对必漏** | AGENTS §3.3 第 7 条要求二者联动，我前面几轮都是「手动看一眼」——本轮写门禁后实跑才发现：代码读 **17** 个环境变量，`.env.example` 只文档化了 **10** 个，**7 个键（DEBUG / DATABASE_URL / LOG_RETENTION_DAYS / DEVELOPER_USERNAME / ADMIN_USERNAME / MEMBER_USERNAME / DEFAULT_GUILD_NAME）是「代码会读、部署者不知道要配」** | ①这类一致性一律固化为脚本门禁（`scripts/check_env_docs.py`，已接入 CI），不要依赖人工核对；②判定要考虑**注释掉的示例也算文档**（本项目 ALERT_*/CORS_ORIGINS 即此风格），同时**行内注释不参与判定**（否则 `# 说明 os.getenv("X")` 会误报——本门禁自检就抓到了这个问题）；③新增环境变量时先写 `.env.example` 再写代码，门禁会兜底 |
| 33 | **esbuild 在沙箱里删不掉 `%TEMP%` 临时文件 → `vite build` 报 `Access is denied`** | `npm run build` 出现 `[vite:esbuild-transpile] remove C:\Users\...\Temp\esbuild-<hash>: Access is denied.`，且 Vite 已清空 `dist/`（构建失败会先清目录）——看着像代码/依赖坏了，**实际是环境权限问题** | ①先看失败发生在哪一步：`vue-tsc -b` 通过、7 千余模块已 transform，只在 esbuild 收尾删临时文件时炸 → 判定为环境问题；②把 `TEMP`/`TMP` 指到工作区内（如 `$env:TEMP="$ws\.git\tmp"`）后重跑即成功；③因此「构建通过」的结论必须附**环境前提**，且在沙箱/权限变化的会话里要重新跑一次，不要复用上一次的结论 | `@unittest.skipUnless` 挡不住**模块级硬 import**：无依赖环境直接收集失败（pytest 退出码 2） | 我在 `tests/test_health.py` 立了「try/except 包运行依赖 + skipUnless 跳过」的范式，却把 `from support import DbTestCase`（它 import sqlalchemy）留在 try **之外**——本地 Python 3.14 跑 pytest 得到 `ERROR collecting … ModuleNotFoundError: No module named 'sqlalchemy'` 与被中断的退出码 2，`skipUnless` 根本没机会执行；同类问题另有 `tests/test_permissions.py`、`tests/test_core_security.py` 与 7 个 `scripts/selfcheck_*.py` | ①需第三方依赖的测试模块，**所有**相关 import 都放进 try，失败时在**模块级** `raise unittest.SkipTest(...)`（pytest 会把整个模块标为 skipped）；②若基类也来自依赖模块，需准备 `unittest.TestCase` 占位基类；③验证方式是在**无依赖环境跑一次全量**并断言 0 error（本轮修完实测 exit 0、依赖模块干净跳过）；④文档里写「缺依赖会自动跳过」之前必须先这样实测，否则只是声明 | **追加式表格的尾部锚点会被自己的写入破坏** | 我为 architecture.md / progress.md 追加更新记录行时，锚点用 `\n\n---\n\n## 使用说明`；替换式写法把锚点前的**空行吃掉**，于是下一轮同一锚点命中 0 次、记录脚本中途退出（本轮 W3-2/W3-3 记录就是这样失败的） | ①锚点不要包含「会被自己改写掉的空白」：用 `\n---\n\n` 这类稳定片段，并**同时尝试 1~2 个换行变体**（合计命中数必须为 1）；②追加操作加**幂等保护**（先检查目标行是否已存在，存在则跳过）；③每个脚本步骤都断言命中数并给出上下文片段——本轮正是靠这条立即定位到锚点失效 | 同一文档内存在**多个同前缀表格**时，用「最后一行匹配 `| 前缀-`」做插入锚点会跨表命中，把行插进错误的表 | 合规化计划同时含 §5 任务表（`| W4-5 | 动作 | …`）与 §7 进度表（`| W4-5 名称 | 状态 | …`）。脚本先按「最后一行 `^\| W4-`」插 §5 任务行 → 实际命中 §7；随后插 §7 进度行时「最后一行」又变成刚插入的 §5 任务行 → 两张表各错一次（本轮修正两遍才对齐）。相关：判定表归属的正则也踩过坑——`^\| W4-\d+ \S` 会同时匹配两种行（§5 行 ID 后紧跟的 `|` 也是 `\S`），须写作 `^\| W4-\d+ \| `（§5）与 `^\| W4-\d+ (?!\|)`（§7） | ①锚点必须**章节内唯一**：先定位章节标题再在其后区间内找锚，或用能区分表的行特征；②插入后**断言每张表的行数与行首序列**；③打印插入点前后 2~3 行人工复核——本轮的错位正是靠打印邻域才发现的；④校验用的正则本身也要先验证：对两种行各取一条做正/负匹配测试，再用于断言 |

---

## 六、安全配置检查清单

修改认证/安全相关代码时：

- [ ] `config.py` 的 SECRET_KEY 是否有安全的默认值（或直接报错）
- [ ] `.env` 中的密钥是否足够强（建议 `openssl rand -hex 32`）
- [ ] 密码策略是否一致（schemas 定义 vs 前端校验 vs 文档描述）
- [ ] 新增 API 是否有正确的权限控制（`get_current_user` / `require_admin`）
- [ ] 级联删除是否覆盖了所有关联表（当前顺序：recordings → match_data → squad_adjustments → attendance_records → lineups → schedules）

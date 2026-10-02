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

---

## 六、安全配置检查清单

修改认证/安全相关代码时：

- [ ] `config.py` 的 SECRET_KEY 是否有安全的默认值（或直接报错）
- [ ] `.env` 中的密钥是否足够强（建议 `openssl rand -hex 32`）
- [ ] 密码策略是否一致（schemas 定义 vs 前端校验 vs 文档描述）
- [ ] 新增 API 是否有正确的权限控制（`get_current_user` / `require_admin`）
- [ ] 级联删除是否覆盖了所有关联表（当前顺序：recordings → match_data → squad_adjustments → attendance_records → lineups → schedules）

# AI 操作检查清单

> 本文件记录 AI 在本项目中犯过的错误和容易遗漏的联动点。
> **每次修改文档或代码前必读本文件，修改后按清单逐项检查。**

---

## 一、单一权威源规则（核心原则）

每个主题有且仅有一个权威源，其余文件只引用不复制。

| 主题 | 权威源 | 其余文件应 |
|------|--------|-----------|
| 技术栈版本 | `tech-stack.md` + `requirements.txt` | 一句话摘要 + "详见 tech-stack.md" |
| 角色与权限 | `design-document-v2.md` §3 | 一句话 + 链接 |
| 功能模块列表 | `design-document-v2.md` §4 | 一句话 + 链接 |
| 代码目录树 | `progress.md` | 不复制，引用 progress.md |
| 文档目录树 | `architecture.md` | 不复制，引用 architecture.md |
| 文档索引 | `architecture.md` | 不复制，引用 architecture.md |
| UI 规范 | `ui-style-guide.md` | 不复制，引用 ui-style-guide.md |
| UI 优化方案 | `ui-polish-plan.md` | 不复制，引用 ui-polish-plan.md |
| Git/分支规范 | `GIT-GUIDE.md` | 3 行摘要 + 链接 |
| 安全要点 | `security-review.md` | 要点摘要 + 链接 |
| 默认账号 | `README.md` | 引用 README.md |
| 启动命令 | `README.md` | 引用 README.md |
| 文件行数规范 | `.claude/rules/file-length-rule.md` | 摘要 + 链接 |

**铁律**：改版本号时，只改权威源。如果其他文件引用了旧值，说明引用写法不够"引用化"，应改为链接。

---

## 二、文档联动规则（血泪教训）

### 2.1 版本号检查

即使有单一权威源，以下位置仍可能直接写死版本号（应逐步改为引用）：

| 版本号 | 权威源 | 可能残留的位置 | 检查方式 |
|--------|--------|---------------|---------|
| 数据库设计版本 | `database-design.md` 头部 | `architecture.md`、`progress.md`、`backend/docs` | `grep "v1\." memory-bank/` |
| 表数量 | `database-design.md` | `architecture.md`、`progress.md`、`backend/docs`、`README.md` | `grep "10 表\|9 表" .` |
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

### 2.3 新增文件联动

新增任何文件时，必须同步更新：

- [ ] `memory-bank/architecture.md` — 文档索引（目录树 + 文档说明 + 更新记录）
- [ ] `memory-bank/progress.md` — 目录树 + 更新记录
- [ ] `CLAUDE.md` — 如果是重要文档，更新文档索引表
- [ ] 上级目录的目录树（如新增 memory-bank 文件要更新 architecture.md 的目录树）

**教训**：2026-08-26 新增 `CLAUDE.md` 和 `ai-context.md` 时，只更新了 `architecture.md` 和 `progress.md` 的更新记录和文档说明，漏了两者的目录树。下一轮才补上。

### 2.4 目录树同步

项目有**两个独立的目录树**，互相不自动同步：

| 目录树 | 位置 | 侧重 |
|--------|------|------|
| 完整项目结构 | `memory-bank/architecture.md` | 文档视角（所有 .md 文件） |
| 代码目录结构 | `memory-bank/progress.md` | 代码视角（前后端源码 + 文档） |

修改时必须**两个都检查**。常见遗漏：
- 根目录新增文件（如 `CLAUDE.md`、`GIT-GUIDE.md`）→ 两个目录树都要加
- `.claude/rules/` 入库 → 两个目录树都要加
- memory-bank 新增文件 → 两个目录树都要加

**教训**：2026-08-26 连续三轮提交都在补目录树遗漏 — 第一轮漏了 `CLAUDE.md`/`GIT-GUIDE.md`/`security-review.md`，第二轮漏了 `.claude/rules/`，第三轮才全部补齐。

---

## 二、配置文件联动

### 2.1 .env.example 与 config.py

`backend/.env.example` 文档的变量必须与 `backend/app/core/config.py` 实际读取的环境变量一致。

**检查项**：
- [ ] config.py 中 `os.getenv()` 的变量是否都在 .env.example 中有说明
- [ ] .env.example 中文档的变量是否真的被 config.py 读取（不是硬编码）
- [ ] 根目录 `.env.example` 与 `backend/.env.example` 的变量是否对齐

**教训**：2026-08-26 审查发现 `backend/.env.example` 文档了 `ALGORITHM` 和 `ACCESS_TOKEN_EXPIRE_MINUTES`，但 `config.py` 硬编码这两个值从不读环境变量 — 文档与代码不一致。同时 `DEBUG` 环境变量在 config.py 中读取但两个 .env.example 都没文档化。

### 2.2 .gitignore 与实际文件

修改 `.gitignore` 后必须验证：
- [ ] `git status` 确认预期忽略的文件确实被忽略
- [ ] `git ls-files` 确认已追踪的文件中没有不该追踪的
- [ ] 新排除的目录如果之前有文件被追踪，需要 `git rm --cached`

**教训**：2026-08-26 将 `.claude/` 改为 `.claude/docs/` 后，`git add .claude/rules/` 被旧缓存拒绝，需要 `-f` 强制添加。

---

## 三、修改后自检流程

每次文档修改完成后，按以下顺序检查：

```
1. 版本号一致性
   └─ grep 所有引用该版本号的文件，逐个确认

2. 表/文件数量一致性
   └─ grep "N 张表" / "N 个" / "N 个版本" 等数量描述

3. 目录树完整性
   └─ architecture.md 目录树 ↔ 实际文件系统
   └─ progress.md 目录树 ↔ 实际文件系统

4. 路径引用有效性
   └─ grep ".trae/" / "design-document.md"（无 -v2）等已知失效模式

5. 更新记录
   └─ architecture.md 更新记录是否包含本次变更
   └─ progress.md 更新记录是否包含本次变更

6. .env.example ↔ config.py 对齐
   └─ 新增/删除环境变量时双向检查

7. 部署文件联动
   └─ deploy.sh exclude 列表是否需要更新
   └─ docker-compose.yml 是否需要更新
```

---

## 四、已知高频遗漏模式

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

---

## 五、安全配置检查清单

修改认证/安全相关代码时：

- [ ] `config.py` 的 SECRET_KEY 是否有安全的默认值（或直接报错）
- [ ] `.env` 中的密钥是否足够强（建议 `openssl rand -hex 32`）
- [ ] 密码策略是否一致（schemas 定义 vs 前端校验 vs 文档描述）
- [ ] 新增 API 是否有正确的权限控制（`get_current_user` / `require_admin`）
- [ ] 级联删除是否覆盖了所有关联表（当前顺序：recordings → match_data → squad_adjustments → attendance_records → lineups → schedules）

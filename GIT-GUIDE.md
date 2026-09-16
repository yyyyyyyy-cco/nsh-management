# 项目 Git 管理规范

> 本文档用于指导 `nsh-management` 项目的日常 Git 使用，包括分支策略、提交规范、版本发布与双远程同步。
> 适用对象：项目所有开发者。

---

## 1. 仓库概览

| 项目 | 值 |
|------|----|
| 本地路径 | `nsh-management/` |
| 默认分支 | `main` |
| 远程 GitHub | `origin` → `https://github.com/yyyyyyyy-cco/nsh-management.git` |
| 远程 Gitee | `gitee` → `https://gitee.com/Gypsophilaaa/nsh-management.git` |
| 当前版本标签 | `v1.1.0`（新增个人战绩、系统日志模块） |

> **双远程策略**：`origin`（GitHub）与 `gitee`（Gitee）互为镜像。任何推到 main 的提交和打出的 tag，都要**同步推送到两个远程**，避免仓库分叉。

---

## 2. 分支策略

### 2.1 分支类型

| 分支 | 命名 | 说明 |
|------|------|------|
| 主分支 | `main` | 唯一长期分支，**始终处于可发布状态**；所有正式版本都从它打出 |
| 功能分支 | `feature/<功能名>` | 开发新功能/模块时使用，如 `feature/squad-analysis` |
| 修复分支 | `hotfix/<描述>` | 紧急修复线上 bug，直接从 `main` 拉出，修复后立即合回 |

### 2.2 分支规则

- **不要在 `main` 上直接开发**。新功能一律从 `main` 拉出功能分支。
- 分支命名用**连字符分隔的小写英文**，如 `feature/data-analysis`、`hotfix/login-timeout`。
- 功能分支合并回 `main` 后，如无继续维护必要，可删除该分支：
  ```bash
  git branch -d feature/xxx            # 删除本地分支（已合并才允许）
  git push origin --delete feature/xxx # 删除远程分支（可选）
  ```

### 2.3 合并方式

合并统一使用 `--no-ff`（不快速前进），保留一条清晰的功能合并记录：

```bash
git checkout main
git pull
git merge --no-ff feature/data-analysis -m "merge(feature): 合并数据分析模块到 main"
```

本项目历史即遵循此风格，例如：

```
c902a15 merge(Data-analysis): 合并数据分析分支到 main
```

---

## 3. 提交规范（Conventional Commits）

统一使用**中文描述 + 约定前缀**的提交信息，保持历史可读、可筛选。

### 3.1 提交格式

```
<类型>(<范围>): <中文描述>
```

示例：

```bash
git commit -m "feat(squad): 新增小队详情弹窗与 4 张可视化图表"
git commit -m "fix(squad-detail): 修复弹窗超出视口的问题"
git commit -m "docs(analysis): 对齐数据分析文档并移入 memory-bank"
git commit -m "refactor(squad): 详情和对比改为弹窗展示"
```

### 3.2 类型说明

| 类型 | 用途 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(export): 排表支持导出 PNG` |
| `fix` | 修复 bug | `fix(login): 修复 token 过期未跳转` |
| `docs` | 文档变更 | `docs(readme): 补充环境变量说明` |
| `refactor` | 重构（不新增功能/不修 bug） | `refactor(api): 统一请求封装` |
| `perf` | 性能优化 | `perf(export): 减少 Excel 导入耗时` |
| `test` | 测试相关 | `test(score): 补充综合评分用例` |
| `chore` | 杂项（依赖、配置、构建） | `chore(deps): 升级 Element Plus` |
| `merge` | 分支合并 | `merge(feature): 合并 xxx 到 main` |

### 3.3 提交原则

- **提交粒度要小**：一个提交只做一件事，方便回溯与回滚。
- **提交前自检**：`git status` 确认没有误把 `.env`、构建产物等加进去。
- **描述要能说清"做了什么、为什么"**，避免 `update`、`fix` 这类无信息量的信息。

---

## 4. 日常开发流程

### 4.1 开始新功能

```bash
# 1. 更新到最新 main
git checkout main
git pull

# 2. 拉出功能分支
git checkout -b feature/data-analysis
```

### 4.2 提交代码

```bash
git add backend/app frontend/src           # 只添加相关文件，避免 git add .
git commit -m "feat(analysis): 新增 CSV 导入与 16 项衍生指标"
```

### 4.3 功能完成，合回 main

```bash
git checkout main
git pull                                    # 先同步远端最新
git merge --no-ff feature/data-analysis -m "merge(feature): 合并数据分析模块到 main"
```

### 4.4 推送并同步双远程

```bash
# 推送 main 到两个远程
git push origin main
git push gitee main
```

> 日常开发中，功能分支可直接推到 `origin` 备份，但**最终合并结果必须同步到两个远程**。

---

## 5. 版本发布流程

采用**语义化版本**（SemVer）：`主版本.次版本.补丁`

- **主版本**：不兼容的重大变更（如数据结构/接口彻底重写）
- **次版本**：向后兼容的新功能
- **补丁**：向后兼容的 bug 修复

### 5.1 打标签

```bash
# 确认 main 处于可发布状态
git checkout main
git pull
git status                       # 工作区必须干净

# 打附注标签（推荐，带发布说明）
git tag -a v1.0.1 -m "release: v1.0.1 修复排表导出偶发空白"

# 查看标签
git tag -n1
```

> **为什么用附注标签（`-a`）**：携带打标签人、时间与说明信息，可校验，适合正式发布。
> 轻量标签（`git tag v1.0.0`）只适合临时标记。

### 5.2 推送标签到双远程

```bash
git push origin v1.0.1
git push gitee v1.0.1
# 或一次性推送全部标签（慎用，会推送所有历史标签）
git push origin --tags
git push gitee --tags
```

### 5.3 发布后

- 需要修旧版本 bug 时，**从对应 tag 拉分支**，修完打补丁版本号再合回 main：
  ```bash
  git checkout -b hotfix/v1.0.1 v1.0.1     # 基于 v1.0.1 修复
  # 修复并提交...
  git checkout main && git merge --no-ff hotfix/v1.0.1
  git tag -a v1.0.2 -m "release: v1.0.2 ..."   # 补丁版本号 +1
  ```
- 版本号与 tag 名称保持一致，**不要** `v1.0`、`1.0.0`、`release-1.0.0` 混用。

---

## 6. 常用命令速查

### 状态与历史

```bash
git status                      # 工作区状态
git log --oneline -10           # 最近 10 条提交
git log --oneline --graph       # 分支图
git diff                        # 查看未暂存改动
git diff --staged               # 查看已暂存改动
```

### 提交与撤销

```bash
git add <file>                  # 暂存指定文件
git restore <file>              # 丢弃工作区改动（未暂存）
git restore --staged <file>     # 取消暂存
git commit --amend              # 修改最近一次提交信息（未推送时）
git reset --soft HEAD~1         # 撤销最近一次提交，保留改动
git reset --hard <commit>       # 回退到某提交（⚠️ 丢弃之后所有改动，谨慎）
```

### 暂存（stash）

```bash
git stash                       # 临时保存未提交改动
git stash list                  # 查看暂存列表
git stash pop                   # 恢复最近一次暂存
```

### 标签

```bash
git tag                         # 列出全部标签
git show v1.0.0                 # 查看标签详情
git checkout v1.0.0             # 检出该版本（脱离分支，只读查看）
git tag -d v1.0.0               # 删除本地标签
git push origin :v1.0.0         # 删除远程标签（⚠️ 会删除正式版本标记）
```

### 双远程同步

```bash
git pull origin main            # 拉取 GitHub
git pull gitee main             # 拉取 Gitee
git push origin main            # 推送 GitHub
git push gitee main             # 推送 Gitee
```

---

## 7. 注意事项

### 7.1 不要提交的内容（已在 .gitignore 中）

以下内容**禁止**提交到版本库，`.gitignore` 已配置忽略，请勿强行 `git add -f`：

| 内容 | 原因 |
|------|------|
| `.env` | 含 `SECRET_KEY` 等生产凭据，仅本地使用 |
| `deploy.sh` / `frontend/nginx.conf` | 含服务器 IP、域名、凭据 |
| `*.tar.gz` / `*.zip` | 发布构建产物，不入源码 |
| `_backup/` | 本地备份副本 |
| `node_modules/` / `.venv/` | 依赖目录，用 `npm install` / `pip install` 还原 |
| `*.db` / `*.sqlite` | 数据库文件，仅存在于本地运行环境 |

### 7.2 检查是否误提交

```bash
git ls-files | findstr /i "\.env tar.gz"     # Windows：检查是否跟踪了敏感/产物文件
```

若发现 `.env` 等被误提交过：**立即从历史中清除并更换密钥**（`SECRET_KEY` 等凭据一旦进过历史就视为已泄露）。

### 7.3 其他约定

- **发布构建产物不进 git**：`nsh-management.tar.gz` 由构建流程生成，由发布脚本处理。
- **大文件/二进制**：避免直接提交大文件，优先走外部分发。
- **不要修改已推送的提交**：如需改动，用新提交覆盖，或明确知会协作者后使用 `git push --force`（本项目单人/小团队使用，仍应谨慎）。

---

## 8. 发布检查清单

发布新版本前逐项确认：

- [ ] `main` 工作区干净（`git status` 无未提交改动）
- [ ] 功能已合入 `main`，且与 `origin`、`gitee` 同步（`git pull` 无更新）
- [ ] 数据库迁移已生成（`alembic revision`）并测试通过
- [ ] 前后端构建通过
- [ ] 打标签：`git tag -a vX.Y.Z -m "release: ..."`
- [ ] 推送标签到双远程：`git push origin vX.Y.Z && git push gitee vX.Y.Z`
- [ ] 按 [DEPLOY.md](DEPLOY.md) 完成部署，线上验证通过

---

*维护建议：本文档随项目规范演进持续更新，重大变更记得用 `docs(git)` 类型提交留痕。*

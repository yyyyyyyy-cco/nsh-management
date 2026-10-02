---
alwaysApply: true
scene: git_message
---

# 必须使用中文撰写全部提交信息


# 生成规则（必须严格遵守）
1. **格式规范**：必须遵循 **Conventional Commits（约定式提交）** 标准，格式为 `<type>(<scope>): <subject>`，如果变更复杂，请在正文（Body）中补充详细说明，与摘要之间空一行。
2. **摘要（Subject）**：
   - 使用**中文 中文 中文 中文**撰写。
   - 长度严格控制在 **50 个字符以内**。
3. **类型（Type）**：从以下选项中严格选取一项：
   - `feat`: 新功能（Feature）
   - `fix`: 修复 Bug
   - `docs`: 仅文档变更
   - `style`: 代码格式（空格、分号等，不影响逻辑）
   - `refactor`: 重构（既非新功能也非修复）
   - `perf`: 性能优化
   - `test`: 增加或修改测试
   - `chore`: 构建工具、依赖或辅助工具变更
   - `ci`: CI/CD 配置变更
   - `merge`: 合并分支（合并提交专用，如 `merge(feature): 合并 X 到 main`）
4. **范围（Scope）**：根据变更的文件路径自动推断影响的功能模块（如 `auth`, `api`, `ui`, `db` 等），必须添加，不能省略。
5. **正文（Body）**（可选）：
   - 如果变更涉及复杂逻辑，请用中文解释 **“是什么”** 和 **“为什么”**，而非仅复述代码变化。
   - 使用项目符号（`- `）列表。
   - 如果变更是简单的单行修改（如修正拼写），则省略正文。
6. **约束**：
   - 不要提及 "根据 diff" 或 "AI 生成" 等无关信息。

## 自动校验（2026-10-02 起）

| 环节 | 位置 | 说明 |
|------|------|------|
| 校验实现 | `scripts/check_commit_msg.py` | 输入方式：消息文件（钩子用法）/ `--stdin`（CI 用法）/ `--self-test`（内置 15 条用例自检）；对 UTF-8 BOM 容错 |
| 本地钩子 | `.githooks/commit-msg` | 版本化于仓库。启用：`sh scripts/install_git_hooks.sh` 或 `git config core.hooksPath .githooks`；卸载：`git config --unset core.hooksPath` |
| CI 门禁 | `.github/workflows/ci.yml` 的 `commit-msg` job | 校验**基线之后**的提交（基线 SHA 见 `.github/commit-msg-baseline`）；基线之前的历史提交不追溯 |

**校验项**：类型白名单（含 `merge`）、scope 必填（允许 `Data-analysis` 这类历史分支名写法）、摘要 ≤50 字符且至少含一个中文字符、禁用「根据 diff」「AI 生成」等表述。
**放行项**：`Merge …`、`Revert …`、`fixup!`/`squash!` 前缀（rebase 中间态）、纯注释消息（视为放弃提交）。

> **多行消息**一律用 `git commit -F <文件>`（首行主题、空行后正文）——`-m` 传含引号的长正文会被 shell 拆参，导致 git 把残段当 pathspec 而提交失败（见 `memory-bank/ai-checklist.md` 第 24 条）。
> **提交后复核**：`git log -1 --format='%s'`，确认主题符合格式且摘要 ≤50 字符；未推送时可用 `git commit --amend -F <文件>` 修正。


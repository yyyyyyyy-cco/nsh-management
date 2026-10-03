# 贡献指南

感谢你愿意为本项目出力。本文件只说明**协作约定与入口**；分支、提交、发布等细节以权威源为准
（下文逐项链接），此处只写摘要，不复制权威源内容。

- [开始之前](#开始之前)
- [环境准备](#环境准备)
- [分支与提交](#分支与提交)
- [代码与文档规范](#代码与文档规范)
- [提交前必须本地跑通的门禁](#提交前必须本地跑通的门禁)
- [Pull Request 流程](#pull-request-流程)
- [报告问题](#报告问题)
- [行为准则与安全](#行为准则与安全)

## 开始之前

1. 先读 [`AGENTS.md`](AGENTS.md)——仓库入口：文档权威源映射、同步流程、硬性行为约定。
2. 产品行为以 [`memory-bank/design-document-v2.md`](memory-bank/design-document-v2.md) 为准；
   表结构与业务规则以 [`memory-bank/database-design.md`](memory-bank/database-design.md) 为准。
3. 本仓库的多数改动由 AI 助手协同完成，规则与人类贡献者相同：**改了代码必须同步文档**
   （见 `AGENTS.md` §3.3）。

## 环境准备

> **依赖拉取超时时先换源（2026-10-03 实测）**：本机（中国网络）访问上游源可能超时——`pip` 可用清华源、`npm` 可用 `npmmirror`。**按命令传参即可，不要改全局配置，也不要把镜像写进仓库文件**：
>
> ```bash
> pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
> npm ci --prefix frontend --registry https://registry.npmmirror.com
> ```


启动命令与默认账号见 [`README.md`](README.md) 的「快速开始」。要点：

- **后端 Python 3.11～3.13**：Python 3.14 目前无法安装依赖（`pydantic-core` 无对应 wheel），
  生产镜像基座为 `python:3.11-slim`。
- **前端 Node 20+**（CI 使用 Node 20）。
- 本地开发库与日志写入 `backend/data/`、`backend/logs/`，均不入库。

## 分支与提交

权威源：[`GIT-GUIDE.md`](GIT-GUIDE.md)（分支策略 §2、日常流程 §4、发布流程 §5）与
[`.agent/rules/git-commit-message.md`](.agent/rules/git-commit-message.md)。

摘要三条（细节一律见上）：

1. `main` 始终可发布；功能走 `feature/<功能名>`，紧急修复走 `hotfix/<描述>`；合并使用 `--no-ff`。
2. 提交格式 `<type>(<scope>): <中文摘要>`，**scope 必填**，摘要 ≤50 字符且含中文。
3. 提交消息受**钩子与 CI 双重校验**：执行 **`git config core.hooksPath .githooks`** 启用本地钩子（跨平台 ✓；`bash scripts/install_git_hooks.sh` 为其脚本封装，但**在 Windows/WSL 环境下可能因策略报 `E_ACCESS_DENIED`** ✗ —— 2026-10-03 实测该脚本在本机 exit 1，而 `git config` 直接生效 ✓）。未启用钩子时**本地提交不会被校验** ✗，不合规消息只会在 CI 暴露（历史上因此累积出 11 条违规 ✓）。

## 代码与文档规范

- 文件行数硬限与拆分要求：[`.agent/rules/file-length-rule.md`](.agent/rules/file-length-rule.md)。
- 模块文档要求：[`.agent/rules/function_rule.md`](.agent/rules/function_rule.md)。
- 分层：`backend/app/api/v1` 薄路由（校验 + 调用）→ `services` 业务逻辑 → `models` / `schemas`。
- UI 相关改动遵循 [`memory-bank/ui-style-guide.md`](memory-bank/ui-style-guide.md)。
- **单一权威源铁律**：任何值/事实只在权威源维护，其他位置写「摘要 + 引用」，禁止复制。

## 提交前必须本地跑通的门禁

下列命令与 [`.github/workflows/ci.yml`](.github/workflows/ci.yml) 的 5 个 job 对应；
按顺序在本地跑一遍再提交（CI 是权威，命令以该文件为准）：

```bash
# 后端（工作目录 backend/）
python -m ruff check .                              # 静态检查（配置 backend/ruff.toml）
python -m compileall -q app scripts alembic         # 语法编译
python -m pytest                                    # 新用例 + 既有 selfcheck_*.py（内存库）

# 前端（工作目录 frontend/）
npm run lint                                        # ESLint（要求 0 error）
npm run test                                        # Vitest
npm run build                                       # vue-tsc 类型检查 + 生产构建

# 仓库根目录——7 道门禁与 CI `repo-hygiene` 完全一致（都支持 `--self-test`，建议先自检再实跑）
python scripts/check_file_length.py --self-test && python scripts/check_file_length.py
python scripts/check_requirements_pins.py --self-test && python scripts/check_requirements_pins.py
python scripts/check_env_docs.py --self-test && python scripts/check_env_docs.py
python scripts/check_plan_integrity.py --self-test && python scripts/check_plan_integrity.py
python scripts/check_stale_paths.py --self-test && python scripts/check_stale_paths.py
python scripts/check_doc_numbers.py --self-test && python scripts/check_doc_numbers.py
python scripts/check_verdict_sync.py --self-test && python scripts/check_verdict_sync.py --strict
```

注意：

- 门禁结论**有时效性**：必须在**最后一次改动之后**对**全量范围**重跑，不要复用改动前的结论，
  也不要只跑改动过的子集（历史教训见 [`memory-bank/ai-checklist.md`](memory-bank/ai-checklist.md) §五）。
- `docker-build` job（镜像构建）需要可用的 Docker 守护进程；本地不具备时请在 PR 中**显式写明「未验证」**，
  不要默认通过。

## Pull Request 流程

1. 从最新 `main` 拉出功能分支（本仓库默认仅维护者可直接推送分支）。
2. 按 `GIT-GUIDE.md` §4 整理提交：单一主题、一次提交一件事。
3. PR 描述包含三要素：**改了什么 / 为什么 / 如何验证**（给出命令与实测输出），
   并列出受影响文档与已同步的权威源。
4. 确认本地门禁全绿、CI 通过后由维护者合并。

## 报告问题

- 缺陷与建议：提交 Issue。请写清**复现步骤、期望行为与实际行为、环境**（版本标签、部署形态、浏览器/系统）。
- **安全漏洞请勿使用公开 Issue**，请按 [`SECURITY.md`](SECURITY.md) 的私有渠道报告。

## 行为准则与安全

- 参与本项目即表示同意遵守 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)（Contributor Covenant 2.1）。
- 安全政策、支持版本范围与报告渠道见 [`SECURITY.md`](SECURITY.md)；
  现有安全结论、已实施措施与**已知接受风险**的权威源是
  [`memory-bank/security-review.md`](memory-bank/security-review.md)。
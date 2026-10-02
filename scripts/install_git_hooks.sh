#!/bin/sh
# ===== 安装版本化 git 钩子（把 core.hooksPath 指向仓库内 .githooks/） =====
# 用法：sh scripts/install_git_hooks.sh
# 作用：使 .githooks/commit-msg 生效（提交消息校验，规则见 .agent/rules/git-commit-message.md）
# 卸载：git config --unset core.hooksPath
set -e

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

if [ ! -d .githooks ]; then
    echo "[错误] 未找到 .githooks 目录，请在仓库根目录执行" >&2
    exit 1
fi

chmod +x .githooks/* 2>/dev/null || true
git config core.hooksPath .githooks

echo "已启用版本化钩子：core.hooksPath = $(git config core.hooksPath)"
echo "生效的钩子："
for f in .githooks/*; do
    [ -f "$f" ] && echo "  - $f"
done
echo
echo "自检（可选）：python scripts/check_commit_msg.py --self-test"
echo "卸载：git config --unset core.hooksPath"
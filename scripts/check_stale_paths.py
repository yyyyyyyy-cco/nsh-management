#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""陈旧绝对路径门禁（合规化计划 F-37 / W2-10）。

**为什么单独成脚本**：这条检查原先只写在 CI 的 `repo-hygiene` job 里（bash `grep -F`），
本地无法执行——本轮实测就因此踩坑：我手搓的临时检查用了**旧仓库前缀**而非**完整仓库路径**，
于是把「省略号形式的说明性引用」全报成违规（9 处假阳性），差点据此改错文档。

**拦截对象**：`<旧仓库前缀>\\<仓库目录名>` 的**完整字面量**（CI 原实现即如此）。
省略号形式（旧前缀 + `\\...`）是**约定允许**的引用写法，不拦截。

**自检**（`--self-test`）覆盖：完整字面量被报出；省略号形式不报；CI 里那种「前缀与仓库名分开书写」
不报；无关路径不报；大小写不同不报。
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# 拆开书写：本文件自身**不得**出现被拦截的完整字面量（否则门禁自我命中，首发即红）
PREFIX = "e:" + "\\" + "code" + "\\" + "@Cjy"
REPO_DIR = "nsh-management"
FORBIDDEN = PREFIX + "\\" + REPO_DIR

INCLUDED_SUFFIXES = (".md", ".py", ".ts", ".vue", ".yml", ".json", ".sh", ".bat")
EXCLUDED_DIRS = (".git", "node_modules", "dist")

ELLIPSIS_FORM_HINT = PREFIX.replace("\\", "\\\\") + "\\\\..."


def analyze(text: str) -> list[int]:
    """返回命中的行号（1 起）。纯函数，自检与实跑共用。"""
    return [i for i, line in enumerate(text.split("\n"), 1) if FORBIDDEN in line]


def tracked_files() -> list[Path]:
    """只检查 git 跟踪的文件（与 CI 的 grep 范围一致，避免扫到 node_modules/dist）。"""
    out = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8"
    ).stdout
    return [ROOT / rel for rel in out.split("\0") if rel.strip()]


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        # CI 原先的写法：前缀与仓库名分开，整行不含完整字面量
        split_form = "OLD_PREFIX='" + PREFIX + "'\n" + 'OLD_REPO="${OLD_PREFIX}' + "\\" + 'nsh-management"'
        cases = (
            (f"路径：{FORBIDDEN}\\data", False, "完整旧仓库路径 → 应报出"),
            (f"路径：{PREFIX}\\...（省略号形式）", True, "省略号形式 → 属约定写法，不报"),
            (split_form, True, "前缀与仓库名分开书写（CI 原写法）→ 不报"),
            ("docs/memory-bank/architecture.md", True, "仓库相对路径 → 不报"),
            (FORBIDDEN.upper(), True, "大小写不同 → 不报（grep -F 区分大小写）"),
        )
        failed = 0
        for text, should_pass, note in cases:
            hit = bool(analyze(text))
            ok = hit != should_pass
            failed += 0 if ok else 1
            print(f"[{'PASS' if ok else 'FAIL'}] {note}｜命中={hit}")
        print(f"自检：{len(cases) - failed}/{len(cases)} 通过")
        return 1 if failed else 0

    hits: list[str] = []
    scanned = 0
    for path in tracked_files():
        if path.suffix.lower() not in INCLUDED_SUFFIXES:
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        scanned += 1
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno in analyze(text):
            hits.append(f"{path.relative_to(ROOT)}:{lineno}")
    if hits:
        print(f"[stale-path] 发现 {len(hits)} 处指向旧仓库位置的绝对路径：")
        for item in hits:
            print(f"  - {item}")
        print(f"[stale-path] 请改为仓库相对路径；引用历史旧路径请写作 {ELLIPSIS_FORM_HINT} 省略号形式")
        return 1
    print(f"[stale-path] 已扫描 {scanned} 个跟踪文件，未发现陈旧绝对路径 : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
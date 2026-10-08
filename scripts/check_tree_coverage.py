#!/usr/bin/env python
"""代码目录树覆盖核对（报告型，默认不失败）。

依据 `AGENTS.md` §3.3 第 3 条「新增文件 → 两个目录树都检查」：
`progress.md` 的**代码目录树**必须登记新增脚本（F-109 登记：该条此前**无人校验** ✗，
本会话第 127 轮真实漂移过一次 ✗ —— 两个新脚本未登记，靠偶然发现才补上）。

本检查只覆盖**已被证据证明会漂移**的范围：`scripts/*.py`。
判定只看**目录树行**（含树形字符 `│├└` 的行 ✓），不整文件子串匹配（ai-checklist 第 124 条 ✓）。
报告型：默认 exit 0；`--strict` 存在未登记文件时 exit 1。
范围说明（2026-10-03 实测）：代码树对 `scripts/` 的覆盖度 = **17/17（100%）** ✓，而 `backend/app/services`(0/22)、`frontend/src/components`(0/72)、`frontend/src/views`(11/34) 等**均为目录级摘要** ✗—— 即约定是「**脚本逐文件列举、源码树用摘要 + 模块表**」。因此**不要扩到其它目录** ✗（会把“约定本身”当成“违规”产生大量误报 ✗）。
文档登记实况（2026-10-03 实测，避免误以为本检查有盲区 ✓）：根目录 *.md **8/8** ✓、`memory-bank/*.md` **15/15** ✓、`backend/docs` **1/1** ✓、`frontend/docs` **1/1** ✓（均在 `architecture.md` 的**索引表/树行**内 ✓）；`.agent/**` 的规则与计划文档登记在 **`AGENTS.md` §2.2** ✓（各占一行 ✓），故本检查**有意不纳入** `.agent/**` ✓。
"""
from __future__ import annotations

import argparse
import re
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TREE = ROOT / "memory-bank" / "progress.md"
TREE_LINE = re.compile(r"^\s*[\u2502\u251c\u2514]")
SCOPE = ("scripts", "*.py")
DOCS = ROOT / "memory-bank"
DOC_INDEX = DOCS / "architecture.md"


def python_files() -> list[str]:
    return sorted(p.name for p in (ROOT / "scripts").glob(SCOPE[1]))


def doc_missing(docs: list[str], text: str) -> list[str]:
    """文档视角：`memory-bank/*.md` 必须出现在**索引表行 / 树行**，
    **排除更新记录行**（首格为日期）——子串判定会被记录行污染（ai-checklist 第 124 条）。
    """
    index = [l for l in text.split("\n")
             if (l.startswith("|") and not re.match(r"^\|\s*\d{4}-\d{2}-\d{2}", l))
             or TREE_LINE.match(l)]
    joined = "\n".join(index)
    return [d for d in docs if d not in joined]


def tree_names(text: str) -> set[str]:
    """目录树行（含树形字符）里出现的文件名集合。"""
    out: set[str] = set()
    for line in text.split("\n"):
        if not TREE_LINE.match(line):
            continue
        out.update(re.findall(r"[\w_.-]+\.(?:py|ts|vue|sh|md|json|yml)", line))
    return out


def analyze(files: list[str], names: set[str]) -> list[str]:
    return [f for f in files if f not in names]


def self_test() -> int:
    failures: list[str] = []
    text = ("\u2502   \u251c\u2500\u2500 scripts/   # \u5de5\u5177\u811a\u672c\n"
            "\u2502   \u2502   \u251c\u2500\u2500 a.py   # A\n"
            "\u2502   \u2502   \u2514\u2500\u2500 b.ts\n"
            "| \u66f4\u65b0\u8bb0\u5f55\u884c\u63d0\u5230 c.py \u4f46\u4e0d\u662f\u6811\u884c |\n")
    names = tree_names(text)
    if "a.py" not in names or "b.ts" not in names:
        failures.append(f"\u6811\u884c\u63d0\u53d6\u5f02\u5e38\uff1a{sorted(names)}")
    if "c.py" in names:
        failures.append("\u8bb0\u5f55\u884c\u88ab\u8bef\u5224\u4e3a\u6811\u884c\uff08\u5b50\u4e32\u6c61\u67d3\uff09")
    if analyze(["a.py", "z.py"], names) != ["z.py"]:
        failures.append("\u672a\u767b\u8bb0\u68c0\u51fa\u5f02\u5e38")
    if analyze(["a.py", "b.ts"], names):
        failures.append("\u8bef\u62a5")
    if doc_missing(["a.md"], "│   ├── a.md\n|更新记录 a.md|") != []:
        failures.append("文档视角：树行已登记却报缺失")
    if doc_missing(["b.md"], "| 2026-10-03 | 更新了 b.md |") != ["b.md"]:
        failures.append("文档视角：记录行被误当登记")
    total = 6
    if failures:
        print("[tree] \u81ea\u68c0\u5931\u8d25\uff1a")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"[tree] \u81ea\u68c0\uff1a{total}/{total} \u901a\u8fc7")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="\u5b58\u5728\u672a\u767b\u8bb0\u6587\u4ef6\u65f6 exit 1")
    args = ap.parse_args()
    if args.self_test:
        return self_test()
    if not TREE.exists():
        print("[tree] [!] \u672a\u627e\u5230 progress.md")
        return 0
    files = python_files()
    names = tree_names(TREE.read_text(encoding="utf-8"))
    missing = analyze(files, names)
    print(f"[tree] \u4ee3\u7801\u76ee\u5f55\u6811\u8986\u76d6\uff1a`{SCOPE[0]}/{SCOPE[1]}` \u5171 {len(files)} \u4e2a\uff0c"
          f"\u76ee\u5f55\u6811\u547d\u4e2d {len(files) - len(missing)} \u4e2a")
    if missing:
        print("[tree] **\u672a\u767b\u8bb0\u5230\u4ee3\u7801\u76ee\u5f55\u6811**\uff08AGENTS \u00a73.3 \u7b2c 3 \u6761\uff09\uff1a")
        for f in missing:
            print(f"  - scripts/{f}")
    else:
        print("[tree] \u672a\u53d1\u73b0\u672a\u767b\u8bb0\u811a\u672c : PASS")
    docs = sorted(p.name for p in DOCS.glob("*.md"))
    dmiss = doc_missing(docs, DOC_INDEX.read_text(encoding="utf-8")) if DOC_INDEX.exists() else []
    print(f"[tree] 文档视角：`memory-bank/*.md` 共 {len(docs)} 个，索引表/树行命中 {len(docs) - len(dmiss)} 个")
    if dmiss:
        print("[tree] **未登记到文档索引**（AGENTS §3.3 第 2/3 条）：")
        for d in dmiss:
            print(f"  - {d}")
    return 1 if (args.strict and (missing or dmiss)) else 0


if __name__ == "__main__":
    sys.exit(main())
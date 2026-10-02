#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文件行数规则检查（CI 门禁）。

规则权威源：`.agent/rules/file-length-rule.md`
用法：`python scripts/check_file_length.py`
退出码：0 = 通过（可含警告）；1 = 存在违规

检查内容：
1. 超限文件必须**同时**满足「① 文件头带 `行数豁免` 标记」与「② 已登记到规则文档的豁免清单」，
   缺任一项即失败（规则原文：新增豁免必须登记，不得只打标记）；
2. 豁免清单中登记的每个文件都必须存在（防止改名/删除后清单悬空）；
3. 豁免文件相对**登记行数**增长 ≥20% 时输出「需重新评估」警告（规则要求豁免文件再增长时重评）。

设计说明：
- 上限与分类必须与规则文档表格保持一致，改规则时同步修改下方 LIMITS；
- 只做静态统计，不修改任何文件。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RULE_DOC = REPO / ".agent/rules/file-length-rule.md"
MARKER = "行数豁免"
GROWTH_WARN = 1.20
EXCLUDE_PARTS = {"node_modules", "dist", "__pycache__", ".venv", "build"}

# (相对目录, 文件模式, 强制上限, 分类名) —— 顺序重要：更严格的规则必须排在前面
LIMITS: list[tuple[str, str, int, str]] = [
    ("frontend/src/utils", "*.ts", 200, "工具函数"),
    ("backend/app/utils", "*.py", 200, "工具函数"),
    ("frontend/src", "*.vue", 300, "组件文件（Vue）"),
    ("frontend/src", "*.ts", 300, "前端 TS（composable / 组件内逻辑）"),
    ("backend/app/services", "*.py", 300, "服务文件（Python）"),
    ("backend/app/api", "*.py", 150, "路由文件"),
]


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def parse_exemptions() -> dict[str, int]:
    """解析规则文档豁免清单表格中的 `文件 → 登记行数`。"""
    if not RULE_DOC.exists():
        print(f"[ERROR] 未找到规则文档：{RULE_DOC}")
        return {}
    out: dict[str, int] = {}
    for line in RULE_DOC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|", line)
        if m and "/" in m.group(1):
            out[m.group(1).strip()] = int(m.group(2))
    return out


def main() -> int:
    exemptions = parse_exemptions()
    if not exemptions:
        print("[ERROR] 未能从规则文档解析出豁免清单（表格格式是否被改动？）")
        return 1

    errors: list[str] = []
    warns: list[str] = []
    checked = 0
    judged: set[str] = set()

    for root, pattern, limit, label in LIMITS:
        base = REPO / root
        if not base.exists():
            continue
        for path in sorted(base.rglob(pattern)):
            if any(part in EXCLUDE_PARTS for part in path.parts):
                continue
            rel = path.relative_to(REPO).as_posix()
            if rel in judged:
                continue
            judged.add(rel)
            checked += 1
            n = line_count(path)
            if n <= limit:
                continue

            head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:120])
            has_marker = MARKER in head
            listed = rel in exemptions

            if not has_marker:
                errors.append(f"{rel} 超限（{n} > {limit}，{label}）且未打「{MARKER}」标记")
            elif not listed:
                errors.append(f"{rel} 已打「{MARKER}」标记但未登记到规则豁免清单")
            else:
                reg = exemptions[rel]
                if n >= reg * GROWTH_WARN:
                    warns.append(
                        f"{rel} 登记行数 {reg} → 当前 {n}（+{(n / reg - 1) * 100:.0f}%），规则要求重新评估是否继续豁免"
                    )

    for rel in sorted(exemptions):
        if not (REPO / rel).exists():
            errors.append(f"豁免清单登记的文件不存在（清单悬空）：{rel}")

    print(f"检查文件数：{checked}（分类上限：{'、'.join(sorted({f'{l}行' for _, _, l, _ in LIMITS}))}）")
    print(f"豁免清单登记：{len(exemptions)} 条")

    if warns:
        print("\n[WARN] 需重新评估（不导致失败）：")
        for w in warns:
            print(f"  - {w}")

    if errors:
        print("\n[ERROR] 行数规则违规：")
        for e in errors:
            print(f"  - {e}")
        print("\n规则与豁免机制见 .agent/rules/file-length-rule.md")
        return 1

    print("\n行数规则检查通过。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
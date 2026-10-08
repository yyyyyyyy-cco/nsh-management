#!/usr/bin/env python3 -*- coding: utf-8 -*-
"""文件行数上限校验（CI repo-hygiene 与本地可跑）。

规则与豁免机制见权威源 `.agent/rules/file-length-rule.md`（§2.1 单一权威源，本文不复制）。
上限与分类必须与该文档表格保持一致；自检：`python scripts/check_file_length.py --self-test`。
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
    ("backend/scripts", "*.py", 200, "检查脚本"),
    ("scripts", "*.py", 200, "检查脚本"),
]

# 豁免清单行：`| \`path/to/file\` | 123 | ...`（含 `/` 才算文件路径，避免命中表头或说明行）
EXEMPTION_LINE = re.compile(r"^\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|")


def line_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").splitlines())


def parse_exemption_line(line: str) -> tuple[str, int] | None:
    """解析豁免清单表格的一行 → (相对路径, 登记行数)；非清单行返回 None。"""
    m = EXEMPTION_LINE.match(line)
    if m and "/" in m.group(1):
        return m.group(1).strip(), int(m.group(2))
    return None


def judge(
    rel: str,
    n: int,
    limit: int,
    label: str,
    *,
    has_marker: bool = False,
    listed: bool = False,
    registered: int | None = None,
    growth_warn: float = GROWTH_WARN,
) -> tuple[str | None, str | None]:
    """判定单个超限文件 → (错误, 警告)。未超限返回 (None, None)。纯函数。"""
    if n <= limit:
        return None, None
    if not has_marker:
        return f"{rel} 超限（{n} > {limit}，{label}）且未打「{MARKER}」标记", None
    if not listed:
        return f"{rel} 已打「{MARKER}」标记但未登记到规则豁免清单", None
    if registered and n >= registered * growth_warn:
        return (
            None,
            f"{rel} 登记行数 {registered} → 当前 {n}（+{(n / registered - 1) * 100:.0f}%），规则要求重新评估是否继续豁免",
        )
    return None, None


def parse_exemptions() -> dict[str, int]:
    """解析规则文档豁免清单表格中的 `文件 → 登记行数`。"""
    if not RULE_DOC.exists():
        print(f"[ERROR] 未找到规则文档：{RULE_DOC}")
        return {}
    out: dict[str, int] = {}
    for line in RULE_DOC.read_text(encoding="utf-8").splitlines():
        parsed = parse_exemption_line(line)
        if parsed:
            out[parsed[0]] = parsed[1]
    return out


SELF_TEST_CASES: tuple[tuple[tuple, tuple[str | None, str | None], str], ...] = (
    ((( "a.py", 300, 300, "服务文件（Python）"), {}), (None, None), "恰好等于上限 → 通过（边界不报）"),
    ((("a.py", 301, 300, "服务文件（Python）"), {"has_marker": False, "listed": False}), ("未打", None), "超限 + 无标记 → 报错"),
    ((("a.py", 301, 300, "服务文件（Python）"), {"has_marker": True, "listed": False}), ("未登记", None), "有标记但未登记 → 报错"),
    ((("a.py", 301, 300, "服务文件（Python）"), {"has_marker": True, "listed": True, "registered": 280}), (None, None), "已登记且增长 <20% → 通过"),
    ((("a.py", 340, 300, "服务文件（Python）"), {"has_marker": True, "listed": True, "registered": 280}), (None, "重新评估"), "增长 ≥20% → 警告（不失败）"),
)


def run_self_test() -> int:
    failed = 0
    for (args, kwargs), (want_err, want_warn), note in SELF_TEST_CASES:
        err, warn = judge(*args, **kwargs)
        ok = (err is None) == (want_err is None) and (warn is None) == (want_warn is None)
        if ok and want_err:
            ok = want_err in err
        if ok and want_warn:
            ok = want_warn in warn
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}｜err={err} warn={warn}")

    for line, expect, note in (
        ("| `frontend/src/a.vue` | 320 | 组件 |", ("frontend/src/a.vue", 320), "标准清单行 → 解析成功"),
        ("| 文件 | 行数 | 说明 |", None, "表头 → 不解析"),
        ("| `无斜杠说明` | 10 | x |", None, "无 `/` 的条目 → 不解析（避免命中说明表格）"),
        ("纯文本", None, "非表格行 → 不解析"),
    ):
        got = parse_exemption_line(line)
        ok = got == expect
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}｜got={got}")

    if not any(lbl == "检查脚本" for *_, lbl in LIMITS):
        failures.append("LIMITS 未包含「检查脚本」类别（scripts/*.py 未被扫描）")
    total = len(SELF_TEST_CASES) + 5
    print(f"自检：{total - failed}/{total} 通过")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

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
            err, warn = judge(
                rel, n, limit, label,
                has_marker=MARKER in head,
                listed=rel in exemptions,
                registered=exemptions.get(rel),
            )
            errors += [err] if err else []
            warns += [warn] if warn else []

    for rel in sorted(exemptions):
        if not (REPO / rel).exists():
            errors.append(f"豁免清单登记的文件不存在（清单悬空）：{rel}")

    print(f"检查文件数：{checked}（分类上限：{'、'.join(sorted({f'{limit}行' for _, _, limit, _ in LIMITS}))}）")
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
    raise SystemExit(main(sys.argv))

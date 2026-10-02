#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「发现已修复但判定未更新」检查（合规化计划 W4-16）。

**动机**：本会话累计 **5 处**过时判定（`6.2.1`/`6.2.5` 于 W4-10 更正，`13.3.2`/`16.3.2`/`16.4.1` 于 W4-15 更正），
共同点是**修复落地后没回头改判定单元格**。为它写规则靠人遵守就会再漏，故做成脚本。

**规则**（保守优先，宁可少报也不误报）：
1. 从整改计划 §4 取每个 `F-<n>` 行的处置状态——行内出现「修复」（且不含「未修复/待修复/不修复」）视为**已修复**；
2. 从 `security-review.md` 取 §17 的**判定行**（形如 `| 13.3.2 | 2 | 🟡 部分 | 证据 |`）；
3. **若判定行的证据里引用了某个「已修复」的 F 编号，而该判定不是 ✅** → 报告。

**为什么这样定**：`F-53` 是「**部分修复**」（管理端仍可设定口令，属取舍），其行内**不含「修复」字样的完整语义**，
因此不会被判为已修复，对应的 🟡 判定也不会被误报；`F-49` 收窄为「仅前端」，其处置不含「修复」→ 同样不误报。

用法：
    python scripts/check_verdict_sync.py                    # 报告模式（始终 exit 0）
    python scripts/check_verdict_sync.py --strict           # 有发现即 exit 1（供门禁使用）
    python scripts/check_verdict_sync.py --self-test        # 内置样例自检
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / ".agent" / "plans" / "compliance-remediation-plan.md"
REVIEW = ROOT / "memory-bank" / "security-review.md"

F_ROW = re.compile(r"^\| \*{0,2}(F-\d+)\*{0,2} \|(.*)$", re.MULTILINE)
VERDICT_ROW = re.compile(r"^\| (\d+\.\d+\.\d+) \| ([123]) \| ([^|]+) \|(.*)\|$", re.MULTILINE)
F_REF = re.compile(r"\bF-\d+\b")
NOT_FIXED = re.compile(r"未修复|待修复|不修复")


def fixed_findings(plan_text: str) -> dict[str, str]:
    """返回 {F-id: 该行处置文本}，仅收录「已修复」的。"""
    out: dict[str, str] = {}
    for m in F_ROW.finditer(plan_text):
        fid, rest = m.group(1), m.group(2)
        if "修复" in rest and not NOT_FIXED.search(rest):
            out[fid] = rest.strip()  # **不截断**：豁免标记「（残留判定：…）」常在长行末尾，截断会让它消失（本轮实测 bug）
    return out


# 计划行里的显式豁免：`（残留判定：6.2.4、6.2.12）` —— 该发现已修复，但这些条目因其未做部分而本就是 🟡/❌
EXEMPT = re.compile(r"残留判定：([^）|]+)")


def exemptions(residual_text: str) -> set[str]:
    """从「残留判定：」列表解析条目编号集合。"""
    out: set[str] = set()
    for m in EXEMPT.finditer(residual_text):
        out |= {x.strip() for x in re.split(r"[、,，\s]+", m.group(1)) if x.strip()}
    return out


def analyze(plan_text: str, review_text: str) -> list[str]:
    """返回问题列表（纯函数：自检、实跑、历史版本验证共用）。"""
    fixed = fixed_findings(plan_text)
    exempt_by_fid = {fid: exemptions(text) for fid, text in fixed.items()}
    problems: list[str] = []
    for m in VERDICT_ROW.finditer(review_text):
        item, verdict, evidence = m.group(1), m.group(3).strip(), m.group(4)
        if verdict.startswith("✅"):
            continue
        for fid in set(F_REF.findall(evidence)):
            if fid in fixed and item not in exempt_by_fid.get(fid, set()):
                problems.append(
                    f"{item} 判定「{verdict}」，但证据引用的 {fid} 在计划中已标记修复 → 需重访该判定行"
                )
    return problems


SELF_TEST_CASES: tuple[tuple[str, str, bool, str], ...] = (
    ("| F-01 | 已完成 | **W1-1 ✅（2026-10-02 已修复）** |", "| 1.1.1 | 1 | 🟡 部分 | 见 F-01 |", False, "已修复 + 非 ✅ → 应报"),
    ("| F-01 | 已完成 | **W1-1 ✅（2026-10-02 已修复）** |", "| 1.1.1 | 1 | ✅ 满足 | 见 F-01 |", True, "已修复 + ✅ → 不报"),
    ("| F-01 | 已完成 | 任务 W1-1（Docker 验证） |", "| 1.1.1 | 1 | 🟡 部分 | 见 F-01 |", True, "未修复 + 非 ✅ → 不报"),
    ("| F-01 | 已完成 | W1-1 🔄（部分修复） |", "| 1.1.1 | 1 | 🟡 部分 | 见 F-01 |", False, "含「部分修复」仍算修复 + 🟡 → 应报"),
    ("| F-01 | 已完成 | 待修复 |", "| 1.1.1 | 1 | ❌ 未满足 | 见 F-01 |", True, "「待修复」不算已修复 → 不报"),
    ("| F-01 | 已完成 | **W1-1 ✅（2026-10-02 已修复）** |", "| 1.1.1 | 1 | ❌ 未满足 | 无编号引用 |", True, "无 F 引用 → 不报"),
    ("| F-01 | 已完成 | **W1-1 ✅（2026-10-02 已修复）** |", "| 1.1.1 | 1 | ❌ 未满足 | 见 F-99 |", True, "引用未修复的 F-99 → 不报"),
    ("| F-01 | 已完成 | **W1-1 ✅（已修复；残留判定：1.1.1）** |", "| 1.1.1 | 1 | ❌ 未满足 | 见 F-01 |", True, "在「残留判定」豁免名单内 → 不报"),
    ("| F-01 | 已完成 | **W1-1 ✅（已修复；残留判定：1.1.1）** |", "| 1.1.2 | 1 | 🟡 部分 | 见 F-01 |", False, "同发现但不在豁免名单内 → 仍报"),
    (
        "| F-01 | 已完成 | " + "x" * 100 + "**W1-1 ✅（已修复；残留判定：1.1.1）** |",
        "| 1.1.1 | 1 | ❌ 未满足 | 见 F-01 |",
        True,
        "豁免标记位于 80 字符之外（曾因截断而失效）→ 不报",
    ),
)
# 注：第 4 条与「F-53 部分修复」的真实语义不同——计划里 F-53 的处置文本是「🔄（自助改密已实现；…仍为取舍）」，
# 其中不含「修复」二字，故不会被判为已修复。这里显式覆盖「含『部分修复』」的情形以保证规则可预期。


def run_self_test() -> int:
    failed = 0
    for plan_text, review_text, should_pass, note in SELF_TEST_CASES:
        problems = analyze(plan_text, review_text)
        ok = (not problems) == should_pass
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}｜发现={problems[:1]}")
    total = len(SELF_TEST_CASES)
    print(f"自检：{total - failed}/{total} 通过")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    problems = analyze(PLAN.read_text(encoding="utf-8"), REVIEW.read_text(encoding="utf-8"))
    if problems:
        print(f"[verdict-sync] 发现 {len(problems)} 处「已修复但判定未更新」：")
        for item in problems:
            print(f"  - {item}")
        print("[verdict-sync] 处置：重访这些判定行（或修正计划的修复状态），规则见 ai-checklist 第 54 条")
        return 1 if "--strict" in argv else 0
    print("[verdict-sync] 未发现「已修复但判定未更新」的问题 : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
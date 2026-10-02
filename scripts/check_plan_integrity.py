"""整改计划结构完整性门禁（`.agent/plans/compliance-remediation-plan.md`）。

**为什么需要**：计划文档是本仓库合规工作的**唯一路线权威**，但它由多轮增量编辑而成——
本轮之前的真实事故：给 §5 新增了任务 `W4-9` 却**忘了加 §7 进度行**，直到记录脚本的锚点报错才发现；
同类风险还有 F 编号笔误、§5/§7 任务不一致、行内状态词写错。

**检查项**（全部对文档本身解析，不做语义判断）：
1. **唯一性**：§4 的 F 编号、§5 的任务编号、§7 的进度编号各自不得重复；
2. **覆盖一致**：§5 的每个任务必须**恰好**有一条 §7 进度行；§7 的每条进度也必须在 §5 有对应任务；
3. **引用有效（计划内）**：§5/§7 行内出现的 `F-<数字>` 必须在 §4 中定义（防笔误）；
4. **状态词合法**：§7 每条进度行必须含 ✅/🔄/⏳/⛔ 之一（或 `—`），否则视为格式漂移；
5. **引用有效（记录内）**：`memory-bank/architecture.md` 与 `memory-bank/progress.md` 的变更记录里
   出现的 `F-<数字>` 也必须在 §4 有定义。

   第 5 条只认**计划自己的补零编号**（`两位及以上数字`）：`security-review.md` 另有 `F-1`…`F-5` 体系，
   其记录中的引用（如「security-review §十 F-1～F-5」）不属本门禁范围，故豁免。

   第 5 条是 2026-10-03 新增：此前事故——我在"更正越界修改"时以旧版本重建了计划文件，
   **误删了 F-114 行**，而本门禁当时只查计划内引用 ✗，**没有告警** ✗；
   记录文件里仍写着 `F-114` 却已无定义，正是该条要拦的情况。

用法：
    python scripts/check_plan_integrity.py                # 校验（含记录文件）
    python scripts/check_plan_integrity.py --self-test    # 内置样例自检（不读文件）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / ".agent" / "plans" / "compliance-remediation-plan.md"
RECORD_FILES = (
    ROOT / "memory-bank" / "architecture.md",
    ROOT / "memory-bank" / "progress.md",
)

# §5 任务行：`| W1-7 | 动作… |`（首格是纯编号）
TASK_ROW = re.compile(r"^\| \*{0,2}(W\d+-\d+)\*{0,2} \| ", re.MULTILINE)
# §7 进度行：`| W1-7 名称… |`（首格是「编号 空格 名称」）
PROGRESS_ROW = re.compile(r"^\| \*{0,2}(W\d+-\d+)\*{0,2} (?!\|)", re.MULTILINE)
FINDING_ROW = re.compile(r"^\| \*{0,2}(F-\d+)\*{0,2}\s*\| ", re.MULTILINE)
F_REF = re.compile(r"\bF-\d+\b")
# 记录内引用只按**计划的补零格式**判定（F-01…F-114）；`F-1`/`F-5` 属 security-review.md 自己的编号体系，应豁免
F_REF_PLAN = re.compile(r"\bF-\d{2,}\b")
# 历史记录中的**废止编号**豁免（按 AGENTS §3.4 不回改历史行；新增豁免必须写明来由）
LEGACY_REFS = {("progress.md", "F-15")}  # F-15 已不在 §4（编号调整），原记录保留不改
STATUS_MARKS = ("✅", "🔄", "⏳", "⛔")
PROGRESS_LINE = re.compile(r"^\| W\d+-\d+ (?!\|).*$", re.MULTILINE)

def duplicates(items: list[str]) -> list[str]:
    seen: set[str] = set()
    dups: set[str] = set()
    for item in items:
        if item in seen:
            dups.add(item)
        seen.add(item)
    return sorted(dups)

def record_ref_problems(defined: set[str], records: tuple[tuple[str, str], ...]) -> list[str]:
    """记录文件里的 `F-<数字>` 必须都在 §4 定义。纯函数，便于自检。"""
    problems: list[str] = []
    for name, text in records:
        for line_no, line in enumerate(text.splitlines(), 1):
            for ref in F_REF_PLAN.findall(line):
                if ref not in defined and (name, ref) not in LEGACY_REFS:
                    problems.append(f"{name}:{line_no} 引用了 §4 未定义的发现：{ref}")
    return problems

def analyze(text: str, records: tuple[tuple[str, str], ...] = ()) -> list[str]:
    """返回问题列表（空 = 通过）。自检与实跑共用本函数。"""
    problems: list[str] = []
    tasks = TASK_ROW.findall(text)
    progress = PROGRESS_ROW.findall(text)
    findings = FINDING_ROW.findall(text)

    for label, ids in (("§4 发现编号", findings), ("§5 任务编号", tasks), ("§7 进度编号", progress)):
        dups = duplicates(ids)
        if dups:
            problems.append(f"{label} 重复：{', '.join(dups)}")

    missing_progress = sorted(set(tasks) - set(progress))
    if missing_progress:
        problems.append(f"§5 有任务但 §7 无进度行：{', '.join(missing_progress)}")
    orphan_progress = sorted(set(progress) - set(tasks))
    if orphan_progress:
        problems.append(f"§7 有进度行但 §5 无任务：{', '.join(orphan_progress)}")

    defined = set(findings)
    # 作用域**刻意只含** | W / | F- 开头的行：2026-10-03 实测把范围放宽到全部行时，
    # §2 的规范表（如 `v1.2`、`PEP 621` 等文本）会产生**假阳性** ✗，故保持收窄。
    for line in text.splitlines():
        if not (line.startswith("| W") or line.startswith("| F-")):
            continue
        own_id = re.sub(r"\*", "", line.split("|")[1]).strip()
        for ref in F_REF.findall(line):
            if ref not in defined and ref != own_id:
                problems.append(f"引用了 §4 未定义的发现：{ref}（出现在：{line[:60]}…）")

    # 2026-10-03 新增：记录文件中的 F 引用同样必须在 §4 定义
    problems.extend(record_ref_problems(defined, records))

    for line in PROGRESS_LINE.findall(text):
        if not any(mark in line for mark in STATUS_MARKS):
            problems.append(f"§7 进度行缺少状态标记（{'/'.join(STATUS_MARKS)}）：{line[:60]}…")
    dup = duplicate_section_numbers(text)
    if dup:
        problems.append(f"顶层章节号重复：{'、'.join(dup)}（计划结构要求编号唯一且单调）")

    # 汇总行必须与表体一致（F-108：汇总行长期无人校验 ✗）
    SUMMARY_ROW = re.search(r"完成 \*\*(\d+)/(\d+)\*\*（([\d.]+)%）；未完成 \*\*(\d+)\*\*；其它 \*\*(\d+)\*\*", text)
    if SUMMARY_ROW:
        cells = [ln.strip().strip("|").split("|")[1].strip()
                 for ln in text.split("\n")
                 if re.match(r"^\| \*{0,2}W\d+-\d+\*{0,2} (?!\|)", ln)]
        d = sum(1 for c in cells if c.startswith("✅"))
        p = sum(1 for c in cells if c.startswith(("⏳", "🔄")))
        want = (d, len(cells), p, len(cells) - d - p)
        got = tuple(int(x) for x in (SUMMARY_ROW.group(1), SUMMARY_ROW.group(2), SUMMARY_ROW.group(4), SUMMARY_ROW.group(5)))
        if got != want:
            problems.append(f"§7 汇总行与表体不一致：汇总 {got}（完成/总数/未完成/其它），实测 {want}")

    return problems

SELF_TEST_CASES: tuple[tuple[str, bool, str], ...] = (
    # (样例文本, 是否应通过, 说明),
    # 新增（2026-10-03）：章节编号唯一性
    ("## 9. 风险\n## 9. 验收\n", False, "顶层章节号重复应报错"),
    ("## 9. 风险\n## 10. 验收\n", True, "编号唯一且单调应通过"),
    ("| F-01 | x |\n| W1-1 | a |\n| W1-1 名称 | ✅ 已完成 |\n| W1-2 | b |\n| W1-2 名称 | ⏳ 待开始 |\n", True, "正常：任务与进度一一对应"),
    ("| W1-1 | a |\n", False, "§5 有任务但 §7 无进度行"),
    ("| W1-1 名称 | ✅ 已完成 |\n", False, "§7 有进度但 §5 无任务"),
    ("| W1-1 | a |\n| W1-1 名称 | ✅ |\n| W1-1 | b |\n", False, "§5 任务编号重复"),
    ("| W1-1 | a |\n| W1-1 名称 | 已完成 |\n", False, "§7 缺状态标记（无 ✅/🔄/⏳/⛔）"),
    ("| F-01 | x |\n| W1-1 | 见 F-99 |\n| W1-1 名称 | ✅ |\n", False, "引用了未定义的 F-99"),
    ("| F-01 | x |\n| W1-1 | 见 F-01 |\n| W1-1 名称 | ✅ |\n", True, "引用已定义的 F-01"),
    ("| **F-01** | x |\n| W1-1 | 见 F-01 |\n| W1-1 名称 | ✅ |\n", True, "§4 编号加粗（真实计划里的写法）"),
    # 新增（2026-10-03）：记录文件中的 F 引用
    ("| F-01 | x |\n| W1-1 | a |\n| W1-1 名称 | ✅ |\n", False, "记录引用未定义 F-99（记录内引用校验）"),
    ("| F-01 | x |\n| W1-1 | a |\n| W1-1 名称 | ✅ |\n", True, "记录引用已定义 F-01（记录内引用校验）"),
    ("| F-01 | x |\n| W1-1 | a |\n| W1-1 名称 | ✅ |\n", True, "记录引用 F-1/F-5（他文档编号）应豁免"),
    ("| **F-15** | x |\n| W1-1 | a |\n| W1-1 名称 | ✅ |\n", True, "§4 行写作 |**F-15**| 也应被识别（空格容忍）"),
)

def run_self_test() -> int:
    failures = 0
    for idx, (text, should_pass, note) in enumerate(SELF_TEST_CASES):
        if "记录引用" in note:
            if "空格容忍" in note:
                records = ()
            elif "豁免" in note:
                records = (("records.md", "批注：见 F-1 与 F-5（security-review §十）"),)
            elif "空格容忍" in note:
                records = ()
            else:
                records = (("records.md", "批注：见 F-01"),)
            bad = "未定义" in note
            records = (("records.md", "批注：见 F-99" if bad else "批注：见 F-01"),)
        else:
            records = ()
        problems = analyze(text, records)
        ok = (not problems) == should_pass
        failures += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}｜期望通过={should_pass}，问题={problems[:1]}")
    total = len(SELF_TEST_CASES)
    print(f"自检：{total - failures}/{total} 通过")
    return 1 if failures else 0

def duplicate_section_numbers(text: str) -> list[str]:
    """返回重复的顶层章节号（如同时存在两个 `## 9.`）——纯函数，便于自检。"""
    nums = re.findall(r"^## (\d+)\.", text, re.MULTILINE)
    return sorted({n for n in nums if nums.count(n) > 1})

def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    text = PLAN.read_text(encoding="utf-8")
    records = tuple((p.name, p.read_text(encoding="utf-8")) for p in RECORD_FILES if p.exists())
    problems = analyze(text, records)
    tasks = TASK_ROW.findall(text)
    progress = PROGRESS_ROW.findall(text)
    findings = FINDING_ROW.findall(text)
    print(f"[plan] 发现 {len(findings)} 条 / 任务 {len(tasks)} 条 / 进度 {len(progress)} 条"
          f"；记录文件 {len(records)} 个（其 F 引用亦校验）")
    if problems:
        print("[plan] 结构问题：")
        for item in problems:
            print(f"  - {item}")
        return 1
    print("[plan] 结构一致性 : PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
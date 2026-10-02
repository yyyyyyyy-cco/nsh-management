#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""文档「数字/版本」一致性门禁（AGENTS §3.3 第 5 条「版本号 / 数量一致性」的固化）。

**为什么需要**：该自检项此前只靠人工 `grep`。本项目已有教训——「靠人工核对必漏」（ai-checklist 第 34 条），
且第 32 轮实测发现「门禁只写在 CI 里等于本地没有门禁」。本轮普查确实抓到一处当前态旧值
（`tech-stack.md` 摘要行仍写 Python 3.13，而同文件正文已按代码事实写 3.11）。

**检查三类事实**（真值来自仓库内的**代码**，不来自任何文档）：
1. **表数量**：实际 = `backend/app/models/*.py` 中 `__tablename__` 的个数；
   文档声明 = 各文档 `当前态` 行里 `N 张表` 的说法——**全部声明必须彼此一致且等于实际值**；
2. **Alembic 迁移数**：实际 = `backend/alembic/versions/*.py` 文件个数；文档 `N 个 Alembic 迁移` 同样口径；
3. **`database-design.md` 版本号**：真值 = 该文档自身声明的 `vX.Y`；其他文档凡在同一行提到
   `database-design` 又出现 `vX.Y` 的，必须与之一致。

**历史行排除**：更新记录表格行以日期开头（`| 2026-…`），属时间戳证据（AGENTS §3.4），不参与判定。

用法：
    python scripts/check_doc_numbers.py                # 校验
    python scripts/check_doc_numbers.py --self-test    # 内置样例自检
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / "backend" / "app" / "models"
VERSIONS_DIR = ROOT / "backend" / "alembic" / "versions"
DB_DESIGN = ROOT / "memory-bank" / "database-design.md"

# 参与「当前态」判定的文档（memory-bank 下全部 md + 根文档）
DOC_GLOBS = ("*.md", "memory-bank/*.md", "backend/docs/*.md", "frontend/docs/*.md", ".agent/plans/*.md")

HISTORY_LINE = re.compile(r"^\s*\|?\s*20\d\d-\d\d-\d\d")  # 更新记录行（日期开头）
TABLE_CLAIM = re.compile(r"(\d+)\s*张表")
MIGRATION_CLAIM = re.compile(r"(\d+)\s*个\s*Alembic\s*迁移|(\d+)\s*个迁移")
DB_VERSION_IN_SELF = re.compile(r"版本[^\n]{0,20}?(v\d+\.\d+)")
DB_VERSION_CLAIM = re.compile(r"database-design[^\n]{0,60}?(v\d+\.\d+)")


def real_table_count() -> int:
    total = 0
    for path in sorted(MODELS_DIR.glob("*.py")):
        total += len(re.findall(r'__tablename__\s*=', path.read_text(encoding="utf-8")))
    return total


def real_migration_count() -> int:
    return len([p for p in VERSIONS_DIR.glob("*.py") if p.name != "__init__.py"])


def current_lines() -> list[tuple[str, int, str]]:
    out: list[tuple[str, int, str]] = []
    for pattern in DOC_GLOBS:
        for path in sorted(ROOT.glob(pattern)):
            if not path.is_file():
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
                if HISTORY_LINE.match(line):
                    continue
                out.append((path.relative_to(ROOT).as_posix(), i, line))
    return out


def analyze(lines: list[tuple[str, int, str]], tables: int, migrations: int, db_version: str | None) -> list[str]:
    """返回问题列表（自检与实跑共用）。"""
    problems: list[str] = []
    table_claims = [(f, i, int(m.group(1))) for f, i, line in lines for m in [TABLE_CLAIM.search(line)] if m]
    for f, i, value in table_claims:
        if value != tables:
            problems.append(f"{f}:{i} 声明「{value} 张表」，实际模型表数 {tables}")
    distinct = {v for _, _, v in table_claims}
    if len(distinct) > 1:
        problems.append(f"「N 张表」的声明彼此不一致：{sorted(distinct)}")

    migration_claims = []
    for f, i, line in lines:
        m = MIGRATION_CLAIM.search(line)
        if m:
            migration_claims.append((f, i, int(m.group(1) or m.group(2))))
    for f, i, value in migration_claims:
        if value != migrations:
            problems.append(f"{f}:{i} 声明「{value} 个 Alembic 迁移」，实际迁移文件 {migrations}")
    distinct_m = {v for _, _, v in migration_claims}
    if len(distinct_m) > 1:
        problems.append(f"「N 个迁移」的声明彼此不一致：{sorted(distinct_m)}")

    if db_version:
        for f, i, line in lines:
            for claim in DB_VERSION_CLAIM.findall(line):
                if claim != db_version:
                    problems.append(f"{f}:{i} 引用 database-design {claim}，实际为 {db_version}")
    return problems


SELF_TEST_CASES: tuple[tuple[tuple, bool, str], ...] = (
    ((([("a.md", 1, "共 12 张表")], 12, 15, None),), True, "声明与真值一致 → 通过"),
    ((([("a.md", 1, "共 11 张表")], 12, 15, None),), False, "表数不符 → 报错"),
    ((([("a.md", 1, "共 12 张表"), ("b.md", 2, "共 13 张表")], 12, 15, None),), False, "彼此不一致 → 报错"),
    ((([("a.md", 1, "15 个 Alembic 迁移")], 12, 15, None),), True, "迁移数一致 → 通过"),
    ((([("a.md", 1, "14 个 Alembic 迁移")], 12, 15, None),), False, "迁移数不符 → 报错"),
    ((([("a.md", 1, "见 database-design.md v1.8")], 12, 15, "v1.9"),), False, "版本引用过期 → 报错"),
    ((([("a.md", 1, "见 database-design.md v1.9")], 12, 15, "v1.9"),), True, "版本引用一致 → 通过"),
    ((([("a.md", 1, "9 表迁移的历史记录")], 12, 15, None),), True, "无「N 张表」说法 → 不判定"),
)


def run_self_test() -> int:
    failed = 0
    for (args,), should_pass, note in SELF_TEST_CASES:
        problems = analyze(*args)
        ok = (not problems) == should_pass
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}｜问题={problems[:1]}")
    total = len(SELF_TEST_CASES)
    print(f"自检：{total - failed}/{total} 通过")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    tables, migrations = real_table_count(), real_migration_count()
    db_text = DB_DESIGN.read_text(encoding="utf-8") if DB_DESIGN.exists() else ""
    found = DB_VERSION_IN_SELF.search(db_text.split("## ")[0] if "## " in db_text else db_text)
    db_version = found.group(1) if found else None
    if not db_version:
        m = re.search(r"v\d+\.\d+", db_text[:2000])
        db_version = m.group(0) if m else None

    lines = current_lines()
    problems = analyze(lines, tables, migrations, db_version)
    print(f"[doc-numbers] 真值：模型表数 {tables}、迁移文件 {migrations}、database-design {db_version or '未识别'}")
    print(f"[doc-numbers] 扫描当前态行 {len(lines)} 行（已排除日期开头的更新记录行）")
    if problems:
        print("[doc-numbers] 不一致：")
        for item in problems:
            print(f"  - {item}")
        return 1
    print("[doc-numbers] 文档数字/版本一致性 : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
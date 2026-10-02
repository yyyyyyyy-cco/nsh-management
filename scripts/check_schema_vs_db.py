#!/usr/bin/env python
"""数据库权威源 ↔ **真实迁移产物** 字段对账（报告型，默认不失败）。

这是 `W2-15` 的实质：`memory-bank/database-design.md` §2.x 是表结构权威源 ✓，
而"**Alembic 空库升级到 head 之后真实生成的表结构**"才是它最终的解释 ✓ ——
`check_schema_drift.py` 比对的是「文档 ↔ SQLAlchemy 模型」，本脚本比对「**文档 ↔ 真实数据库**」，
两者互补：模型对了但迁移漏了列（或迁移里多出未文档化的列）只有本脚本能发现 ✗。

做法：把 `DATABASE_URL` 指向**临时 SQLite 文件**，在 `backend/` 下执行 `alembic upgrade head`，
再用 `PRAGMA table_info` 读真实列，与文档逐表逐列比对。

约定：
- **报告型**：默认 exit 0；`--strict` 存在任一方向不一致则 exit 1。
- 跳过 `alembic_version`（迁移元数据表，不属业务表）。
- 不修改仓库内任何数据库文件（全部在临时目录）✓。
"""
from __future__ import annotations

import argparse
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from check_schema_drift import parse_doc  # noqa: E402  （复用文档解析器，避免两套解析）

DOC = ROOT / "memory-bank" / "database-design.md"
SKIP_TABLES = {"alembic_version"}


def compare_columns(doc_cols: list[str], db_cols: list[str]) -> tuple[list[str], list[str]]:
    """返回 (文档有库里没有, 库里有文档没有)。"""
    d, b = set(doc_cols), set(db_cols)
    return sorted(d - b), sorted(b - d)


def compare_tables(doc: dict[str, list[str]], db: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    """返回 (仅文档有, 仅库里有) —— 排除跳过表。"""
    d, b = set(doc), set(db) - SKIP_TABLES
    return sorted(d - b), sorted(b - d)


def build_and_read(keep: bool = False) -> dict[str, list[str]]:
    """临时库升级到 head，返回 {表名: [列名]}。"""
    tmpdir = tempfile.mkdtemp(prefix="schema-vs-db-")
    db_path = pathlib.Path(tmpdir) / "probe.db"
    url = f"sqlite+aiosqlite:///{db_path.as_posix()}"
    env = dict(os.environ, DATABASE_URL=url)
    r = subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                       cwd=str(BACKEND), env=env, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise RuntimeError(f"alembic upgrade head 失败（exit={r.returncode}）：\n{(r.stderr or '')[-1500:]}")
    if not db_path.exists():
        raise RuntimeError(f"迁移未生成预期数据库文件：{db_path}")
    conn = sqlite3.connect(str(db_path))
    try:
        tables = [row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        out: dict[str, list[str]] = {}
        for t in tables:
            if t in SKIP_TABLES or t.startswith("sqlite_"):
                continue
            cols = [row[1] for row in conn.execute(f'PRAGMA table_info("{t}")')]
            out[t] = cols
    finally:
        conn.close()
    if not keep:
        try:
            db_path.unlink()
            pathlib.Path(tmpdir).rmdir()
        except OSError:
            pass
    return out


# ---------------- 自检（纯函数，不依赖 alembic） ----------------
def self_test() -> int:
    failures = []
    # 1) 完全一致
    if compare_columns(["id", "name"], ["name", "id"]) != ([], []):
        failures.append("一致时应无差异")
    # 2) 库里有、文档没有（迁移多出列）——最危险：权威源漏记
    if compare_columns(["id"], ["id", "extra"]) != ([], ["extra"]):
        failures.append("未检出「库里有、文档没有」")
    # 3) 文档有、库里没有（迁移漏列）
    if compare_columns(["id", "ghost"], ["id"]) != (["ghost"], []):
        failures.append("未检出「文档有、库里没有」")
    # 4) 表集合：仅文档有 / 仅库里有；alembic_version 必须被跳过
    doc = {"a": ["id"], "doc_only": ["id"]}
    db = {"a": ["id"], "db_only": ["id"], "alembic_version": ["version_num"]}
    if compare_tables(doc, db) != (["doc_only"], ["db_only"]):
        failures.append(f"表集合比对异常：{compare_tables(doc, db)}")
    # 5) 跳过表的**真实形态**：文档从不列它，DB 侧出现时必须被排除（契约：仅在 DB 侧排除）
    if compare_tables({"a": ["id"]}, {"a": ["id"], "alembic_version": ["x"]}) != ([], []):
        failures.append("alembic_version 未在 DB 侧被正确跳过")
    # 5b) 反向：文档侧出现该表名时按普通表处理（本检查宁多报不漏报）
    if compare_tables({"alembic_version": ["v"], "a": ["id"]}, {"a": ["id"]}) != (["alembic_version"], []):
        failures.append("文档侧出现 alembic_version 时的行为与契约不符")

    total = 6
    if failures:
        print("[schema-vs-db] 自检失败：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"[schema-vs-db] 自检：{total}/{total} 通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    doc = parse_doc(DOC.read_text(encoding="utf-8"))
    try:
        db = build_and_read()
    except Exception as exc:  # 迁移只在真实运行时才可能失败
        print(f"[schema-vs-db] 无法构建迁移产物：{exc}")
        return 2 if args.strict else 0

    only_doc_t, only_db_t = compare_tables(doc, db)
    rows = []
    for t in sorted(set(doc) & set(db)):
        od, ob = compare_columns(doc[t], db[t])
        rows.append((t, od, ob))
    drift = [r for r in rows if r[1] or r[2]]

    print(f"[schema-vs-db] 文档 {len(doc)} 张表；迁移产物 {len(db)} 张表；共同 {len(rows)} 张")
    if only_doc_t:
        print(f"[schema-vs-db] **仅文档有（迁移未建该表）**：{only_doc_t}")
    if only_db_t:
        print(f"[schema-vs-db] **仅库里有（未文档化的表）**：{only_db_t}")
    for t, od, ob in drift:
        if od:
            print(f"  - {t}：**文档有、库里没有（迁移漏列？）** -> {od}")
        if ob:
            print(f"  - {t}：**库里有、文档没有（权威源漏记？）** -> {ob}")
    if not drift and not only_doc_t and not only_db_t:
        print("[schema-vs-db] 迁移产物与权威源逐表逐列一致 : PASS")
    bad = bool(drift or only_doc_t or only_db_t)
    return 1 if (args.strict and bad) else 0


if __name__ == "__main__":
    sys.exit(main())
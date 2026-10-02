#!/usr/bin/env python
"""数据库权威源 ↔ SQLAlchemy 模型 字段对账（报告型，默认不失败）。

用途：把 `memory-bank/database-design.md` §2.x 各表的字段表（权威源）与
`backend/app/models/*.py` 的 `__tablename__` + `mapped_column` 列进行比对，
发现两个方向的不一致：
- **模型有、文档缺**：权威源漏记列（历史教训 F-72 就是这一类 ✗）
- **文档有、模型缺**：文档写了实现里没有的列 ✗

约定：
- **报告型**：默认始终 exit 0；`--strict` 存在任一方向不一致则 exit 1。
- 模型侧**只统计 `= mapped_column(...)`**：`guild: Mapped[...] = relationship(...)` 是关系属性，不是列（否则会假报 ✗）。
- 行式解析（见 ai-checklist 第 102/103 条：跨行正则容易吞掉换行与缩进）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC = ROOT / "memory-bank" / "database-design.md"
MODELS = ROOT / "backend" / "app" / "models"


def parse_doc(text: str) -> dict[str, list[str]]:
    """解析 `### 2.N <table> — ...` 小节里的字段表（第一格为字段名）。"""
    out: dict[str, list[str]] = {}
    table = None
    for line in text.split("\n"):
        h = re.match(r"^###\s*2\.\d+\s+`?([a-z_][a-z0-9_]*)`?\s*[—-]", line)
        if h:
            table = h.group(1)
            out.setdefault(table, [])
            continue
        if line.startswith("### ") or line.startswith("## "):
            table = None
            continue
        if table is None or not line.startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in line.strip().strip("|").split("|")]
        if not cells:
            continue
        first = cells[0]
        if not first or first in ("字段", "------") or set(first) <= {"-", " "}:
            continue
        if re.fullmatch(r"[a-z_][a-z0-9_]*", first):
            out[table].append(first)
    return {k: v for k, v in out.items() if v}


def parse_models(dirpath: pathlib.Path) -> dict[str, list[str]]:
    """解析模型：`__tablename__ = "x"` 与 `name: Mapped[...] = mapped_column(...)`（行式）。"""
    out: dict[str, list[str]] = {}
    for p in sorted(dirpath.glob("*.py")):
        table: str | None = None
        cols: list[str] = []

        def flush() -> None:
            if table:
                out[table] = cols[:]

        for line in p.read_text(encoding="utf-8").split("\n"):
            # 类边界：收束上一张表（支持一个文件多张表——自检构造的最脆形状）
            if re.match(r"class\s+\w+", line):
                flush()
                table, cols = None, []
                continue
            tm = re.match(r'\s*__tablename__\s*=\s*"([^"]+)"', line)
            if tm:
                flush()
                table, cols = tm.group(1), []
                continue
            cm = re.match(r"\s{4}([a-z_][a-z0-9_]*)\s*:\s*Mapped\[", line)
            if cm and "mapped_column(" in line:
                cols.append(cm.group(1))
        flush()
    return out


def analyze(doc: dict[str, list[str]], models: dict[str, list[str]]) -> list[tuple[str, list[str], list[str]]]:
    """返回 [(表名, 模型有文档缺, 文档有模型缺)]（只比共同存在的表，缺表另报）。"""
    rows = []
    for table in sorted(set(doc) & set(models)):
        d, m = set(doc[table]), set(models[table])
        rows.append((table, sorted(m - d), sorted(d - m)))
    return rows


def tables_only_in_one(doc: dict[str, list[str]], models: dict[str, list[str]]) -> tuple[list[str], list[str]]:
    return sorted(set(models) - set(doc)), sorted(set(doc) - set(models))


# ---------------- 自检 ----------------
SELFTEST_DOC = """
### 2.1 demo — 演示表

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK | 主键 |
| name | TEXT | NOT NULL | 名称 |

索引：`name`。

### 2.2 other — 另一表

| 字段 | 类型 |
|------|------|
| id | INTEGER |
| ghost | TEXT |
"""
SELFTEST_MODELS = '''
class Demo(Base):
    __tablename__ = "demo"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32))
    extra: Mapped[str | None] = mapped_column(String(32), nullable=True)
    rel: Mapped[list["X"]] = relationship(back_populates="demo")


class Only(Base):
    __tablename__ = "model_only"

    id: Mapped[int] = mapped_column(primary_key=True)
'''


def self_test() -> int:
    import tempfile

    failures = []
    doc = parse_doc(SELFTEST_DOC)
    # 1) 文档解析：表名与字段
    if doc.get("demo") != ["id", "name"]:
        failures.append(f"文档解析异常：{doc.get('demo')}")
    if doc.get("other") != ["id", "ghost"]:
        failures.append(f"文档解析异常（第二表）：{doc.get('other')}")
    # 2) 模型解析：关系属性不算列
    with tempfile.TemporaryDirectory() as td:
        tp = pathlib.Path(td)
        (tp / "demo.py").write_text(SELFTEST_MODELS, encoding="utf-8")
        models = parse_models(tp)
    if models.get("demo") != ["id", "name", "extra"]:
        failures.append(f"模型解析异常（关系属性应被排除）：{models.get('demo')}")
    # 3) 双向漂移检出
    rows = {t: (a, b) for t, a, b in analyze(doc, models)}
    if rows.get("demo") != (["extra"], []):
        failures.append(f"模型有文档缺未检出：{rows.get('demo')}")
    if rows.get("other") != ([], ["ghost"]):
        failures.append(f"文档有模型缺未检出：{rows.get('other')}")
    # 4) 只在一侧存在的表
    mo, do = tables_only_in_one(doc, models)
    if mo != ["model_only"] or do:
        failures.append(f"单侧表检出异常：model_only={mo} doc_only={do}")
    # 5) 一致时不误报
    rows2 = {t: (a, b) for t, a, b in analyze({"x": ["id"]}, {"x": ["id"]})}
    if rows2.get("x") != ([], []):
        failures.append(f"误报：{rows2.get('x')}")

    total = 5
    if failures:
        print("[schema-drift] 自检失败：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"[schema-drift] 自检：{total}/{total} 通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    doc = parse_doc(DOC.read_text(encoding="utf-8"))
    models = parse_models(MODELS)
    rows = analyze(doc, models)
    model_only, doc_only = tables_only_in_one(doc, models)
    drift = [r for r in rows if r[1] or r[2]]

    print(f"[schema-drift] 文档解析到 {len(doc)} 张表；模型解析到 {len(models)} 张表；共同 {len(rows)} 张")
    if model_only:
        print(f"[schema-drift] **仅模型有（权威源缺整张表）**：{model_only}")
    if doc_only:
        print(f"[schema-drift] **仅文档有（实现里没有这张表）**：{doc_only}")
    for table, only_model, only_doc in drift:
        if only_model:
            print(f"  - {table}：**模型有、文档缺** -> {only_model}")
        if only_doc:
            print(f"  - {table}：**文档有、模型缺** -> {only_doc}")
    if not drift and not model_only and not doc_only:
        print("[schema-drift] 字段与表完全一致 : PASS")
    return 1 if (args.strict and (drift or model_only or doc_only)) else 0


if __name__ == "__main__":
    sys.exit(main())
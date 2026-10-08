#!/usr/bin/env python
"""空值契约核对（报告型，默认不失败）——从 `check_type_drift.py` 拆出的独立关注点。

发现「**后端可空但前端既非 `null` 又非可选**」的字段：UI 收到 null 会崩。
默认 exit 0；`--strict` 存在风险时 exit 1。配对表见 `_pairs.py`（与漂移/请求侧共用）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from _pairs import PAIRS

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_TYPES = ROOT / "frontend" / "src" / "types"
BE_SCHEMAS = ROOT / "backend" / "app" / "schemas"


def ts_fields_with_nullable(text: str) -> dict[str, dict[str, dict]]:
    """{接口: {字段: {"optional": bool, "nullable": bool}}}（TS 侧）"""
    out: dict[str, dict[str, dict]] = {}
    for m in re.finditer(r"export interface (\w+)\s*(?:extends\s+[\w,\s]+)?\{([^}]*)\}", text):
        name, body = m.group(1), m.group(2)
        fields: dict[str, dict] = {}
        for line in body.split("\n"):
            s = line.strip()
            if not s or s.startswith(("//", "/*", "*")):
                continue
            fm = re.match(r"([A-Za-z_]\w*)(\??)\s*:\s*(.+?)\s*$", s)
            if not fm:
                continue
            fields[fm.group(1)] = {"optional": fm.group(2) == "?", "nullable": "null" in fm.group(3)}
        out[name] = fields
    return out


def py_nullable(text: str) -> dict[str, dict[str, bool]]:
    """{模型: {字段: 是否可空}}（`X | None` / `Optional[X]`；行式）"""
    out: dict[str, dict[str, bool]] = {}
    cur, fields = None, {}
    for line in text.split("\n"):
        m = re.match(r"class (\w+)\s*\(", line)
        if m:
            if cur:
                out[cur] = fields
            cur, fields = m.group(1), {}
            continue
        if cur is None:
            continue
        if line and not line.startswith((" ", "\t")):
            out[cur] = fields
            cur, fields = None, {}
            continue
        fm = re.match(r"\s{4}([a-z_]\w*)\s*:\s*(.+)", line)
        if fm:
            fields[fm.group(1)] = bool(re.search(r"\|\s*None|Optional\[", fm.group(2)))
    if cur:
        out[cur] = fields
    return out


def nullability_risks(fe_nullable: dict[str, dict[str, dict]], be_null: dict[str, dict[str, bool]],
                      pairs: dict[str, list[str]] | None = None) -> list[tuple[str, str, str]]:
    """返回 [(接口, 字段, 说明)]：**后端可空但前端既非 null 又非可选**（UI 收到 null 会崩）。"""
    risks = []
    for fe_name, be_names in sorted((pairs if pairs is not None else PAIRS).items()):
        if fe_name not in fe_nullable:
            continue
        for fname, info in fe_nullable[fe_name].items():
            for n in be_names:
                if n in be_null and fname in be_null[n]:
                    if be_null[n][fname] and not info["nullable"] and not info["optional"]:
                        risks.append((fe_name, fname, f"后端 {n} 可空，前端非 null 且非可选"))
                    break
    return risks


def _load() -> tuple[dict[str, dict[str, dict]], dict[str, dict[str, bool]]]:
    fe: dict[str, dict[str, dict]] = {}
    for p in sorted(FE_TYPES.glob("*.ts")):
        fe.update(ts_fields_with_nullable(p.read_text(encoding="utf-8")))
    be: dict[str, dict[str, bool]] = {}
    for p in sorted(BE_SCHEMAS.glob("*.py")):
        be.update(py_nullable(p.read_text(encoding="utf-8")))
    return fe, be


def self_test_cases() -> list[str]:
    """供本模块 CLI 与 check_type_drift 聚合调用；返回失败说明列表（空 = 通过）。"""
    failures: list[str] = []
    r6 = nullability_risks({"A": {"x": {"optional": False, "nullable": False}}}, {"M": {"x": True}}, {"A": ["M"]})
    if r6 != [("A", "x", "后端 M 可空，前端非 null 且非可选")]:
        failures.append(f"空值风险未检出：{r6}")
    if nullability_risks({"A": {"x": {"optional": False, "nullable": True}}}, {"M": {"x": True}}, {"A": ["M"]}):
        failures.append("前端 nullable 被误报")
    if nullability_risks({"A": {"x": {"optional": True, "nullable": False}}}, {"M": {"x": True}}, {"A": ["M"]}):
        failures.append("前端 optional 被误报")
    return failures


CASE_COUNT = 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="存在空值契约风险时 exit 1")
    args = ap.parse_args()
    if args.self_test:
        failures = self_test_cases()
        if failures:
            print("[nullability] 自检失败：")
            for f in failures:
                print(f"  - {f}")
            return 1
        # F-111：前端侧失效配对告警（与后端侧对称）
        fe_stale = [k for k in PAIRS if k not in fe]
        if fe_stale:
            print(f"[类型对账] 配对表中的前端类型不存在（FE 失效配对）：{fe_stale}")
        print(f"[nullability] 自检：{CASE_COUNT}/{CASE_COUNT} 通过")
        return 0
    fe, be = _load()
    risks = nullability_risks(fe, be)
    print(f"[nullability] 空值契约：**后端可空但前端非空** {len(risks)} 条")
    for fe_name, fname, why in risks:
        print(f"  - {fe_name}.{fname}：{why}")
    return 1 if (args.strict and risks) else 0


if __name__ == "__main__":
    sys.exit(main())
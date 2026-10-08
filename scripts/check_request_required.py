#!/usr/bin/env python
"""请求侧必填核对（报告型，默认不失败）——从 `check_type_drift.py` 拆出的独立关注点。

发现「**后端必填但前端标了 `?`**」的字段：前端可漏传 -> 运行时 422。
默认 exit 0；`--strict` 存在风险时 exit 1。配对表见 `_pairs.py`（与漂移/空值侧共用）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

from _pairs import PAIRS_REQ

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_TYPES = ROOT / "frontend" / "src" / "types"
BE_SCHEMAS = ROOT / "backend" / "app" / "schemas"


def py_required(text: str) -> dict[str, dict[str, bool]]:
    """{模型: {字段: 是否必填}}。

    必填判定（**修正版**）：无 `=` 默认值，或默认值是 `Field(..., ...)`（可跨行）。
    首版脚本用 `"Field(...)" in typ` 判断 ✗ —— `Field(...,` 不含完整 `Field(...)` ✗，
    会把必填字段误判为可选（见 ai-checklist 第 111 条 ①）。
    """
    out: dict[str, dict[str, bool]] = {}
    cur: str | None = None
    fields: dict[str, bool] = {}
    pending: str | None = None  # 跨行的 Field(...) 续行
    for line in text.split("\n"):
        cm = re.match(r"class (\w+)\s*\(", line)
        if cm:
            if cur:
                out[cur] = fields
            cur, fields, pending = cm.group(1), {}, None
            continue
        if cur is None:
            continue
        if line and not line.startswith((" ", "\t")):
            out[cur] = fields
            cur, fields, pending = None, {}, None
            continue
        fm = re.match(r"\s{4}([a-z_]\w*)\s*:\s*(.+)", line)
        if fm:
            name, typ = fm.group(1), fm.group(2)
            if "=" not in typ:
                fields[name] = True
            elif re.search(r"=\s*Field\(\s*\.\.\.", typ):  # search 而非 match：typ 以类型名开头，match 会锚定失败
                fields[name] = True
            else:
                fields[name] = False
            pending = name if (typ.rstrip().endswith(("Field(", ",")) or typ.count("(") > typ.count(")")) else None
            continue
        if pending and re.match(r"\s{4,}", line) and "..." in line:
            fields[pending] = True
            pending = None
    if cur:
        out[cur] = fields
    return out


def ts_optional(text: str) -> dict[str, dict[str, bool]]:
    """{接口: {字段: 是否带 `?`}}"""
    out: dict[str, dict[str, bool]] = {}
    for m2 in re.finditer(r"export interface (\w+)\s*(?:extends\s+[\w,\s]+)?\{([^}]*)\}", text):
        name, body = m2.group(1), m2.group(2)
        fields: dict[str, bool] = {}
        for line in body.split("\n"):
            s = line.strip()
            if not s or s.startswith(("//", "/*", "*")):
                continue
            fm = re.match(r"([A-Za-z_]\w*)(\??)\s*:", s)
            if fm:
                fields[fm.group(1)] = fm.group(2) == "?"
        out[name] = fields
    return out


def required_risks(fe_opt: dict[str, dict[str, bool]], be_req: dict[str, dict[str, bool]],
                   pairs: dict[str, list[str]] | None = None) -> list[tuple[str, str, str]]:
    """返回 [(前端接口, 字段, 说明)]：**后端必填但前端标了 `?`**（前端可漏传 -> 422）。"""
    risks = []
    for fe_name, be_names in sorted((pairs if pairs is not None else PAIRS_REQ).items()):
        if fe_name not in fe_opt:
            continue
        for fname, optional in fe_opt[fe_name].items():
            for n in be_names:
                if n in be_req and fname in be_req[n]:
                    if be_req[n][fname] and optional:
                        risks.append((fe_name, fname, f"后端 {n} 必填，前端标为可选"))
                    break
    return risks


def _load() -> tuple[dict[str, dict[str, bool]], dict[str, dict[str, bool]]]:
    fe: dict[str, dict[str, bool]] = {}
    for p in sorted(FE_TYPES.glob("*.ts")):
        fe.update(ts_optional(p.read_text(encoding="utf-8")))
    be: dict[str, dict[str, bool]] = {}
    for p in sorted(BE_SCHEMAS.glob("*.py")):
        be.update(py_required(p.read_text(encoding="utf-8")))
    return fe, be


SELFTEST_PY = 'class M(BaseModel):\n    a: str = Field(..., min_length=1)\n    b: str | None = None\n    c: int\n'


def self_test_cases() -> list[str]:
    """供本模块 CLI 与 check_type_drift 聚合调用；返回失败说明列表（空 = 通过）。"""
    failures: list[str] = []
    req = py_required(SELFTEST_PY)
    if req.get("M") != {"a": True, "b": False, "c": True}:
        failures.append(f"必填判定异常（Field(..., 应判必填）：{req.get('M')}")
    r8 = required_risks({"A": {"a": True}}, req, {"A": ["M"]})
    if r8 != [("A", "a", "后端 M 必填，前端标为可选")]:
        failures.append(f"请求侧风险未检出：{r8}")
    if required_risks({"A": {"a": False}}, req, {"A": ["M"]}):
        failures.append("请求侧无反例失败")
    return failures


CASE_COUNT = 3


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="存在请求侧必填风险时 exit 1")
    args = ap.parse_args()
    if args.self_test:
        failures = self_test_cases()
        if failures:
            print("[request-required] 自检失败：")
            for f in failures:
                print(f"  - {f}")
            return 1
        # F-111：前端侧失效配对告警（与后端侧对称）
        fe_stale = [k for k in PAIRS_REQ if k not in fe]
        if fe_stale:
            print(f"[类型对账] 配对表中的前端类型不存在（FE 失效配对）：{fe_stale}")
        print(f"[request-required] 自检：{CASE_COUNT}/{CASE_COUNT} 通过")
        return 0
    fe, be = _load()
    risks = required_risks(fe, be)
    print(f"[request-required] 请求侧必填：**后端必填但前端可选** {len(risks)} 条")
    for fe_name, fname, why in risks:
        print(f"  - {fe_name}.{fname}：{why}")
    return 1 if (args.strict and risks) else 0


if __name__ == "__main__":
    sys.exit(main())
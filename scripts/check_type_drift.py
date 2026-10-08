#!/usr/bin/env python
"""前后端字段一致性核对（报告型，默认不失败）——按关注点拆分后的**主入口**。

职责收窄为「字段漂移」（前端声明了、后端输出模型不提供）；空值契约与请求侧必填已拆到
`check_nullability.py` / `check_request_required.py`（可单独运行），共用配对表见 `_pairs.py`。
本文件保留原输出格式与前缀，并**聚合**两个子模块的自检用例。
约定：报告型（默认 exit 0；`--strict` 存在漂移或任一子风险时 exit 1）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

import check_nullability
import check_request_required
from _pairs import PAIRS

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_TYPES = ROOT / "frontend" / "src" / "types"
BE_SCHEMAS = ROOT / "backend" / "app" / "schemas"


def parse_ts_interfaces(text: str) -> dict[str, list[str]]:
    """解析 `export interface X { ... }`（单行字段，忽略注释行）。"""
    out: dict[str, list[str]] = {}
    for m in re.finditer(r"export interface (\w+)\s*(?:extends\s+[\w,\s]+)?\{([^}]*)\}", text):
        name, body = m.group(1), m.group(2)
        fields = []
        for line in body.split("\n"):
            s = line.strip()
            if not s or s.startswith(("//", "/*", "*")):
                continue
            fm = re.match(r"([A-Za-z_]\w*)\??\s*:", s)
            if fm:
                fields.append(fm.group(1))
        out[name] = fields
    return out


def parse_py_models(text: str) -> dict[str, tuple[list[str], list[str]]]:
    """行式解析 Pydantic 模型 -> {类名: (直接字段, 基类)}；行式可保证首个字段不被漏掉。"""
    out: dict[str, tuple[list[str], list[str]]] = {}
    cur: str | None = None
    fields: list[str] = []
    bases: list[str] = []

    def flush() -> None:
        if cur:
            out[cur] = (fields[:], bases[:])

    for line in text.split("\n"):
        m = re.match(r"class (\w+)\s*\(([^)]*)\)\s*:", line)
        if m:
            flush()
            cur = m.group(1)
            fields = []
            bases = [b.strip() for b in m.group(2).split(",")
                     if b.strip() and b.strip() not in ("BaseModel", "object")]
            continue
        if cur is None:
            continue
        if line and not line.startswith((" ", "\t")):  # 类外，收尾
            flush()
            cur = None
            continue
        fm = re.match(r"\s{4}([a-z_]\w*)\s*:", line)
        if fm:
            fields.append(fm.group(1))
    flush()
    return out


def resolve(model: str, models: dict[str, tuple[list[str], list[str]]], seen: set[str] | None = None) -> set[str]:
    seen = seen if seen is not None else set()
    if model in seen or model not in models:
        return set()
    seen.add(model)
    fields, bases = models[model]
    out = {f for f in fields}
    for b in bases:
        out |= resolve(b, models, seen)
    return out


def analyze(fe_types: dict[str, list[str]], be_models: dict[str, tuple[list[str], list[str]]],
            pairs: dict[str, list[str]] | None = None) -> list[tuple[str, list[str], list[str]]]:
    """返回 [(前端接口名, 仅前端有的字段, 仅后端有的字段)]"""
    result = []
    for fe_name, be_names in sorted((pairs if pairs is not None else PAIRS).items()):
        if fe_name not in fe_types:
            continue
        be_fields: set[str] = set()
        found = False
        for n in be_names:
            if n in be_models:
                found = True
                be_fields |= resolve(n, be_models)
        if not found:
            continue
        fe_fields = fe_types[fe_name]
        only_fe = [f for f in fe_fields if f not in be_fields]
        only_be = sorted(f for f in be_fields - set(fe_fields) if not f.startswith("_"))
        result.append((fe_name, only_fe, only_be))
    return result


def _load() -> tuple[dict[str, list[str]], dict[str, tuple[list[str], list[str]]]]:
    fe: dict[str, list[str]] = {}
    for p in sorted(FE_TYPES.glob("*.ts")):
        fe.update(parse_ts_interfaces(p.read_text(encoding="utf-8")))
    be: dict[str, tuple[list[str], list[str]]] = {}
    for p in sorted(BE_SCHEMAS.glob("*.py")):
        be.update(parse_py_models(p.read_text(encoding="utf-8")))
    return fe, be


SELFTEST_PY = 'class Parent(BaseModel):\n    id: int\n\n\nclass ChildOut(Parent):\n    name: str\n    remark: str | None = None\n'
SELFTEST_TS = 'export interface Child {\n  id: number\n  name: string\n}\nexport interface Kid {\n  id: number\n  ghost: string\n}\n'


def self_test() -> int:
    """5 项漂移用例 + 聚合两个子模块用例（空值 3 / 请求 3）。"""
    failures: list[str] = []
    models = parse_py_models(SELFTEST_PY)
    checks = [
        (models.get("ChildOut", ([], []))[0] == ["name", "remark"], f"首个字段解析异常：{models.get('ChildOut')}"),
        (resolve("ChildOut", models) == {"id", "name", "remark"}, f"继承解析异常：{resolve('ChildOut', models)}"),
        (parse_ts_interfaces(SELFTEST_TS).get("Child") == ["id", "name"], "TS 解析异常"),
    ]
    for ok, msg in checks:
        if not ok:
            failures.append(msg)
    fe = dict(parse_ts_interfaces(SELFTEST_TS))
    test_pairs = {"Child": ["ChildOut"], "Kid": ["ChildOut"]}
    rows = {(n, tuple(only_fe)) for n, only_fe, _ in analyze(fe, models, test_pairs)}
    if ("Kid", ("ghost",)) not in rows:
        failures.append(f"漂移检出异常：{rows}")
    if ("Child", ()) not in rows:
        failures.append(f"误报：{rows}")
    failures += [f"（空值契约）{f}" for f in check_nullability.self_test_cases()]
    failures += [f"（请求侧必填）{f}" for f in check_request_required.self_test_cases()]
    total = 5 + check_nullability.CASE_COUNT + check_request_required.CASE_COUNT
    if failures:
        print("[type-drift] 自检失败：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"[type-drift] 自检：{total}/{total} 通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="存在「仅前端有」的漂移时 exit 1")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    fe, be = _load()
    fe_stale = [k for k in PAIRS if k not in fe]
    if fe_stale:
        print(f"[类型对账] 配对表中的前端类型不存在（FE 失效配对）：{fe_stale}")
    stale = [f"{k}->{n}" for k, names in PAIRS.items() for n in names if n not in be]
    if stale:
        print(f"[type-drift] 配对表指向不存在的后端模型：{stale}")

    rows = analyze(fe, be)
    drift = [(n, only_fe) for n, only_fe, _ in rows if only_fe]

    fe_null, be_null = check_nullability._load()
    null_risks = check_nullability.nullability_risks(fe_null, be_null)
    print(f"[type-drift] 空值契约：**后端可空但前端非空** {len(null_risks)} 条")

    fe_opt, be_req = check_request_required._load()
    req_risks = check_request_required.required_risks(fe_opt, be_req)
    print(f"[type-drift] 请求侧必填：**后端必填但前端可选** {len(req_risks)} 条")
    for fe_name, fname, why in req_risks:
        print(f"  - {fe_name}.{fname}：{why}")
    for fe_name, fname, why in null_risks:
        print(f"  - {fe_name}.{fname}：{why}")
    print(f"[type-drift] 已核对 {len(rows)} 对前后端模型（前端接口 {len(fe)} 个 / 后端模型 {len(be)} 个）")
    for name, only_fe, only_be in rows:
        if only_fe:
            print(f"  - {name}：**仅前端有** -> {only_fe}")
    if not drift:
        print("[type-drift] 未发现「前端声明但后端不提供」的字段 : PASS")
    return 1 if (args.strict and (drift or null_risks or req_risks)) else 0


if __name__ == "__main__":
    sys.exit(main())
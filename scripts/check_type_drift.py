#!/usr/bin/env python
"""前后端字段一致性核对（报告型，默认不失败）。

用途：把 `frontend/src/types/*.ts` 的 interface 字段与后端 **Pydantic 模型（含继承链）** 的字段对账，
发现「前端声明了、后端输出模型不提供」的字段（最危险：读空值）以及「后端提供、前端未声明」的字段
（可能只是暂未使用，仅提示）。

约定：
- **报告型**：默认始终 exit 0；加 `--strict` 时存在「仅前端有」的漂移则 exit 1。
- 配对表 `PAIRS` 为**人工维护**：前端接口名 → 后端模型名候选（可多选，取并集）。
- 行式解析（按行取 `    field:`），**不用跨行正则**——2026-10-03 首版曾因 `):\\s*` 吃掉换行与缩进，
  导致**每个类的第一个字段**永远解析不到、把 `id` 全部误报为漂移（见 ai-checklist 第 102 条）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_TYPES = ROOT / "frontend" / "src" / "types"
BE_SCHEMAS = ROOT / "backend" / "app" / "schemas"

# 前端接口名 → 后端 Pydantic 模型名（取并集；人工维护）
PAIRS: dict[str, list[str]] = {
    "MemberInfo": ["MemberOut"],
    "AttendanceRecord": ["AttendanceRecordOut"],
    "LineupInfo": ["LineupOut"],
    "LineupSlot": ["LineupSlot"],
    "LineupTeam": ["LineupTeam"],
    "ScheduleInfo": ["ScheduleOut"],
    "Recording": ["RecordingOut"],
    "MatchData": ["MatchDataOut"],
    "ProfessionConfig": ["ProfessionConfigOut"],
    "Account": ["AccountOut"],
    "Guild": ["GuildOut"],
    "OperationLog": ["OperationLogOut"],
    "GameIdRequestItem": ["GameIdRequestMemberOut"],
    "UserInfo": ["UserOut"],
    "LogStats": ["LogStatsOut"],
    "WeeklyErrorItem": ["WeeklyErrorItem"],
}


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
    """行式解析 Pydantic 模型：返回 {类名: (直接字段, 基类)}。

    行式解析保证**第一个字段**不会被漏掉（首版跨行正则的教训）。
    """
    out: dict[str, tuple[list[str], list[str]]] = {}
    lines = text.split("\n")
    cur: str | None = None
    fields: list[str] = []
    bases: list[str] = []

    def flush() -> None:
        if cur:
            out[cur] = (fields[:], bases[:])

    for line in lines:
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


# ---------------- 自检 ----------------
SELFTEST_PY = '''
class Parent(BaseModel):
    id: int


class ChildOut(Parent):
    name: str
    remark: str | None = None
'''
SELFTEST_TS = '''
export interface Child {
  id: number
  name: string
}
export interface Kid {
  id: number
  ghost: string
}
'''


def self_test() -> int:
    failures = []
    models = parse_py_models(SELFTEST_PY)
    # 1) 第一个字段必须被解析到（首版 bug 的回归）
    if models.get("ChildOut", ([], []))[0] != ["name", "remark"]:
        failures.append(f"首个字段解析异常：{models.get('ChildOut')}")
    # 2) 继承解析
    if resolve("ChildOut", models) != {"id", "name", "remark"}:
        failures.append(f"继承解析异常：{resolve('ChildOut', models)}")
    # 3) TS 解析（含可选 ?）
    ts = parse_ts_interfaces(SELFTEST_TS)
    if ts.get("Child") != ["id", "name"]:
        failures.append(f"TS 解析异常：{ts.get('Child')}")
    # 4) 漂移检出：Kid.ghost 后端没有
    fe = dict(ts)
    test_pairs = {"Child": ["ChildOut"], "Kid": ["ChildOut"]}
    res = {(n, tuple(only_fe)) for n, only_fe, _ in analyze(fe, models, test_pairs) if n == "Kid"}
    if res != {("Kid", ("ghost",))}:
        failures.append(f"漂移检出异常：{res}")
    # 5) 无漂移不误报
    res2 = {(n, tuple(only_fe)) for n, only_fe, _ in analyze(fe, models, test_pairs) if n == "Child"}
    if res2 != {("Child", ())}:
        failures.append(f"误报：{res2}")

    total = 5
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

    # 自检也要看 PAIRS 是否仍指向存在的模型
    fe, be = _load()
    stale = [f"{k}->{n}" for k, names in PAIRS.items() for n in names if n not in be]
    if stale:
        print(f"[type-drift] 配对表指向不存在的后端模型：{stale}")

    rows = analyze(fe, be)
    drift = [(n, only_fe) for n, only_fe, _ in rows if only_fe]
    print(f"[type-drift] 已核对 {len(rows)} 对前后端模型（前端接口 {len(fe)} 个 / 后端模型 {len(be)} 个）")
    for name, only_fe, only_be in rows:
        if only_fe:
            print(f"  - {name}：**仅前端有** -> {only_fe}")
    if not drift:
        print("[type-drift] 未发现「前端声明但后端不提供」的字段 : PASS")
    return 1 if (args.strict and drift) else 0


if __name__ == "__main__":
    sys.exit(main())
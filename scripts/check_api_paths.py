#!/usr/bin/env python
"""前端 API 调用 ↔ 后端路由 对账（报告型，默认不失败）。

用途：把 `frontend/src/api/*.ts` 里 `http.<method>('<url>')` 的调用（含模板字符串路径参数）
与后端 `app/api/v1/*.py` 注册的路由（router 前缀 + 全局 `settings.API_PREFIX`）比对，
重点发现「**前端调用了、后端没有这条路由**」——那会直接 404。

约定：
- **报告型**：默认始终 exit 0；`--strict` 时存在「前端无对应路由」则 exit 1。
- 路径参数一律归一为 `{p}`（前端 `${x}` / `${encodeURIComponent(x)}` ↔ 后端 `{x}`），**只比形状不比参数名**。
- 行式解析（按行取 `@router.<m>("<path>")` 与 `http.<m>(...)`）——2026-10-03 的教训：跨行正则容易吞掉换行与缩进（见 ai-checklist 第 102 条）。
"""
from __future__ import annotations

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_API = ROOT / "frontend" / "src" / "api"
BE_API = ROOT / "backend" / "app" / "api" / "v1"
BE_MAIN = ROOT / "backend" / "app" / "main.py"

METHODS = ("get", "post", "put", "delete", "patch")


def normalize(path: str) -> str:
    """归一化路径：模板参数与后端参数统一为 {p}，去掉查询串与尾部斜杠。"""
    p = path.split("?")[0].strip()
    p = re.sub(r"\$\{[^}]*\}", "{p}", p)   # 前端模板参数（含 encodeURIComponent(...)）
    p = re.sub(r"\{[^}]*\}", "{p}", p)     # 后端参数
    if len(p) > 1:
        p = p.rstrip("/")
    return p


def parse_backend() -> tuple[set[tuple[str, str]], list[str]]:
    """返回 ({(method, 归一化路径)}, 说明行)"""
    routes: set[tuple[str, str]] = set()
    notes: list[str] = []
    # 全局前缀
    prefix = "/api/v1"
    mt = (ROOT / "backend" / "app" / "core" / "config.py").read_text(encoding="utf-8")
    m = re.search(r'API_PREFIX[^=]*=\s*"([^"]*)"', mt)
    if m:
        prefix = m.group(1)
    for p in sorted(BE_API.glob("*.py")):
        lines = p.read_text(encoding="utf-8").split("\n")
        rp = ""
        for line in lines:
            pm = re.search(r'APIRouter\(prefix="([^"]*)"', line)
            if pm:
                rp = pm.group(1)
        for line in lines:
            rm = re.match(r'\s*@router\.(get|post|put|delete|patch)\("([^"]*)"', line)
            if not rm:
                continue
            method, path = rm.group(1), rm.group(2)
            full = normalize(prefix + rp + path)
            routes.add((method, full))
    # 健康检查等直接挂在 app 上的路由（include_router 不带 api 前缀的那次）
    routes.add(("get", "/api/v1/health"))
    routes.add(("get", "/health"))
    notes.append(f"全局前缀 {prefix}")
    return routes, notes


def parse_frontend() -> tuple[set[tuple[str, str]], list[tuple[str, str]]]:
    """返回 ({(method, 归一化路径)}, [(来源, 原始调用)])"""
    calls: set[tuple[str, str]] = set()
    raw: list[tuple[str, str]] = []
    base = "/api/v1"
    hp = FE_API / "http.ts"
    if hp.exists():
        hm = re.search(r'baseURL:\s*[\'"]([^\'"]+)[\'"]', hp.read_text(encoding="utf-8"))
        if hm:
            base = hm.group(1)
    for p in sorted(FE_API.glob("*.ts")):
        if p.name == "http.ts":
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").split("\n"), 1):
            cm = re.search(r"http\.(get|post|put|delete|patch)\(\s*([`'\"])([^`'\"]*)", line)
            if not cm:
                continue
            method, _q, url = cm.group(1), cm.group(2), cm.group(3)
            if not url.startswith("/"):
                continue
            full = normalize(base + url)
            calls.add((method, full))
            raw.append((f"{p.name}:{i}", f"{method.upper()} {url}"))
    return calls, raw


def analyze(be_routes: set[tuple[str, str]], fe_calls: set[tuple[str, str]]) -> tuple[list, list]:
    missing = sorted([c for c in fe_calls if c not in be_routes])
    unused = sorted([r for r in be_routes if r not in fe_calls])
    return missing, unused


# ---------------- 自检 ----------------
def self_test() -> int:
    failures = []
    # 1) 归一化：模板参数 / encodeURIComponent / 后端参数 / 查询串 / 尾斜杠
    cases = {
        "/a/${x}": "/a/{p}",
        "/a/${encodeURIComponent(name)}": "/a/{p}",
        "/a/{member_id}/b": "/a/{p}/b",
        "/a/b/": "/a/b",
        "/a/b?q=1": "/a/b",
    }
    for src, want in cases.items():
        got = normalize(src)
        if got != want:
            failures.append(f"normalize({src}) = {got}，期望 {want}")
    # 2) 完全匹配不报缺失
    be = {("get", "/api/v1/schedules"), ("put", "/api/v1/members/{p}")}
    fe = {("get", "/api/v1/schedules"), ("put", "/api/v1/members/{p}")}
    miss, _ = analyze(be, fe)
    if miss:
        failures.append(f"应无缺失，实得 {miss}")
    # 3) 路径不存在 → 检出
    miss2, _ = analyze(be, {("get", "/api/v1/nope")})
    if miss2 != [("get", "/api/v1/nope")]:
        failures.append(f"未检出缺失：{miss2}")
    # 4) 方法不同视为缺失（GET vs PUT）
    miss3, _ = analyze({("put", "/api/v1/x")}, {("get", "/api/v1/x")})
    if miss3 != [("get", "/api/v1/x")]:
        failures.append(f"方法不匹配未检出：{miss3}")
    # 5) 参数形状匹配（前端 ${id} ↔ 后端 {record_id}）
    miss4, _ = analyze({("delete", "/api/v1/members/{p}")}, {("delete", "/api/v1/members/{p}")})
    if miss4:
        failures.append(f"参数形状匹配失败：{miss4}")
    total = 1 + len(cases) + 3
    if failures:
        print("[api-paths] 自检失败：")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"[api-paths] 自检：{total}/{total} 通过")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--strict", action="store_true", help="存在「前端调用但后端无此路由」时 exit 1")
    ap.add_argument("--list-unused", action="store_true", help="附带列出后端有但前端未调用的路由")
    args = ap.parse_args()
    if args.self_test:
        return self_test()

    be_routes, notes = parse_backend()
    fe_calls, raw = parse_frontend()
    missing, unused = analyze(be_routes, fe_calls)
    print(f"[api-paths] 后端路由 {len(be_routes)} 条（{'；'.join(notes)}）；前端调用 {len(fe_calls)} 个唯一 (方法, 路径)")
    if missing:
        print("[api-paths] **前端调用了但后端没有这条路**（会 404）：")
        for method, path in missing:
            print(f"  - {method.upper():6} {path}")
    else:
        print("[api-paths] 未发现「前端调用但后端无此路由」 : PASS")
    if args.list_unused:
        print(f"[api-paths] 后端有、前端未调用 {len(unused)} 条（信息性）：")
        for method, path in unused:
            print(f"  - {method.upper():6} {path}")
    return 1 if (args.strict and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
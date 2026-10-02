#!/usr/bin/env python
"""前端 API 调用 ↔ 后端路由 对账（报告型，默认不失败）。

把 `frontend/src/api/*.ts` 的 `http.<m>('<url>')` 与后端路由（router 前缀 + `main.py` 挂载前缀 +
`settings.API_PREFIX`）比对，重点发现「前端调用了、后端没有」的路由（会直接 404）。

约定：
- 报告型：默认 exit 0；`--strict` 时存在缺失则 exit 1。
- 路径参数统一归一为 `{p}`，只比形状不比参数名。
- 后端用 **AST** 解析（跨行装饰器 / `APIRouter(prefix=)` / `include_router(prefix=)` 均可正确取到，
  见 ai-checklist 第 102/120 条）；前端仍按行提取（TS 侧用 `http.<m>('...')` 形态稳定）。
"""
from __future__ import annotations

import argparse
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
FE_API = ROOT / "frontend" / "src" / "api"
BE_API = ROOT / "backend" / "app" / "api" / "v1"
BE_MAIN = ROOT / "backend" / "app" / "main.py"
METHODS = ("get", "post", "put", "delete", "patch")


def normalize(path: str) -> str:
    """归一化：模板参数与后端参数统一为 {p}，去掉查询串与尾部斜杠。"""
    p = re.sub(r"\$\{[^}]*\}", "{p}", path.split("?")[0].strip())  # 前端模板参数
    p = re.sub(r"\{[^}]*\}", "{p}", p)                             # 后端参数
    return p.rstrip("/") if len(p) > 1 else p


def routes_from_source(source: str) -> set[tuple[str, str]]:
    """从模块源码提取 {(方法, router 前缀 + 装饰器路径)}——纯函数，便于自检。"""
    prefixes: dict[str, str] = {"router": ""}
    routes: set[tuple[str, str]] = set()
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) \
                and getattr(node.value.func, "id", "") == "APIRouter":
            pre = ""
            for kw in node.value.keywords:
                if kw.arg == "prefix" and isinstance(kw.value, ast.Constant):
                    pre = str(kw.value.value)
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    prefixes[tgt.id] = pre
    for node in ast.walk(tree):
        if not isinstance(node, (ast.AsyncFunctionDef, ast.FunctionDef)):
            continue
        for dec in node.decorator_list:
            if not isinstance(dec, ast.Call) or not isinstance(dec.func, ast.Attribute):
                continue
            owner, method = getattr(dec.func.value, "id", ""), dec.func.attr
            if owner in prefixes and method in METHODS and dec.args \
                    and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str):
                routes.add((method, prefixes[owner] + dec.args[0].value))
    return routes


def mount_prefixes() -> dict[str, str]:
    """从 main.py 的 include_router 推导「模块名 -> 挂载前缀」（健康检查挂在 api 前缀之外）。"""
    out: dict[str, str] = {}
    if not BE_MAIN.exists():
        return out
    for node in ast.walk(ast.parse(BE_MAIN.read_text(encoding="utf-8"))):
        if isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "include_router":
            mod = getattr(node.args[0], "attr", "") if node.args else ""
            pre = ""
            for kw in node.keywords:
                if kw.arg == "prefix" and isinstance(kw.value, ast.Constant) and isinstance(kw.value.value, str):
                    pre = kw.value.value
            if mod:
                out[mod] = pre
    return out


def parse_backend() -> tuple[set[tuple[str, str]], list[str]]:
    """返回 ({(method, 归一化路径)}, 说明行)。"""
    prefix = "/api/v1"
    cfg = (ROOT / "backend" / "app" / "core" / "config.py").read_text(encoding="utf-8")
    m = re.search(r'API_PREFIX[^=]*=\s*"([^"]*)"', cfg)
    if m:
        prefix = m.group(1)
    mounts = mount_prefixes()
    routes: set[tuple[str, str]] = set()
    for p in sorted(BE_API.glob("*.py")):
        mod_routes = routes_from_source(p.read_text(encoding="utf-8"))
        for method, path in mod_routes:
            routes.add((method, normalize(prefix + path)))
            if p.stem in mounts:
                routes.add((method, normalize(mounts[p.stem] + path)))
    return routes, [f"全局前缀 {prefix}", f"main.py 挂载 {len(mounts)} 处"]


def parse_frontend() -> set[tuple[str, str]]:
    """返回 {(method, 归一化路径)}。"""
    calls: set[tuple[str, str]] = set()
    hp = FE_API / "http.ts"
    base = "/api/v1"
    if hp.exists():
        hm = re.search(r'baseURL:\s*[\'"]([^\'"]+)[\'"]', hp.read_text(encoding="utf-8"))
        if hm:
            base = hm.group(1)
    for p in sorted(FE_API.glob("*.ts")):
        if p.name == "http.ts":
            continue
        for line in p.read_text(encoding="utf-8").split("\n"):
            cm = re.search(r"http\.(get|post|put|delete|patch)\(\s*([`'\"])([^`'\"]*)", line)
            if cm and cm.group(3).startswith("/"):
                calls.add((cm.group(1), normalize(base + cm.group(3))))
    return calls


def analyze(be_routes: set[tuple[str, str]], fe_calls: set[tuple[str, str]]) -> tuple[list, list]:
    return (sorted([c for c in fe_calls if c not in be_routes]),
            sorted([r for r in be_routes if r not in fe_calls]))


def self_test() -> int:
    failures: list[str] = []
    for src, want in {"/a/${x}": "/a/{p}", "/a/${encodeURIComponent(n)}": "/a/{p}",
                      "/a/{member_id}/b": "/a/{p}/b", "/a/b/": "/a/b", "/a/b?q=1": "/a/b"}.items():
        if normalize(src) != want:
            failures.append(f"normalize({src}) = {normalize(src)}，期望 {want}")
    src = (
        "from fastapi import APIRouter\n"
        "r = APIRouter(prefix='/things')\n"
        "r2 = APIRouter()\n"
        "@r.get(\n    '/a/{x}',\n    response_model=dict,\n)\n"
        "async def a(x: int): ...\n"
        "@r.post('/b')\nasync def b(): ...\n"
        "@r2.get('/c')\nasync def c(): ...\n"
        "@r.websocket('/d')\nasync def d(): ...\n"
    )
    found = routes_from_source(src)
    want_found = {("get", "/things/a/{x}"), ("post", "/things/b"), ("get", "/c")}
    if found != want_found:
        failures.append(f"AST 提取不符：{sorted(found)}，期望 {sorted(want_found)}")
    be = {("get", "/api/v1/schedules"), ("put", "/api/v1/members/{p}")}
    miss, _ = analyze(be, set(be))
    if miss:
        failures.append(f"应无缺失，实得 {miss}")
    miss2, _ = analyze(be, {("get", "/api/v1/nope")})
    if miss2 != [("get", "/api/v1/nope")]:
        failures.append(f"未检出缺失：{miss2}")
    miss3, _ = analyze({("put", "/api/v1/x")}, {("get", "/api/v1/x")})
    if miss3 != [("get", "/api/v1/x")]:
        failures.append(f"方法不匹配未检出：{miss3}")
    total = 1 + 5 + 4
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
    fe_calls = parse_frontend()
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
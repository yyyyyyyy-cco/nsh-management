#!/usr/bin/env python
"""前端 API 调用 ↔ 后端路由 对账（报告型，默认不失败）。

比对 `frontend/src/api/*.ts` 的 `http.<m>('<url>')` 与后端路由，发现「前端调用了、后端没有」（会 404）。
后端**全用 AST 且不硬编码路由**（模块前缀 + `api/v1/router.py` 清单 + `main.py` 直挂前缀）；前端按行提取。
约定：默认 exit 0，`--strict` 有缺失则 exit 1；路径参数统一归一为 `{p}`，只比形状不比参数名。见 ai-checklist 第 102/120/121 条。
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
BE_SUBROUTER = BE_API / "router.py"
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


def _includes(path: pathlib.Path) -> list[tuple[str, str]]:
    """返回 [(模块名, 前缀表达式)]——支持 `x.router` 与 `x_router`；`prefix=` 缺省记 ""。"""
    out: list[tuple[str, str]] = []
    if not path.exists():
        return out
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
        if not (isinstance(node, ast.Call) and getattr(node.func, "attr", "") == "include_router"):
            continue
        arg = node.args[0] if node.args else None
        mod = ""
        if isinstance(arg, ast.Attribute):          # auth.router -> auth
            mod = getattr(arg.value, "id", "")
        elif isinstance(arg, ast.Name):             # health_router -> health_router
            mod = arg.id
        pre = ""
        for kw in node.keywords:
            if kw.arg == "prefix":
                try:
                    pre = ast.unparse(kw.value)
                except Exception:
                    pre = ""
        if mod:
            out.append((mod, pre))
    return out


def mounts() -> tuple[set[str], dict[str, set[str]], str]:
    """返回 (经 api_router 挂载的模块名, 直接挂在 app 上的模块->前缀集合, API_PREFIX 实际值)。"""
    cfg = (ROOT / "backend" / "app" / "core" / "config.py").read_text(encoding="utf-8")
    m = re.search(r'API_PREFIX[^=]*=\s*"([^"]*)"', cfg)
    prefix = m.group(1) if m else "/api/v1"
    included = {mod for mod, _ in _includes(BE_SUBROUTER)}
    direct: dict[str, set[str]] = {}
    for mod, raw in _includes(BE_MAIN):
        if mod == "api_router":
            continue
        pre = prefix if "API_PREFIX" in raw else raw.strip("'\"")
        for key in (mod, mod.removesuffix("_router")):
            direct.setdefault(key, set()).add(pre)
    return included, direct, prefix


def parse_backend() -> tuple[set[tuple[str, str]], list[str]]:
    """返回 ({(method, 归一化路径)}, 说明行)。"""
    included, direct, prefix = mounts()
    routes: set[tuple[str, str]] = set()
    for p in sorted(BE_API.glob("*.py")):
        mod_routes = routes_from_source(p.read_text(encoding="utf-8"))
        prefs: set[str] = set()
        if p.stem in included:
            prefs.add(prefix)
        prefs |= direct.get(p.stem, set())
        for pre in prefs or {""}:
            for method, path in mod_routes:
                routes.add((method, normalize(pre + path)))
    return routes, [f"前缀 {prefix}；api_router {len(included)} 模块；直挂 {len(direct)} 模块"]


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
        "@r.get(\n    '/a/{x}',\n    response_model=dict,\n)\nasync def a(x: int): ...\n"
        "@r.post('/b')\nasync def b(): ...\n"
        "@r2.get('/c')\nasync def c(): ...\n"
        "@r.websocket('/d')\nasync def d(): ...\n"
    )
    found = routes_from_source(src)
    want_found = {("get", "/things/a/{x}"), ("post", "/things/b"), ("get", "/c")}
    if found != want_found:
        failures.append(f"AST 提取不符：{sorted(found)}，期望 {sorted(want_found)}")
    be = {("get", "/api/v1/schedules"), ("put", "/api/v1/members/{p}")}
    if analyze(be, set(be))[0] or analyze(be, {("get", "/api/v1/nope")})[0] != [("get", "/api/v1/nope")] \
            or analyze({("put", "/api/v1/x")}, {("get", "/api/v1/x")})[0] != [("get", "/api/v1/x")]:
        failures.append("analyze 行为不符（应无缺失 / 应检出缺失 / 方法不匹配应检出）")
    total = 1 + 5 + 2
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
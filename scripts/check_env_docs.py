#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境变量文档完整性门禁（AGENTS §3.3 第 7 条「配置文件联动」的固化）。

背景：`backend/app/**` 通过 `os.getenv("KEY")` 读取 13 个环境变量，而 `.env.example` 只文档化了其中
6 个——**7 个键是「代码会读、但部署者不知道要配」**（DEBUG / DATABASE_URL / LOG_RETENTION_DAYS /
DEVELOPER_USERNAME / DEFAULT_GUILD_NAME / ADMIN_USERNAME / MEMBER_USERNAME）。人工核对漏过一次，
故固化为门禁；同类漂移以后再犯就会在 CI 直接失败。

规则：
- 代码中出现的 `os.getenv("KEY")` / `os.getenv('KEY')` 都必须在 `.env.example` 中有对应条目；
- `.env.example` 中「条目」= 行首（允许前置 `#` 注释）为 `KEY=` 或 `# KEY=`——即**注释掉的示例也算已文档化**
  （本项目 ALERT_* / CORS_ORIGINS 即此风格），因为它们同样告诉部署者该键的存在与含义；
- 反向检查（文档里有、代码里没用）只作**提示**，不算失败（可能是预留或给其它组件用）；
- 行内出现的 `APP_ENV=production` 之类的句子不会误判：条目必须**行首**以 KEY 开头。

用法：
    python scripts/check_env_docs.py                # 校验
    python scripts/check_env_docs.py --self-test    # 内置样例自检（不读文件）
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIR = ROOT / "backend" / "app"
ENV_FILE = ROOT / ".env.example"

GETENV = re.compile(r"os\.getenv\(\s*[\"']([A-Z][A-Z0-9_]*)[\"']")
DOC_ENTRY = re.compile(r"^\s*#?\s*([A-Z][A-Z0-9_]{2,})\s*=")


def keys_in_line(line: str) -> list[str]:
    """**生产与自检共用**的取键逻辑：注释不参与判定。

    为什么单独成函数：自检必须走与生产**相同的代码路径**——若自检直接调用裸正则，测的就是「另一个实现」。
    本门禁第一次提交即栽在这里：只改了 `code_keys`、自检仍用裸正则，于是自检 10/11 未过而生产已通过（CI 会红）。
    截断点选第一个 `#`：键名总在默认值之前，故不会截掉键名。
    """
    return GETENV.findall(line.split("#", 1)[0])


def code_keys(root: Path = SCAN_DIR) -> dict[str, set[str]]:
    """返回 {KEY: {相对路径:行号…}}。"""
    found: dict[str, set[str]] = {}
    for path in sorted(root.rglob("*.py")):
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            for key in keys_in_line(line):
                found.setdefault(key, set()).add(f"{path.relative_to(ROOT)}:{no}")
    return found


def documented_keys(env_file: Path = ENV_FILE) -> dict[str, int]:
    doc: dict[str, int] = {}
    for no, line in enumerate(env_file.read_text(encoding="utf-8").splitlines(), start=1):
        m = DOC_ENTRY.match(line)
        if m:
            doc.setdefault(m.group(1), no)
    return doc


SELF_TEST_CASES: tuple[tuple[str, str | None], ...] = (
    ('SECRET_KEY: str = os.getenv("SECRET_KEY", "x")', "SECRET_KEY"),
    ("DEBUG: bool = os.getenv('DEBUG', 'false') == 'true'", "DEBUG"),
    ("app_env = os.getenv(\"APP_ENV\", \"\").strip().lower()", "APP_ENV"),
    ("value: str = os.getenv(KEY_NAME)", None),  # 变量而非字面量：不参与判定
    ("# 注释里的 os.getenv(\"FAKE\") 不应被统计", None),
)
SELF_TEST_DOC: tuple[tuple[str, str | None], ...] = (
    ("SECRET_KEY=please-change-me", "SECRET_KEY"),
    ("# APP_ENV=production", "APP_ENV"),
    ("# 错误率告警（可选，2026-10-02 新增，合规化计划 W4-6）", None),
    ("# docker-compose.yml 已在 backend 服务固定 APP_ENV=production，此处无需重复设置；", None),
    ("    # ALERT_WEBHOOK_URL=https://hooks.example.com/nsh-alert", "ALERT_WEBHOOK_URL"),
    ("普通说明文字，没有键", None),
)


def run_self_test() -> int:
    failures = 0
    for line, expected in SELF_TEST_CASES:
        hits = keys_in_line(line)  # 与生产同一函数，避免「测另一个实现」
        actual = hits[0] if hits else None
        ok = actual == expected
        failures += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] getenv {line[:46]!r} 期望={expected!r} 实际={actual!r}")
    for line, expected in SELF_TEST_DOC:
        m = DOC_ENTRY.match(line)
        actual = m.group(1) if m else None
        ok = actual == expected
        failures += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] 文档 {line[:46]!r} 期望={expected!r} 实际={actual!r}")
    total = len(SELF_TEST_CASES) + len(SELF_TEST_DOC)
    print(f"自检：{total - failures}/{total} 通过")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    used = code_keys()
    doc = documented_keys()
    missing = {k: v for k, v in used.items() if k not in doc}
    extra = {k: v for k, v in doc.items() if k not in used}

    print(f"[env-docs] 代码读取 {len(used)} 个环境变量；.env.example 文档化 {len(doc)} 个")
    for key, where in sorted(extra.items()):
        print(f"[env-docs][提示] 文档中有 `{key}`（第 {where} 行），但代码未读取——确认是否预留")
    if missing:
        print("[env-docs] 以下变量**代码会读但未文档化**（部署者无从得知）：")
        for key, where in sorted(missing.items()):
            print(f"  {key}: {', '.join(sorted(where))}")
        return 1
    print("[env-docs] 全部环境变量均已文档化 : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
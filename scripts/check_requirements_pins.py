#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""依赖清单锁定门禁（合规化计划 W1-4）。

背景：`backend/requirements.txt` 曾对 `fastapi` 与 `python-multipart` 使用范围约束
（`>=0.115.0` / `>=0.0.18`），导致**全新环境静默漂移**——2026-10-02 实测一次干净安装
把 fastapi 解析到 0.142.2（项目开发期为 0.115.x，见合规化计划 F-15）。

规则：
- 运行时依赖必须**精确锁定**（`==`）；带范围标记（`>=` `<=` `~=` `!=` `>` `<` `*` `,`）即为违规；
- 允许 extras（`uvicorn[standard]==0.27.1`）与传递依赖显式锁定；
- 确有理由保留范围时，在该行注释中写 `# range-ok: <理由>` 显式豁免（便于审计）；
- 以 `#` 开头、空行、`-r/-c/--` 开头的行跳过；**行内注释中的范围符号不参与判定**
  （例如 `bcrypt==4.0.1  # passlib 1.7.4 与 bcrypt>=4.1 不兼容` 不误报）。

用法：
    python scripts/check_requirements_pins.py                # 校验默认清单
    python scripts/check_requirements_pins.py --self-test     # 自检内置样例（不读文件）
    python scripts/check_requirements_pins.py backend/requirements.txt ...
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FILES = ("backend/requirements.txt", "backend/requirements-dev.txt")
EXEMPT_MARKER = "# range-ok:"
INCLUDE_PREFIXES = ("-r ", "-c ", "--")
RANGE_TOKENS = (">=", "<=", "~=", "!=", ">", "<", "*", ",")


def check_line(line: str) -> str | None:
    """返回违规原因；`None` 表示该行合规（或无需判定）。"""
    code, _comment = line.partition("#")[0].strip(), line.partition("#")[2].strip()
    if not code or code.startswith(INCLUDE_PREFIXES):
        return None
    if EXEMPT_MARKER in line:
        return None
    if "==" not in code:
        return "未使用精确锁定（缺少 `==`）"
    body = code.replace("==", "")
    for token in RANGE_TOKENS:
        if token in body:
            return f"含范围标记 `{token}`（应改为精确 `==`，或加 `{EXEMPT_MARKER} <理由>` 豁免）"
    return None


SELF_TEST_CASES: tuple[tuple[str, str | None], ...] = (
    # (输入行, 期望结果)  —— 期望 None 表示合规
    ("fastapi==0.142.2", None),
    ("fastapi>=0.115.0", "未使用精确锁定（缺少 `==`）"),
    ("python-multipart>=0.0.18  # 修复 CVE-2024-53981 multipart DoS", "未使用精确锁定（缺少 `==`）"),
    ("bcrypt==4.0.1  # passlib 1.7.4 与 bcrypt>=4.1 不兼容", None),
    ("uvicorn[standard]==0.27.1", None),
    ("pillow==11.1.0  # range-ok: 上游仅提供范围约束", None),
    ("sqlalchemy==2.0.36,<3.0", "含范围标记 `<`（应改为精确 `==`，或加 `# range-ok: <理由>` 豁免）"),
    ("PyYAML", "未使用精确锁定（缺少 `==`）"),
    ("", None),
    ("# 纯注释行", None),
    ("-r requirements.txt", None),
    ("-c constraints.txt", None),
)


def run_self_test() -> int:
    failures = 0
    for line, expected in SELF_TEST_CASES:
        actual = check_line(line)
        ok = actual == expected
        status = "PASS" if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] 输入={line!r} 期望={expected!r} 实际={actual!r}")
    total = len(SELF_TEST_CASES)
    print(f"自检：{total - failures}/{total} 通过")
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    targets = [a for a in argv[1:] if not a.startswith("-")] or list(DEFAULT_FILES)
    violations: list[tuple[str, int, str, str]] = []
    for rel in targets:
        path = ROOT / rel
        if not path.exists():
            print(f"[错误] 清单不存在：{rel}", file=sys.stderr)
            return 2
        for no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            reason = check_line(line)
            if reason:
                violations.append((rel, no, line.strip(), reason))

    checked = sum(len((ROOT / r).read_text(encoding="utf-8").splitlines()) for r in targets)
    print(f"[deps-pin] 已检查 {len(targets)} 个清单 / {checked} 行")
    if violations:
        print("[deps-pin] 违规行：")
        for rel, no, line, reason in violations:
            print(f"  {rel}:{no}: {line}")
            print(f"      → {reason}")
        return 1
    print("[deps-pin] 全部依赖均已精确锁定 : PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
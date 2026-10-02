#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提交消息校验（规则权威源：`.agent/rules/git-commit-message.md`）。

用法：
    python scripts/check_commit_msg.py <commit-msg 文件>   # git commit-msg 钩子用法（钩子见 .githooks/commit-msg）
    python scripts/check_commit_msg.py --stdin             # 从标准输入读取消息（CI 逐个提交校验用）
    python scripts/check_commit_msg.py --self-test         # 运行内置用例自检
退出码：0 = 通过；1 = 违规（打印具体原因）

校验项：
1. 首行为 `<type>(<scope>): <中文摘要>`，类型限 feat/fix/docs/style/refactor/perf/test/chore/ci/merge；
2. scope 必填（允许字母、数字、下划线、连字符，大小写不限——历史分支名如 `Data-analysis` 需兼容）；
3. 摘要 ≤50 字符且**至少含一个中文字符**；
4. 正文不得出现「根据 diff」「AI 生成」等无信息量表述。

豁免（按常规约定放行并提示，不计违规）：
- git 默认合并消息（`Merge ...`）与 `Revert ...`；
- rebase 中间态（`fixup!` / `squash!` 前缀，最终提交会再校验一次）；
- 全为注释/空行的消息（视为放弃提交）。
"""
from __future__ import annotations

import argparse
import re
import sys

ALLOWED_TYPES = ("feat", "fix", "docs", "style", "refactor", "perf", "test", "chore", "ci", "merge")
PATTERN = re.compile(r"^(?P<type>[a-z]+)\((?P<scope>[^()\s]+)\): (?P<subject>.+)$")
SUBJECT_MAX = 50
CJK_PATTERN = re.compile(r"[\u4e00-\u9fff]")
BANNED_PHRASES = ("根据 diff", "根据diff", "AI 生成", "AI生成", "ai生成")
PASS_PREFIXES = ("Merge ", "Revert ", "fixup!", "squash!")


def strip_quoted(text: str) -> str:
    """去掉**引号内**的片段（「」、“”、‘’、反引号、ASCII 单双引号）。

    用途（F-110）：禁用短语扫描不应命中「**引用/转述该禁令本身**」的正文——
    历史提交 b9247c03 在正文里说明这两条禁令，却被误判为违规。
    """
    for a, b in (("「", "」"), ("“", "”"), ("‘", "’"), ("`", "`"), ("'", "'"), ("\"", "\"")):
        text = re.sub(re.escape(a) + "[^" + re.escape(b) + "]*" + re.escape(b), "", text)
    return text


def meaningful_lines(text: str) -> list[str]:
    """去掉 BOM、git 注释行与空行后的消息行。

    BOM 容错：部分编辑器/管道会把 UTF-8 BOM（U+FEFF）写进消息文件，
    若不去除会让首行格式匹配失败（实测 Windows PowerShell 管道传参即会注入 BOM）。
    """
    out: list[str] = []
    for line in text.lstrip("\ufeff").splitlines():
        if line.startswith("#"):
            continue
        if line.strip() == "":
            continue
        out.append(line.rstrip().lstrip("\ufeff"))
    return out


def validate(text: str) -> tuple[list[str], list[str]]:
    """返回 (错误列表, 提示列表)。"""
    errors: list[str] = []
    notices: list[str] = []
    lines = meaningful_lines(text)

    if not lines:
        errors.append("提交消息为空（仅有注释或空行）——若是有意放弃提交，请直接中止")
        return errors, notices

    subject_line = lines[0]
    body = "\n".join(lines[1:])

    _scan = strip_quoted(text)  # F-110：引号内的引用不算违规
    for phrase in BANNED_PHRASES:
        if phrase in _scan:
            errors.append(f"消息中出现无信息量表述「{phrase}」")

    if subject_line.startswith(PASS_PREFIXES):
        notices.append("识别为合并/revert/rebase 中间态消息，跳过格式校验（仅检查禁用表述）")
        return errors, notices

    m = PATTERN.match(subject_line)
    if not m:
        errors.append(
            "首行不符合 `<type>(<scope>): <中文摘要>` 格式"
            f"（实际：{subject_line[:60]}{'…' if len(subject_line) > 60 else ''}）"
        )
        return errors, notices

    ctype, scope, subject = m.group("type"), m.group("scope"), m.group("subject")

    if ctype not in ALLOWED_TYPES:
        errors.append(f"类型 `{ctype}` 不在允许列表内（允许：{'/'.join(ALLOWED_TYPES)}）")
    if not CJK_PATTERN.search(subject):
        errors.append("摘要必须使用中文（未检测到中文字符）")
    if len(subject) > SUBJECT_MAX:
        errors.append(f"摘要长度 {len(subject)} 字符，超过上限 {SUBJECT_MAX}")
    if scope != scope.lower():
        notices.append(f"scope `{scope}` 含大写字母；建议用小写（历史合并分支名除外）")
    if subject.endswith(("。", ".")):
        notices.append("摘要末尾建议不加句号")
    if body and len(lines) > 1:
        notices.append(f"含正文 {len(lines) - 1} 行")

    return errors, notices


def run_self_test() -> int:
    cases = [
        ("feat(auth): 新增令牌吊销版本校验", 0),
        ("fix(lineups): 排表保存串行化并防重载覆盖", 0),
        ("merge(Data-analysis): 合并数据分析分支到 main", 0),
        ("ci(lint): 接入 ruff 静态检查并修复其告警", 0),
        ("docs(plan): 新增合规化整改计划并登记文档索引\n\n正文说明", 0),
        ("Merge branch 'main' into feature/x", 0),
        ("Revert \"feat(auth): 新增令牌吊销版本校验\"", 0),
        ("fixup! feat(auth): 新增令牌吊销版本校验", 0),
        ("feat: 缺少作用域", 1),
        ("update(auth): 类型不在列表内", 1),
        ("feat(auth): add token revoke", 1),
        ("feat(auth): " + "很长" * 30, 1),
        ("feat(auth): 修复问题 根据 diff 生成", 1),
        ("docs(rule): 说明「根据 diff」与「AI 生成」两条禁令", 0),  # F-110：引用不算违规
        ("docs(rule): 反引号内 `根据 diff` 也不算违规", 0),
        ("", 1),
        ("# 只有注释\n#\n", 1),
    ]
    failed = 0
    for text, expect in cases:
        errors, _ = validate(text)
        got = 0 if not errors else 1
        mark = "OK " if got == expect else "FAIL"
        if got != expect:
            failed += 1
        preview = text.splitlines()[0][:48] if text.strip() else "<空>"
        print(f"  [{mark}] 期望={expect} 实际={got}  {preview}")
    print(f"自检用例 {len(cases)} 条，失败 {failed} 条")
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="校验提交消息是否符合 .agent/rules/git-commit-message.md")
    parser.add_argument("message_file", nargs="?", help="git commit-msg 钩子传入的消息文件路径")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取消息")
    parser.add_argument("--self-test", action="store_true", help="运行内置用例自检")
    parser.add_argument("--quiet", action="store_true", help="仅在失败时输出")
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    if args.stdin:
        text = sys.stdin.read()
        label = "<stdin>"
    elif args.message_file:
        with open(args.message_file, encoding="utf-8") as fh:
            text = fh.read()
        label = args.message_file
    else:
        parser.error("需要提供消息文件路径，或使用 --stdin / --self-test")

    errors, notices = validate(text)

    if errors:
        print("提交消息不符合规范（权威源 .agent/rules/git-commit-message.md）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("\n正确格式：<type>(<scope>): <中文摘要（≤50 字符）>", file=sys.stderr)
        print("提示：多行消息请用 `git commit -F <文件>`（首行主题、空行后正文）", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"提交消息校验通过（{label}）")
        for n in notices:
            print(f"  提示：{n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
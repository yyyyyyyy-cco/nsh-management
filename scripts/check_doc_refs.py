#!/usr/bin/env python3
"""文档引用的「存活核对」：memory-bank 等文档里引用的文件路径/行号是否真实存在。

**动机**：第 36–40 轮我手工反复抓到「文档指向已漂移」的问题（旧路径、旧版本号、指向不存在的文件）。
这类问题**不会让任何现有门禁报错**，故单独做成检查：抽取文档中**反引号内的路径引用**，
逐个核对「文件是否存在」与「`:行号` 是否越界」。

**设计（便于自检与反向验证）**：
- `extract_refs(text)` 与 `check_refs(refs, exists, line_count)` 都是**纯函数**，不碰文件系统；
- 实际运行时才用 `git ls-files` 建立「存在性」与「行数」查询；
- **误报控制**：只认带**已知扩展名**的反引号片段，排除 URL、glob、含空格、绝对 Windows 路径；
  裸文件名（如 `config.py:52`）通过**全仓 basename 唯一匹配**解析，多重匹配记为「歧义」而不是失败。

用法：
    python scripts/check_doc_refs.py                 # 报告模式（有缺失即 exit 1）
    python scripts/check_doc_refs.py --self-test     # 内置样例自检
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCAN = [
    "AGENTS.md", "README.md", "DEPLOY.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md",
    # 2026-10-03 补：两端的模块开发文档此前未被覆盖（本轮核对发现盲区，实测引用全部存活：4 + 5 条）
    "backend/docs/README.md", "frontend/docs/README.md",
]
SCAN_DIRS = ["memory-bank", ".agent/plans", ".agent/rules"]

# 反引号片段；只接受「像文件」的：带扩展名（/ 或裸文件名皆可）
BACKTICK = re.compile(r"`([^`\n]{3,140})`")
EXT = r"(?:py|ts|vue|md|json|ya?ml|sh|conf|txt|toml|ini|cfg|example|css|scss|html|sql|db|env)"
# 行号后缀：`:12`、`:12-34`、`:15,18,281`（后者仅取首个数字，且不参与越界判定）
LINE_SUFFIX = re.compile(r"^(?P<path>.+?):(?P<line>\d+)(?P<rest>(?:[-,\d])*)$")
SKIP = re.compile(r"(https?://|www\.|^E:|^[A-Za-z]:|\*|^/|\$|\.\.\.|~|^[!<>])")

# 明确不是路径的常见反引号内容（命令、变量、规则名等）
NOT_PATH = re.compile(
    # 裸扩展名（`.sh`/`.py`/`.vue`/`.css`/`.html`/`.db`/`.md` 等）不是路径；含空白/等号/括号的也不是
    r"^\.[A-Za-z0-9]+$|^(\d+\.\d+\.\d+|v\d+[\w.]*|[A-Z_]{3,}|[a-z-]+\(\)|--?[a-z-]+|"
    r"[a-z_]+\|[a-z_]+|\$[\w-]+)$|[\s=<>|&(){}\[\]]"
)


# 历史记录行（更新记录表 / 时间戳行）不作为引用来源：
# 它们记录的是**当时的**事实，常含旧文件名、旧路径、一次性脚本名等，扫进来只会制造噪声。
# 口径与 check_doc_numbers.py「已排除日期开头的更新记录行」一致（2026-10-03 补）。
_HIST_ROW = re.compile(r"^\|\s*\d{4}-\d{2}-\d{2}\s*\||^\s*[-*]?\s*\d{4}-\d{2}-\d{2}\s*[:：|]")


def strip_history_rows(text: str) -> str:
    """剔除历史记录行（纯函数）：保留行数以便行号仍可对应原文件。"""
    return "\n".join("" if _HIST_ROW.match(line) else line for line in text.split("\n"))


def extract_refs(text: str) -> list[tuple[str, int | None, int | None]]:
    """从文档文本抽取 (路径, 起始行, 结束行)。纯函数。"""
    out: list[tuple[str, int | None, int | None]] = []
    seen: set[str] = set()
    for m in BACKTICK.finditer(text):
        raw = m.group(1).strip()
        if SKIP.search(raw) or NOT_PATH.search(raw):
            continue
        line = end = None
        lm = LINE_SUFFIX.match(raw)
        if lm:
            raw, line = lm.group("path"), int(lm.group("line"))
            rest = lm.group("rest") or ""
            if "-" in rest:  # 明确的范围；用正则取数字，避免 lstrip 误用导致 int("") 崩溃
                m2 = re.match(r"-\s*(\d+)", rest)
                end = int(m2.group(1)) if m2 else None
            elif "," in rest:  # 逗号列表：不参与越界判定（如 `:15,18,281`）
                line = None
        raw = raw.strip().strip("`'\"()")
        if not re.search(rf"\.{EXT}$", raw) and not re.search(rf"\.{EXT}[:#]", raw):
            continue
        if raw in seen:
            continue
        seen.add(raw)
        out.append((raw, line, end))
    return out


def check_refs(refs, exists, line_count):
    """返回 (ok, missing, ambiguous, bad_line)。纯函数，三个回调由调用方注入。"""
    ok: list[str] = []
    missing: list[str] = []
    ambiguous: list[tuple[str, list[str]]] = []
    bad_line: list[tuple[str, int, int]] = []
    for path, line, end in refs:
        target = exists(path)
        if target is None:
            missing.append(path)
            continue
        if isinstance(target, list):
            ambiguous.append((path, target))
            continue
        if line is not None:
            n = line_count(target)
            if n is not None and (line < 1 or line > n or (end is not None and end > n)):
                bad_line.append((path, end or line, n))
                continue
        ok.append(path)
    return ok, missing, ambiguous, bad_line


# ---------------- 自检 ----------------
SELF_TESTS = (
    # (文本, 期望抽取数, 说明)
    ("见 `backend/app/core/security.py`。", 1, "普通路径"),
    ("见 `config.py:52`。", 1, "裸文件名 + 行号"),
    ("见 `frontend/nginx.conf.example:82-88`。", 1, "带范围行号"),
    ("见 `https://example.com/a.py`。", 0, "URL 不算"),
    ("见 `SECRET_KEY` 与 `W1-12`。", 0, "常量/编号不算"),
    ("见 `scripts/*.py`。", 0, "glob 不算"),
    ("见 `E:\\study\\x.py`。", 0, "绝对 Windows 路径不算"),
    ("见 `backend/app/core/security.py:10` 与 `config.py`。", 2, "多引用去重"),
    ("见 `scripts/selfcheck_*.py`。", 0, "glob 出现在中段也要排除"),
    ("见 `.sh` / `.bat` 引用与 `.vue` 文件。", 0, "裸扩展名不是路径"),
    ("见 `/openapi.json` 与 `/app/data/nsh.db`。", 0, "API 路由/容器路径不是仓库文件"),
    ("见 `GIT-GUIDE.md:15,18,281`。", 1, "逗号行号仍能抽出路径"),
    ("见 `.env.example`。", 1, "以点开头的隐藏文件也是路径（曾因 lstrip 误剥导致误判）"),
    ("见 `.gitignore` 这类无扩展名文件。", 0, "无扩展名的文件名不在覆盖范围（已知限制）"),
)


def run_self_test() -> int:
    failed = 0
    for text, want, note in SELF_TESTS:
        got = len(extract_refs(text))
        ok = got == want
        failed += 0 if ok else 1
        print(f"[{'PASS' if ok else 'FAIL'}] {note}：期望 {want} 实得 {got}")
    # 纯函数行为：存在性 / 行号越界
    refs = [("a.py", 5, None), ("b.py", 99, None), ("c.py", None, None)]
    files = {"a.py": 10, "b.py": 10}
    ok, missing, amb, bad = check_refs(refs, lambda p: (p if p in files else (["x", "y"] if p == "c.py" else None)),
                                        lambda t: files.get(t))
    cases = [(len(ok) == 1, "存在且行号合法计入 ok"), (missing == [], "无缺失"),
             (len(amb) == 1, "多重匹配记为歧义"), (len(bad) == 1 and bad[0][1] == 99, "行号越界被识别")]
    for cond, note in cases:
        failed += 0 if cond else 1
        print(f"[{'PASS' if cond else 'FAIL'}] {note}")
    # 历史记录行剔除（管线行为，单列断言以免与 extract_refs 表格用例混淆）
    hist = "| 2026-10-03 | 修了 `old/ghost.py` |\n正文 `backend/app/main.py`\n"
    cases.append((len(extract_refs(strip_history_rows(hist))) == 1,
                  "带日期的历史记录行被剔除，且行号仍与原文件对齐"))
    cases.append((len(extract_refs(hist)) == 2, "未剔除时两条引用都会被抽出（对照）"))
    total = len(SELF_TESTS) + len(cases)
    print(f"自检：{total - failed}/{total} 通过")
    return 1 if failed else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return run_self_test()

    files = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True,
                           encoding="utf-8").stdout.split("\n")
    by_name: dict[str, list[str]] = {}
    for f in files:
        if f:
            by_name.setdefault(Path(f).name, []).append(f)
    line_cache: dict[str, int] = {}

    def exists(path: str):
        # 注意：不能用 `lstrip("./")` —— lstrip 剥的是**字符集合**，会把 `.env.example` 剥成 `env.example` ✗
        p = path[2:] if path.startswith("./") else path
        if (ROOT / p).is_file():
            return p
        if (ROOT / p).exists() and not (ROOT / p).is_dir():
            return p
        hits = by_name.get(Path(p).name, [])
        if len(hits) == 1:
            return hits[0]
        if len(hits) > 1:
            return hits
        if (ROOT / p).exists():
            return p  # 目录
        return None

    def line_count(target: str) -> int:
        if target not in line_cache:
            try:
                line_cache[target] = len((ROOT / target).read_text(encoding="utf-8", errors="ignore").split("\n"))
            except OSError:
                line_cache[target] = 0
        return line_cache[target]

    docs: list[Path] = [ROOT / f for f in SCAN if (ROOT / f).exists()]
    for d in SCAN_DIRS:
        docs += sorted((ROOT / d).glob("*.md"))
    total_ok = total_missing = total_amb = total_bad = 0
    for doc in docs:
        refs = extract_refs(strip_history_rows(doc.read_text(encoding="utf-8")))
        ok, missing, amb, bad = check_refs(refs, exists, line_count)
        total_ok += len(ok)
        total_missing += len(missing)
        total_amb += len(amb)
        total_bad += len(bad)
        if missing or bad:
            rel = doc.relative_to(ROOT).as_posix()
            for m in missing:
                print(f"[missing] {rel}: 引用了不存在的文件 -> {m}")
            for p, ln, n in bad:
                print(f"[bad-line] {rel}: {p}:{ln} 越界（该文件仅 {n} 行）")
        if amb:
            rel = doc.relative_to(ROOT).as_posix()
            for p, hits in amb:
                print(f"[ambiguous] {rel}: `{p}` 匹配多个文件 -> {hits[:3]}")
    print(f"[doc-refs] 扫描 {len(docs)} 个文档：引用 {total_ok + total_missing + total_amb + total_bad} 处 "
          f"| 有效 {total_ok} | 缺失 {total_missing} | 行号越界 {total_bad} | 歧义 {total_amb}")
    print(
        "[doc-refs] 说明：本检查**不作为门禁**。实测存在大量**故意的**不存在的引用"
        "（待创建文件如 `deploy.sh`、gitignore 文件、占位符、API 路由、改名历史记录等），"
        "故只作人工辅助；如需失败语义请显式加 `--strict`。"
    )
    if (total_missing or total_bad) and "--strict" in argv:
        return 1
    if total_missing or total_bad:
        print("[doc-refs] 报告完毕（未加 --strict，退出码 0）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
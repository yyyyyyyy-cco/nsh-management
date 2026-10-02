"""pytest 引导：把后端根目录与 tests 目录加入 sys.path（合规化计划 W2-2）。

这样测试可以直接 `import app...`（无需安装为包），也可以 `from support import ...`
复用公共基类，且与 `python -m pytest`（在 backend/ 下执行）或 IDE 直接运行都兼容。
"""
import sys
from pathlib import Path

TESTS_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = TESTS_DIR.parent

for path in (str(BACKEND_ROOT), str(TESTS_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)
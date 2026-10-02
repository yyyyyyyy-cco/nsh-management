"""统一日志配置：控制台 + 滚动文件，接管 uvicorn 日志。

用法：main.py 启动时调用 setup_logging()。
"""
import logging
import logging.handlers
import sys

from app.core.config import LOG_DIR, settings

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging() -> None:
    """配置根 logger 与 uvicorn logger，避免重复 handler。"""
    level = logging.DEBUG if settings.DEBUG else logging.INFO
    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    root = logging.getLogger()
    root.setLevel(level)
    # 幂等：重复调用不叠加 handler
    if any(isinstance(h, logging.StreamHandler) for h in root.handlers):
        return

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    if LOG_DIR is not None:
        file_handler = logging.handlers.RotatingFileHandler(
            LOG_DIR / "app.log",
            maxBytes=10 * 1024 * 1024,  # 单文件 10MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    # uvicorn 自带 handler 与根 logger 重复输出，统一接管
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True

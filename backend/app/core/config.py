"""应用配置：环境变量优先，未设置时使用开发默认值。"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    APP_NAME: str = "轻衫都会用的帮会联赛管理系统"
    API_PREFIX: str = "/api/v1"

    # 安全
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10 * 60  # JWT 有效期 10 小时

    # 调试开关：生产默认关闭（异常详情不入响应），本地开发可设 DEBUG=true
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR / 'nsh.db'}")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 登录限流
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_LOCK_MINUTES: int = 5


settings = Settings()

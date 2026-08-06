"""应用配置：环境变量优先，未设置时使用开发默认值。"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Settings:
    APP_NAME: str = "帮会联赛管理系统"
    API_PREFIX: str = "/api/v1"

    # 安全
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 7 * 24 * 60  # JWT 有效期 7 天

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR / 'nsh.db'}")

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # 登录限流
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_LOCK_MINUTES: int = 5


settings = Settings()

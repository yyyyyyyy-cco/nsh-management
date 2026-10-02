"""应用配置：环境变量优先，未设置时使用开发默认值。"""
import os
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR = BASE_DIR / "logs"
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    # 文件系统只读时退化为仅控制台输出
    LOG_DIR = None


def _parse_cors_origins(raw: str) -> list[str]:
    """解析 CORS 白名单（合规化计划 W4-3）：逗号分隔，去除首尾空白与空项。

    空字符串返回空列表，由调用方决定回退值——这样「未配置」与「配置为空」语义一致。
    """
    return [item for item in (part.strip() for part in raw.split(",")) if item]


class Settings:
    APP_NAME: str = "轻衫都会用的帮会联赛管理系统"
    API_PREFIX: str = "/api/v1"

    # 安全
    # 开发默认值：仅供本地开发使用，生产环境（APP_ENV=production 或容器特征兜底）由**应用启动入口**强制校验，
    # 见 validate_secret_key / enforce_secret_key 与 app/main.py 的 startup_checks（导入期不再校验，见文件末尾说明）
    _DEV_SECRET_KEY = "dev-secret-key-change-in-production"
    SECRET_KEY: str = os.getenv("SECRET_KEY", _DEV_SECRET_KEY)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10 * 60  # JWT 有效期 10 小时

    # 调试开关：生产默认关闭（异常详情不入响应），本地开发可设 DEBUG=true
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR / 'nsh.db'}")

    # CORS（W4-3：外置为环境变量 CORS_ORIGINS，逗号分隔）
    # 默认值只覆盖本地开发（Vite 5173）。生产部署由 Nginx **同源**反代 /api，浏览器不触发跨域，
    # 通常无需设置；仅当 API 被跨域直接调用（独立前端域名 / 第三方调用）时才需显式配置。
    # 安全提示：不要配置为 `*`——本项目 `allow_credentials=True`，通配会放宽浏览器侧凭证策略。
    _DEV_CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    CORS_ORIGINS: list[str] = _parse_cors_origins(os.getenv("CORS_ORIGINS", "")) or list(_DEV_CORS_ORIGINS)

    # 登录限流
    LOGIN_MAX_FAILURES: int = 5
    LOGIN_LOCK_MINUTES: int = 5

    # 日志
    LOG_RETENTION_DAYS: int = int(os.getenv("LOG_RETENTION_DAYS", "90"))

    # 告警（合规化计划 W4-6 / F-44）：错误率阈值触发通知
    # 未配置 ALERT_WEBHOOK_URL 时**仅写 WARNING 日志**（不静默）；阈值 <=0 表示禁用告警。
    ALERT_ERROR_THRESHOLD: int = int(os.getenv("ALERT_ERROR_THRESHOLD", "20"))
    ALERT_WINDOW_MINUTES: int = int(os.getenv("ALERT_WINDOW_MINUTES", "30"))
    ALERT_CHECK_INTERVAL_MINUTES: int = int(os.getenv("ALERT_CHECK_INTERVAL_MINUTES", "15"))
    ALERT_WEBHOOK_URL: str = os.getenv("ALERT_WEBHOOK_URL", "")


settings = Settings()

# .env.example 模板中的占位密钥，与开发默认值一样均视为弱密钥
_WEAK_SECRET_KEYS = frozenset({
    Settings._DEV_SECRET_KEY,
    "your-secret-key-change-this",
    "please-change-me-with-openssl-rand-hex-32",
})

# 可猜片段黑名单（小写匹配）：拦截「长而可猜」的拼接式密钥。
# 片段均含非十六进制字符；随机 hex 串另走豁免通道（见 _secret_key_is_weak）。
_GUESSABLE_FRAGMENTS = frozenset({
    "nsh", "management", "secret", "key", "change", "example", "please",
    "password", "admin", "member", "developer", "guild", "league",
    "qingshan", "banghui", "jwt", "token", "dev", "test", "prod",
})
_YEAR_PATTERN = re.compile(r"20\d{2}")
_HEX_PATTERN = re.compile(r"[0-9a-f]+")


def _secret_key_is_weak(key: str) -> bool:
    """密钥强度判定：弱集合 / 长度 <32 / 含可猜片段或年份 → True。

    豁免通道：≥64 字符的纯十六进制串（即 openssl rand -hex 32 及以上，熵 ≥256 bit）
    恒判为强；否则年份模式 20\\d\\d 在随机 hex 中会偶然出现（单密钥概率约 20%），
    导致误杀合法强密钥。
    """
    if key in _WEAK_SECRET_KEYS or len(key) < 32:
        return True
    lowered = key.lower()
    if len(lowered) >= 64 and _HEX_PATTERN.fullmatch(lowered):
        return False
    return any(frag in lowered for frag in _GUESSABLE_FRAGMENTS) or bool(_YEAR_PATTERN.search(lowered))


def _is_production() -> bool:
    """判定是否运行在生产环境。

    主判据为显式 APP_ENV 变量（docker-compose.yml 已固定 production）；
    未声明时以容器特征兜底（k8s/podman/裸机无法命中兜底，故迁移时应显式设置 APP_ENV）。
    """
    app_env = os.getenv("APP_ENV", "").strip().lower()
    if app_env in {"production", "prod"}:
        return True
    if app_env in {"development", "dev", "test"}:
        return False
    # 未声明 APP_ENV：容器特征兜底
    if os.path.exists("/.dockerenv"):
        return True
    try:
        with open("/proc/1/cgroup", encoding="utf-8") as f:
            content = f.read()
        return "docker" in content or "containerd" in content
    except (OSError, UnicodeDecodeError):
        # cgroup v2 主机上该文件常只有 "0::/"，判据可能失效，故上方 APP_ENV 为主
        return False


def api_docs_enabled() -> bool:
    """是否启用在线 API 文档（`/docs`、`/redoc`、`/openapi.json`）。

    生产环境关闭：在线文档会向任何访问者暴露完整接口、参数与数据结构，属
    OWASP Top 10:2025 A02（安全配置错误）与 ASVS 配置项的整改范围（合规化计划 W4-1）；
    本地开发环境（无非生产特征）保留，便于调试与联调。
    """
    return not _is_production()


class InsecureSecretKeyError(RuntimeError):
    """生产环境 SECRET_KEY 强度不足（由启动门禁抛出，见 validate_secret_key）。"""


# 运维可见文案（centrally defined，测试断言关键句）：FATAL 文案保持与改造前逐字一致
FATAL_SECRET_KEY_MESSAGE = (
    "FATAL: 生产环境 SECRET_KEY 未设置、仍为默认/占位值或强度不足\n"
    "（要求：至少 32 字符，且不含项目名/单词/年份等可猜片段）。\n"
    "请在部署 .env 文件中配置强随机密钥（生成命令：openssl rand -hex 32），\n"
    "否则任何持有默认密钥的人都可伪造登录 Token。"
)
WEAK_SECRET_KEY_WARNING = (
    "WARNING: 当前 SECRET_KEY 为弱密钥（开发默认值或可猜片段）。\n"
    "本地开发可忽略；生产/容器部署前请用 openssl rand -hex 32 生成强随机密钥\n"
    "并在 .env 中设置 APP_ENV=production（生产环境下弱密钥将拒绝启动）。"
)


def validate_secret_key() -> None:
    """SECRET_KEY 安全校验：生产环境弱密钥抛 `InsecureSecretKeyError`，开发环境仅告警放行。

    开发环境保持可用：允许未设置时使用默认值，不影响本地开发与现有 .env；
    但弱密钥会打印 WARNING，避免生产判定 fail-open 时被静默跳过。

    返回 `None` 表示通过（无返回值语义）；调用方在启动入口用 `enforce_secret_key()`。
    """
    weak = _secret_key_is_weak(settings.SECRET_KEY)
    if _is_production():
        if weak:
            raise InsecureSecretKeyError(FATAL_SECRET_KEY_MESSAGE)
    elif weak:
        print(WEAK_SECRET_KEY_WARNING, file=sys.stderr)


def enforce_secret_key() -> None:
    """启动门禁：把弱密钥转成「打印 FATAL + 退出码 1」（部署侧既有可见行为）。

    应用入口（`app/main.py` 的 startup 钩子）与任何自定义入口都应调用本函数；
    进程被 uvicorn 的 lifespan 路径终止时 uvicorn 会以「启动失败」退出（非零），
    直接调用本函数时退出码恒为 1。
    """
    try:
        validate_secret_key()
    except InsecureSecretKeyError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


# 注意（F-04 / 合规化计划 W2-6）：这里**不再**在导入期调用校验。
# 原因：`app.core.config` 被 alembic、测试收集、一次性脚本等大量非服务场景导入，
# 导入期 `sys.exit` 会让这些场景在生产环境下被无谓终止，也使门禁本身无法被测试。
# 门禁现由应用启动入口显式执行：`app/main.py` → `startup_checks()`。
# 目录创建（DATA_DIR / LOG_DIR）保留在导入期：幂等、不中止进程，且被
# `logging_config`（LOG_DIR）与 SQLite 路径（DATA_DIR）在导入期依赖。

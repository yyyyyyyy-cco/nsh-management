"""应用入口：创建 FastAPI 实例、注册 CORS/异常处理/审计日志中间件/路由。"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.health import router as health_router
from app.api.v1.router import api_router
from app.core.client_ip import get_client_ip
from app.core.config import api_docs_enabled, enforce_secret_key, settings
from app.core.logging_config import setup_logging
from app.core.security import decode_access_token
from app.core.database import async_session_factory
from app.models.user import User
from app.services import alert_service, log_service
from app.services.attendance_service import AttendanceServiceError
from app.services.auth_service import AuthError
from app.services.config_service import ConfigServiceError
from app.services.game_id_request_service import GameIdRequestError
from app.services.lineup_service import LineupServiceError
from app.services.match_data_csv import MatchDataError
from app.services.member_service import MemberServiceError
from app.services.player_identity_service import PlayerIdentityError
from app.services.recording_service import RecordingServiceError
from app.services.schedule_service import ScheduleServiceError
from app.services.squad_adjustment_service import SquadAdjustmentError
from app.utils.excel_import import ExcelImportError

setup_logging()
logger = logging.getLogger(__name__)

# 在线 API 文档开关（合规化计划 W4-1）：生产环境关闭 `/docs`、`/redoc`、`/openapi.json`
# （暴露完整接口与数据结构属 OWASP Top 10:2025 A02 安全配置错误）；本地开发保留以便调试。
_DOCS_ENABLED = api_docs_enabled()

@asynccontextmanager
async def lifespan(application: FastAPI):
    """应用生命周期（2026-10-02 迁移：替代 FastAPI 已弃用的 `@app.on_event("startup")`）。

    语义与迁移前一致：先过**启动安全门禁**（生产弱密钥拒绝启动），再启动两个后台循环；
    退出时取消循环，避免测试/重启场景下后台任务悬挂（原写法没有关闭钩子）。
    """
    startup_checks()
    application.state.log_cleanup_task = asyncio.create_task(_log_cleanup_loop())
    application.state.alert_task = asyncio.create_task(_alert_loop())
    try:
        yield
    finally:
        for attr in ("log_cleanup_task", "alert_task"):
            task = getattr(application.state, attr, None)
            if task is not None:
                task.cancel()


app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan,
    docs_url="/docs" if _DOCS_ENABLED else None,
    redoc_url="/redoc" if _DOCS_ENABLED else None,
    openapi_url="/openapi.json" if _DOCS_ENABLED else None,
)

# 审计中间件拦截的写方法与豁免路径（login 在 auth 接口内手动埋点，含失败详情；
# developer/logs 的 DELETE 在接口内手动埋点带清理详情）
AUDIT_METHODS = {"POST", "PUT", "DELETE", "PATCH"}
AUDIT_EXCLUDED_PATHS = {"/api/v1/auth/login", "/api/v1/developer/logs"}


class AuditLogMiddleware(BaseHTTPMiddleware):
    """写操作审计中间件：拦截 POST/PUT/DELETE/PATCH，响应后落库一条审计日志。

    用户身份优先复用请求认证依赖挂载的 request.state.user（省一次 JWT 解码 + 查库）；
    依赖未执行到（如 401/404）时回退到 Authorization 解析。
    """

    async def dispatch(self, request: Request, call_next):
        should_audit = (
            request.method in AUDIT_METHODS
            and request.url.path not in AUDIT_EXCLUDED_PATHS
        )
        exception: Exception | None = None
        status_code: int | None = None
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as exc:
            exception = exc
            raise
        finally:
            is_error = exception is not None or (status_code is not None and status_code >= 500)
            # 写操作全部审计；错误（未处理异常/5xx）不限方法也落库，读操作的 4xx 不记避免噪音
            if is_error or should_audit:
                detail: dict | str | None = None
                if exception is not None:
                    level = "error"
                    detail = f"未处理异常: {exception}"
                elif status_code is not None and status_code >= 500:
                    level = "error"
                else:
                    level = "info"
                    if status_code is not None and status_code >= 400:
                        level = "warning"
                asyncio.create_task(self._write_log(request, status_code, level, detail))

    @staticmethod
    async def _resolve_user(request: Request) -> User | None:
        # 请求认证依赖已解析用户时直接复用；回退路径用于依赖未执行到的情况
        cached = getattr(request.state, "user", None)
        if cached is not None:
            return cached
        auth_header = request.headers.get("authorization", "")
        token = auth_header[7:] if auth_header.lower().startswith("bearer ") else ""
        payload = decode_access_token(token) if token else None
        if payload is None:
            return None
        try:
            user_id = int(payload["sub"])
        except (KeyError, TypeError, ValueError):
            return None
        try:
            async with async_session_factory() as session:
                return await session.get(User, user_id)
        except Exception:  # noqa: BLE001
            return None

    async def _write_log(
        self, request: Request, status_code: int | None, level: str, detail: dict | str | None
    ) -> None:
        try:
            user = await self._resolve_user(request)
            ip = get_client_ip(request)
            await log_service.record_log(
                module=log_service.module_from_path(request.url.path),
                action=log_service.action_from_method(request.method, request.url.path),
                level=level,
                user=user,
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                detail=detail,
                ip=ip,
            )
        except Exception:  # noqa: BLE001
            logger.exception("审计中间件写日志失败")


app.add_middleware(AuditLogMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)
# 健康检查（合规化计划 W3-1）挂两处：
#   ① 根路径 `/health`：容器 healthcheck 与内网探针直接命中（见 docker-compose.yml）；
#   ② `/api/v1/health`：经既有 `/api/*` 反向代理对外可达，供外部 uptime 监控探活
#      （若运维不希望对外暴露，可在边缘 Nginx 拦掉该路径）
app.include_router(health_router)
app.include_router(health_router, prefix=settings.API_PREFIX)


def startup_checks() -> None:
    """启动前置安全门禁（合规化计划 F-04）：生产环境弱 SECRET_KEY 打印 FATAL 并拒绝启动。

    该门禁原先在 `app.core.config` **导入期**执行，导致 alembic、测试收集、一次性脚本等
    只要 import 配置就会被终止（也使门禁本身无法被测试）；现改为显式启动校验：
    运维可见文案与退出行为不变（见 DEPLOY.md §六），且可被单元测试直接调用。
    """
    enforce_secret_key()


async def _alert_loop() -> None:
    """错误率告警循环（W4-6）：启动即检查一次，之后每 `ALERT_CHECK_INTERVAL_MINUTES` 分钟一次。

    判定与通知策略见 `app/core/alerting.py` 与 `app/services/alert_service.py`；
    未配置 `ALERT_WEBHOOK_URL` 时仅写 WARNING 日志（不静默）。
    """
    interval = max(settings.ALERT_CHECK_INTERVAL_MINUTES, 1) * 60
    while True:
        try:
            await alert_service.run_alert_check()
        except Exception:  # noqa: BLE001 — 告警循环自身异常不得终止进程
            logger.exception("错误率告警检查失败")
        await asyncio.sleep(interval)


async def _log_cleanup_loop() -> None:
    """审计日志保留清理循环：启动即清一次，之后每日一次（长驻进程日志不再只增不减）。"""
    while True:
        try:
            await log_service.clear_old_logs()
        except Exception:  # noqa: BLE001
            logger.exception("审计日志定期清理失败")
        await asyncio.sleep(24 * 3600)


def error_response(status_code: int, message: str) -> JSONResponse:
    """统一错误响应体：{code, message, data}。"""
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": None},
    )


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    # 账号锁定时 data 携带剩余解锁秒数，供前端禁用表单并倒计时
    data = {"remaining_seconds": exc.remaining_seconds} if exc.remaining_seconds is not None else None
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.status_code, "message": exc.message, "data": data},
    )


@app.exception_handler(MemberServiceError)
async def member_error_handler(request: Request, exc: MemberServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(GameIdRequestError)
async def game_id_request_error_handler(request: Request, exc: GameIdRequestError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(PlayerIdentityError)
async def player_identity_error_handler(request: Request, exc: PlayerIdentityError) -> JSONResponse:
    """战绩名称合并冲突：提示改用「仅查此 ID」（HTTP 409）。"""
    return error_response(exc.status_code, exc.message)


@app.exception_handler(ScheduleServiceError)
async def schedule_error_handler(request: Request, exc: ScheduleServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(AttendanceServiceError)
async def attendance_error_handler(request: Request, exc: AttendanceServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(LineupServiceError)
async def lineup_error_handler(request: Request, exc: LineupServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(ExcelImportError)
async def excel_import_error_handler(request: Request, exc: ExcelImportError) -> JSONResponse:
    return error_response(400, exc.message)


@app.exception_handler(ConfigServiceError)
async def config_error_handler(request: Request, exc: ConfigServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(RecordingServiceError)
async def recording_error_handler(request: Request, exc: RecordingServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(MatchDataError)
async def match_data_error_handler(request: Request, exc: MatchDataError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(SquadAdjustmentError)
async def squad_adjustment_error_handler(request: Request, exc: SquadAdjustmentError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "请求参数校验失败")


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """全局异常处理，捕获所有未处理的异常。"""
    logger.exception("未处理的异常: %s %s", request.method, request.url.path)
    # 安全：生产环境不向客户端泄露异常详情，仅本地开发（DEBUG=true）可见
    message = f"服务器内部错误: {str(exc)}" if settings.DEBUG else "服务器内部错误"
    return error_response(500, message)


@app.get("/")
async def root() -> dict:
    return {"message": settings.APP_NAME, "status": "ok"}

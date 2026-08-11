"""应用入口：创建 FastAPI 实例、注册 CORS/异常处理/路由。"""
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.auth_service import AuthError
from app.services.member_service import MemberServiceError
from app.utils.excel_import import ExcelImportError

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


def error_response(status_code: int, message: str) -> JSONResponse:
    """统一错误响应体：{code, message, data}。"""
    return JSONResponse(
        status_code=status_code,
        content={"code": status_code, "message": message, "data": None},
    )


@app.exception_handler(AuthError)
async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(MemberServiceError)
async def member_error_handler(request: Request, exc: MemberServiceError) -> JSONResponse:
    return error_response(exc.status_code, exc.message)


@app.exception_handler(ExcelImportError)
async def excel_import_error_handler(request: Request, exc: ExcelImportError) -> JSONResponse:
    return error_response(400, exc.message)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return error_response(exc.status_code, str(exc.detail))


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "请求参数校验失败")


@app.get("/")
async def root() -> dict:
    return {"message": settings.APP_NAME, "status": "ok"}

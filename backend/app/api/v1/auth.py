"""认证接口：登录、登出、当前用户。"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.config import settings
from app.models.guild import Guild
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserOut
from app.services import log_service
from app.services.auth_service import AuthError, authenticate

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request, body: LoginRequest, session: AsyncSession = Depends(get_db)
) -> LoginResponse:
    ip = request.client.host if request.client else None
    try:
        token, user = await authenticate(session, body.username, body.password)
    except AuthError as exc:
        # 登录失败埋点：中间件豁免 /auth/login，此处手动记录含失败原因
        await log_service.record_log(
            module="auth",
            action="login_failed",
            level="warning",
            username=body.username,
            method="POST",
            path=f"{settings.API_PREFIX}/auth/login",
            status_code=exc.status_code,
            detail=exc.message,
            ip=ip,
        )
        raise
    await log_service.record_log(
        module="auth",
        action="login",
        level="info",
        user=user,
        method="POST",
        path=f"{settings.API_PREFIX}/auth/login",
        status_code=200,
        ip=ip,
    )
    return LoginResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout")
async def logout() -> dict:
    # JWT 无状态：登出由前端丢弃 Token。不递增 token_version——共享账号多人多 IP 使用，
    # 一人登出不应踢掉同账号其他设备；令牌吊销由改密/禁用触发（见 get_current_user）。
    return {"message": "已退出登录"}


@router.get("/me", response_model=UserOut)
async def me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> UserOut:
    guild = None
    if current_user.guild_id is not None:
        guild = await session.get(Guild, current_user.guild_id)
    return UserOut(
        id=current_user.id,
        guild_id=current_user.guild_id,
        guild_name=guild.name if guild else None,
        guild_icon=guild.icon_char if guild else None,
        username=current_user.username,
        role=current_user.role,
        status=current_user.status,
    )

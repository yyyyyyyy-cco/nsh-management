"""认证业务：密码校验、登录限流、令牌签发。"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User


class AuthError(Exception):
    """认证业务异常，携带 HTTP 状态码与提示。"""

    def __init__(self, message: str, status_code: int = 401):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def authenticate(session: AsyncSession, username: str, password: str) -> tuple[str, User]:
    """校验账号密码，返回 (access_token, user)。失败抛 AuthError。"""
    user = await get_user_by_username(session, username)
    if user is None:
        raise AuthError("用户名或密码错误")

    now = datetime.now(timezone.utc)
    if user.locked_until and user.locked_until > now:
        raise AuthError("登录失败次数过多，账号已锁定，请稍后再试")

    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.LOGIN_MAX_FAILURES:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
        await session.commit()
        raise AuthError("用户名或密码错误")

    if user.status != "active":
        raise AuthError("账号已被禁用")

    user.failed_attempts = 0
    user.locked_until = None
    await session.commit()

    token = create_access_token(user.id, user.role)
    return token, user

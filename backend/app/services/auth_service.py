"""认证业务：密码校验、登录限流、令牌签发。"""
import math
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.models.user import User


class AuthError(Exception):
    """认证业务异常，携带 HTTP 状态码与提示。"""

    def __init__(self, message: str, status_code: int = 401, remaining_seconds: int | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        # 账号锁定时携带剩余解锁秒数，供前端禁用表单并倒计时
        self.remaining_seconds = remaining_seconds


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    result = await session.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


# 账号不存在时的失败计数与锁定时间（进程内存，服务重启后清零）
_unknown_login_failures: dict[str, dict] = {}


async def authenticate(session: AsyncSession, username: str, password: str) -> tuple[str, User]:
    """校验账号密码，返回 (access_token, user)。失败抛 AuthError。"""
    user = await get_user_by_username(session, username)
    now = datetime.now(timezone.utc)
    if user is None:
        # 账号不存在：内存计数锁定，防止对不存在账号的暴力试探
        record = _unknown_login_failures.setdefault(username, {"failed_attempts": 0, "locked_until": None})
        if record["locked_until"] and record["locked_until"] > now:
            seconds_left = max(1, int((record["locked_until"] - now).total_seconds()))
            minutes_left = max(1, math.ceil(seconds_left / 60))
            raise AuthError(
                f"登录失败次数过多，账号已锁定，请 {minutes_left} 分钟后重试",
                remaining_seconds=seconds_left,
            )
        record["failed_attempts"] += 1
        if record["failed_attempts"] >= settings.LOGIN_MAX_FAILURES:
            record["locked_until"] = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            raise AuthError(
                f"登录失败次数过多，账号已锁定，请 {settings.LOGIN_LOCK_MINUTES} 分钟后重试",
                remaining_seconds=settings.LOGIN_LOCK_MINUTES * 60,
            )
        remaining = settings.LOGIN_MAX_FAILURES - record["failed_attempts"]
        raise AuthError(f"用户名或密码错误，还可尝试 {remaining} 次")

    # SQLite 读回的 locked_until 丢失时区信息（naive），统一按 UTC 处理后再比较
    locked_until = user.locked_until
    if locked_until is not None and locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    if locked_until and locked_until > now:
        seconds_left = max(1, int((locked_until - now).total_seconds()))
        minutes_left = max(1, math.ceil(seconds_left / 60))
        raise AuthError(
            f"登录失败次数过多，账号已锁定，请 {minutes_left} 分钟后重试",
            remaining_seconds=seconds_left,
        )

    if not verify_password(password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= settings.LOGIN_MAX_FAILURES:
            user.locked_until = now + timedelta(minutes=settings.LOGIN_LOCK_MINUTES)
            await session.commit()
            raise AuthError(
                f"登录失败次数过多，账号已锁定，请 {settings.LOGIN_LOCK_MINUTES} 分钟后重试",
                remaining_seconds=settings.LOGIN_LOCK_MINUTES * 60,
            )
        remaining = settings.LOGIN_MAX_FAILURES - user.failed_attempts
        await session.commit()
        raise AuthError(f"用户名或密码错误，还可尝试 {remaining} 次")

    if user.status != "active":
        raise AuthError("账号已被禁用")

    user.failed_attempts = 0
    user.locked_until = None
    await session.commit()
    # 账号不存在时的失败记录随同名账号创建后登录成功一并清理
    _unknown_login_failures.pop(username, None)

    token = create_access_token(user.id, user.role)
    return token, user

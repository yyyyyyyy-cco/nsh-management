"""依赖注入：当前用户、管理员权限校验。"""

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="未登录")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    # 防御异常 payload：sub 缺失或非数字时按未登录处理，避免 500
    try:
        user_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError):
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    user = await session.get(User, user_id)
    if user is None or user.status != "active":
        raise HTTPException(status_code=401, detail="账号不存在或已被禁用")
    # 令牌版本校验：登出/改密后旧 Token 立即失效（旧版 Token 无 ver 声明同样拒绝）
    if payload.get("ver") != user.token_version:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    # 供审计中间件复用（避免响应后二次解码 JWT + 二次查库）
    request.state.user = user
    return user


async def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role not in ("admin", "developer"):
        raise HTTPException(status_code=403, detail="无权限操作")
    return current_user


async def require_non_member(current_user: User = Depends(get_current_user)) -> User:
    """非帮众（开发者/管理员）——自助修改密码接口专用。

    产品决策（2026-10-09）：帮众禁用自助改密。帮众账号为帮会共享账号，改密会使其他
    使用者无法登录；帮众密码一律由管理员在「系统配置 → 账号管理」重置。
    """
    if current_user.role == "member":
        raise HTTPException(status_code=403, detail="帮众账号不支持自助修改密码，请联系管理员重置")
    return current_user


async def require_developer(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "developer":
        raise HTTPException(status_code=403, detail="仅开发者可操作")
    return current_user


async def _require_guild(user: User) -> User:
    """要求账号绑定有效帮会（developer 无帮会，不能访问帮会内功能）。"""
    if user.guild_id is None:
        raise HTTPException(status_code=403, detail="当前账号未绑定帮会")
    return user


async def require_member(current_user: User = Depends(get_current_user)) -> User:
    """仅帮众（游戏 ID 改名申请提交；不含 developer）。"""
    if current_user.role != "member":
        raise HTTPException(status_code=403, detail="无权限操作")
    return await _require_guild(current_user)


async def require_admin_strict(current_user: User = Depends(get_current_user)) -> User:
    """仅管理员（游戏 ID 改名审核；不含 developer）。"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="无权限操作")
    return await _require_guild(current_user)


async def require_member_or_admin(current_user: User = Depends(get_current_user)) -> User:
    """帮众或管理员（个人战绩查询；不含 developer）。"""
    if current_user.role not in ("member", "admin"):
        raise HTTPException(status_code=403, detail="无权限操作")
    return await _require_guild(current_user)

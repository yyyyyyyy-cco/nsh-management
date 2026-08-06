"""认证接口：登录、登出、当前用户。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, UserOut
from app.services.auth_service import authenticate

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_db)) -> LoginResponse:
    token, user = await authenticate(session, body.username, body.password)
    return LoginResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/logout")
async def logout() -> dict:
    # JWT 无状态，登出由前端丢弃 Token
    return {"message": "已退出登录"}


@router.get("/me", response_model=UserOut)
async def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user

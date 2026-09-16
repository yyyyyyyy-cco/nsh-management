"""系统配置接口：账号管理（自 config.py 拆出，URL 前缀不变）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.config import (
    AccountCreate,
    AccountOut,
    AccountStatusUpdate,
    AccountUpdate,
)
from app.services import account_service
from app.services.config_service import ConfigServiceError

router = APIRouter(prefix="/config", tags=["系统配置"])


# ========== 账号管理 ==========

@router.get("/accounts", response_model=list[AccountOut])
async def list_accounts(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AccountOut]:
    """获取账号列表（管理员）。"""
    accounts = await account_service.list_accounts(session, current_user.guild_id)
    result = []
    for a in accounts:
        out = AccountOut.model_validate(a)
        out.guild_name = a.guild.name if a.guild else None
        # 安全：明文密码仅开发者可见，管理员/帮众不可见
        if current_user.role != "developer":
            out.plain_password = None
        result.append(out)
    return result


@router.post("/accounts", response_model=AccountOut)
async def create_account(
    body: AccountCreate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AccountOut:
    """创建账号（管理员/开发者）。开发者可指定目标帮会，管理员默认本帮会。"""
    target_guild_id = body.guild_id or current_user.guild_id
    account = await account_service.create_account(
        session, target_guild_id, body.username, body.password, body.role
    )
    out = AccountOut.model_validate(account)
    out.guild_name = account.guild.name if account.guild else None
    return out


@router.put("/accounts/{user_id}", response_model=AccountOut)
async def update_account(
    user_id: int,
    body: AccountUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AccountOut:
    """更新账号信息（管理员）。"""
    account = await account_service.update_account(
        session, current_user.guild_id, user_id, body.username, body.password
    )
    out = AccountOut.model_validate(account)
    out.guild_name = account.guild.name if account.guild else None
    return out


@router.put("/accounts/{user_id}/status", response_model=AccountOut)
async def update_account_status(
    user_id: int,
    body: AccountStatusUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AccountOut:
    """更新账号状态（管理员）。"""
    # 不允许禁用自己
    if user_id == current_user.id and body.status == "disabled":
        raise ConfigServiceError("不能禁用当前登录的账号")

    account = await account_service.update_account_status(
        session, current_user.guild_id, user_id, body.status
    )
    out = AccountOut.model_validate(account)
    out.guild_name = account.guild.name if account.guild else None
    return out


@router.delete("/accounts/{user_id}", response_model=dict)
async def delete_account(
    user_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """删除账号（管理员）。"""
    if user_id == current_user.id:
        raise ConfigServiceError("不能删除当前登录的账号")

    await account_service.delete_account(session, current_user.guild_id, user_id)
    return {"message": "账号已删除"}

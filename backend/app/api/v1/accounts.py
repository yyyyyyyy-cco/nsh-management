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


def _build_account_out(account: User, current_user: User) -> AccountOut:
    """统一构造账号响应：填充 guild_name + 角色感知脱敏 plain_password。"""
    out = AccountOut.model_validate(account)
    out.guild_name = account.guild.name if account.guild else None
    # 安全：明文密码仅 developer 可见，admin/member 不可见
    if current_user.role != "developer":
        out.plain_password = None
    return out


# ========== 账号管理 ==========


@router.get("/accounts", response_model=list[AccountOut])
async def list_accounts(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AccountOut]:
    """获取账号列表（管理员）。"""
    accounts = await account_service.list_accounts(session, current_user.guild_id)
    return [_build_account_out(a, current_user) for a in accounts]


@router.post("/accounts", response_model=AccountOut)
async def create_account(
    body: AccountCreate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> AccountOut:
    """创建账号（管理员/开发者）。开发者可指定目标帮会，管理员默认本帮会。"""
    if current_user.role == "developer":
        target_guild_id = body.guild_id
    else:
        if current_user.guild_id is None:
            raise ConfigServiceError("当前账号未绑定帮会", 403)
        if body.guild_id is not None and body.guild_id != current_user.guild_id:
            raise ConfigServiceError("无权限为其他帮会创建账号", 403)
        target_guild_id = current_user.guild_id
    account = await account_service.create_account(session, target_guild_id, body.username, body.password, body.role)
    return _build_account_out(account, current_user)


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
    return _build_account_out(account, current_user)


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

    account = await account_service.update_account_status(session, current_user.guild_id, user_id, body.status)
    return _build_account_out(account, current_user)


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

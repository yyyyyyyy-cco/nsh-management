"""系统配置接口：职业配置、账号管理、帮会管理。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin, require_developer
from app.core.database import get_db
from app.models.user import User
from app.schemas.config import (
    AccountCreate,
    AccountOut,
    AccountStatusUpdate,
    AccountUpdate,
    GuildCreate,
    GuildIconUpdate,
    GuildOut,
    GuildRename,
    ProfessionConfigBatchUpdate,
    ProfessionConfigOut,
    ProfessionConfigUpdate,
)
from app.services import config_service

router = APIRouter(prefix="/config", tags=["系统配置"])


# ========== 职业配置 ==========

@router.get("/professions", response_model=list[ProfessionConfigOut])
async def get_profession_configs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ProfessionConfigOut]:
    """获取职业配置列表。"""
    configs = await config_service.get_profession_configs(session, current_user.guild_id)
    # 缺失职业为未落库的默认配置（GET 不写库）：补 id 展示占位，首次批量保存时才会真正插入
    for c in configs:
        if c.id is None:
            c.id = 0
    return [ProfessionConfigOut.model_validate(c) for c in configs]


@router.put("/professions/{profession}", response_model=ProfessionConfigOut)
async def update_profession_config(
    profession: str,
    body: ProfessionConfigUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ProfessionConfigOut:
    """更新单个职业的目标人数（管理员）。"""
    config = await config_service.update_profession_config(
        session, current_user.guild_id, profession, body.target_count
    )
    return ProfessionConfigOut.model_validate(config)


@router.put("/professions", response_model=dict)
async def batch_update_profession_configs(
    body: ProfessionConfigBatchUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """批量更新职业配置（管理员）。"""
    count = await config_service.batch_update_profession_configs(
        session, current_user.guild_id, body.configs
    )
    return {"message": f"已更新 {count} 个职业配置"}


# ========== 账号管理 ==========

@router.get("/accounts", response_model=list[AccountOut])
async def list_accounts(
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[AccountOut]:
    """获取账号列表（管理员）。"""
    accounts = await config_service.list_accounts(session, current_user.guild_id)
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
    account = await config_service.create_account(
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
    account = await config_service.update_account(
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
        raise config_service.ConfigServiceError("不能禁用当前登录的账号")

    account = await config_service.update_account_status(
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
        raise config_service.ConfigServiceError("不能删除当前登录的账号")

    await config_service.delete_account(session, current_user.guild_id, user_id)
    return {"message": "账号已删除"}


# ========== 帮会管理 ==========

@router.get("/guilds", response_model=list[GuildOut])
async def list_guilds(
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> list[GuildOut]:
    """获取帮会列表（仅开发者）。"""
    return await config_service.list_guilds(session)


@router.post("/guilds", response_model=GuildOut)
async def create_guild(
    body: GuildCreate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """创建帮会，并自动生成管理员和帮众账号（初始密码由创建者指定，仅开发者）。"""
    return await config_service.create_guild(session, body.name, body.admin_password, body.member_password)


@router.delete("/guilds/{guild_id}", response_model=dict)
async def delete_guild(
    guild_id: int,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """删除帮会及其全部关联数据（仅开发者）。"""
    await config_service.delete_guild(session, guild_id)
    return {"message": "帮会已删除"}


@router.put("/guilds/{guild_id}", response_model=GuildOut)
async def rename_guild(
    guild_id: int,
    body: GuildRename,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """帮会更名（仅开发者）。"""
    guild = await config_service.rename_guild(session, guild_id, body.name)
    return GuildOut.model_validate(guild)


@router.put("/guilds/{guild_id}/icon", response_model=GuildOut)
async def update_guild_icon(
    guild_id: int,
    body: GuildIconUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """设置本帮会图标字（管理员，仅限自己所属帮会）。"""
    if current_user.guild_id != guild_id:
        from app.services.config_service import ConfigServiceError

        raise ConfigServiceError("只能设置自己所属帮会的图标", 403)
    guild = await config_service.update_guild_icon(session, guild_id, body.icon_char)
    return GuildOut.model_validate(guild)

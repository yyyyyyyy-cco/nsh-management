"""系统配置接口：帮会管理（自 config.py 拆出，URL 前缀不变）。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin, require_developer
from app.core.database import get_db
from app.models.user import User
from app.schemas.config import GuildCreate, GuildIconUpdate, GuildOut, GuildRename
from app.services import guild_service
from app.services.config_service import ConfigServiceError

router = APIRouter(prefix="/config", tags=["系统配置"])


# ========== 帮会管理 ==========


@router.get("/guilds", response_model=list[GuildOut])
async def list_guilds(
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> list[GuildOut]:
    """获取帮会列表（仅开发者）。"""
    return [GuildOut.model_validate(g) for g in await guild_service.list_guilds(session)]


@router.post("/guilds", response_model=GuildOut)
async def create_guild(
    body: GuildCreate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """创建帮会，并自动生成管理员和帮众账号（初始密码由创建者指定，仅开发者）。"""
    return GuildOut.model_validate(
        await guild_service.create_guild(session, body.name, body.admin_password, body.member_password)
    )


@router.delete("/guilds/{guild_id}", response_model=dict)
async def delete_guild(
    guild_id: int,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """删除帮会及其全部关联数据（仅开发者）。"""
    await guild_service.delete_guild(session, guild_id)
    return {"message": "帮会已删除"}


@router.put("/guilds/{guild_id}", response_model=GuildOut)
async def rename_guild(
    guild_id: int,
    body: GuildRename,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """帮会更名（仅开发者）。"""
    guild = await guild_service.rename_guild(session, guild_id, body.name)
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
        raise ConfigServiceError("只能设置自己所属帮会的图标", 403)
    guild = await guild_service.update_guild_icon(session, guild_id, body.icon_char)
    return GuildOut.model_validate(guild)

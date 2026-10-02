"""开发者接口：创建帮会、派发账号。"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_developer
from app.core.database import get_db
from app.models.user import User
from app.schemas.config import AccountCreate, AccountOut, GuildCreate, GuildOut
from app.services import account_service, guild_service

router = APIRouter(prefix="/developer", tags=["开发者"])


@router.post("/guilds", response_model=GuildOut)
async def create_guild(
    body: GuildCreate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> GuildOut:
    """创建帮会，并自动生成管理员和帮众账号（初始密码由创建者指定，仅开发者）。"""
    guild = await guild_service.create_guild(session, body.name, body.admin_password, body.member_password)
    return GuildOut.model_validate(guild)


@router.post("/guilds/{guild_id}/accounts", response_model=AccountOut)
async def create_account_for_guild(
    guild_id: int,
    body: AccountCreate,
    current_user: User = Depends(require_developer),
    session: AsyncSession = Depends(get_db),
) -> AccountOut:
    """为指定帮会创建账号（仅开发者）。"""
    account = await account_service.create_account(session, guild_id, body.username, body.password, body.role)
    return AccountOut.model_validate(account)

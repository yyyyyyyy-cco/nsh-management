"""系统配置业务：职业配置、账号管理、帮会管理。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.guild import Guild
from app.models.profession import ProfessionConfig
from app.models.user import User
from app.utils.constants import PROFESSIONS


class ConfigServiceError(Exception):
    """系统配置业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ========== 职业配置 ==========

async def get_profession_configs(session: AsyncSession, guild_id: int) -> list[ProfessionConfig]:
    """获取帮会的职业配置列表。"""
    configs = list(
        (
            await session.execute(
                select(ProfessionConfig)
                .where(ProfessionConfig.guild_id == guild_id)
                .order_by(ProfessionConfig.profession)
            )
        )
        .scalars()
        .all()
    )

    # 如果缺少某些职业的配置，自动创建默认配置
    existing_professions = {c.profession for c in configs}
    for profession in PROFESSIONS:
        if profession not in existing_professions:
            config = ProfessionConfig(
                guild_id=guild_id,
                profession=profession,
                target_count=0,
            )
            session.add(config)
            configs.append(config)

    if any(c.id is None for c in configs):
        await session.commit()
        for c in configs:
            if c.id is None:
                await session.refresh(c)

    return configs


async def update_profession_config(
    session: AsyncSession, guild_id: int, profession: str, target_count: int
) -> ProfessionConfig:
    """更新单个职业的目标人数。"""
    if profession not in PROFESSIONS:
        raise ConfigServiceError(f"无效的职业：{profession}")

    config = (
        await session.execute(
            select(ProfessionConfig).where(
                ProfessionConfig.guild_id == guild_id,
                ProfessionConfig.profession == profession,
            )
        )
    ).scalar_one_or_none()

    if config is None:
        config = ProfessionConfig(
            guild_id=guild_id,
            profession=profession,
            target_count=target_count,
        )
        session.add(config)
    else:
        config.target_count = target_count

    await session.commit()
    await session.refresh(config)
    return config


async def batch_update_profession_configs(
    session: AsyncSession, guild_id: int, configs_data: list[dict]
) -> int:
    """批量更新职业配置。"""
    count = 0
    for item in configs_data:
        profession = item.get("profession")
        target_count = item.get("target_count", 0)

        if profession not in PROFESSIONS:
            continue

        await update_profession_config(session, guild_id, profession, target_count)
        count += 1

    return count


# ========== 账号管理 ==========

async def list_accounts(session: AsyncSession, guild_id: int) -> list[User]:
    """获取帮会的账号列表。"""
    return list(
        (
            await session.execute(
                select(User)
                .where(User.guild_id == guild_id)
                .order_by(User.role.desc(), User.username)
            )
        )
        .scalars()
        .all()
    )


async def create_account(
    session: AsyncSession, guild_id: int, username: str, password: str, role: str = "member"
) -> User:
    """创建账号。"""
    if role not in ["admin", "member"]:
        raise ConfigServiceError("无效的角色")

    # 检查用户名是否已存在
    existing = (
        await session.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"用户名「{username}」已存在")

    user = User(
        guild_id=guild_id,
        username=username,
        password_hash=hash_password(password),
        role=role,
        status="active",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_account(
    session: AsyncSession, guild_id: int, user_id: int, username: str | None, password: str | None
) -> User:
    """更新账号信息。"""
    user = await session.get(User, user_id)
    if user is None or user.guild_id != guild_id:
        raise ConfigServiceError("账号不存在", 404)

    if username is not None:
        # 检查新用户名是否已存在
        existing = (
            await session.execute(
                select(User).where(User.username == username, User.id != user_id)
            )
        ).scalar_one_or_none()
        if existing:
            raise ConfigServiceError(f"用户名「{username}」已存在")
        user.username = username

    if password is not None:
        user.password_hash = hash_password(password)

    await session.commit()
    await session.refresh(user)
    return user


async def update_account_status(
    session: AsyncSession, guild_id: int, user_id: int, status: str
) -> User:
    """更新账号状态（启用/禁用）。"""
    if status not in ["active", "disabled"]:
        raise ConfigServiceError("无效的状态")

    user = await session.get(User, user_id)
    if user is None or user.guild_id != guild_id:
        raise ConfigServiceError("账号不存在", 404)

    # 不允许禁用自己
    # 这个检查需要在 API 层进行，因为 Service 层不知道当前用户

    user.status = status
    await session.commit()
    await session.refresh(user)
    return user


# ========== 帮会管理 ==========

async def list_guilds(session: AsyncSession) -> list[Guild]:
    """获取所有帮会列表（超级管理员功能）。"""
    return list(
        (await session.execute(select(Guild).order_by(Guild.name))).scalars().all()
    )


async def create_guild(session: AsyncSession, name: str) -> Guild:
    """创建帮会，并自动生成管理员和帮众账号。"""
    # 检查帮会名是否已存在
    existing = (
        await session.execute(select(Guild).where(Guild.name == name))
    ).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"帮会「{name}」已存在")

    guild = Guild(name=name)
    session.add(guild)
    await session.flush()

    # 创建管理员账号
    admin_user = User(
        guild_id=guild.id,
        username=f"{name}_admin",
        password_hash=hash_password("123456"),  # 默认密码
        role="admin",
        status="active",
    )
    session.add(admin_user)

    # 创建帮众账号
    member_user = User(
        guild_id=guild.id,
        username=f"{name}_member",
        password_hash=hash_password("123456"),  # 默认密码
        role="member",
        status="active",
    )
    session.add(member_user)

    # 初始化职业配置
    for profession in PROFESSIONS:
        config = ProfessionConfig(
            guild_id=guild.id,
            profession=profession,
            target_count=0,
        )
        session.add(config)

    await session.commit()
    await session.refresh(guild)
    return guild

"""系统配置业务：职业配置、账号管理、帮会管理。"""
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.match_data import MatchData
from app.models.member import Member
from app.models.profession import ProfessionConfig
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.models.user import User
from app.utils.constants import PROFESSIONS


class ConfigServiceError(Exception):
    """系统配置业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


# ========== 职业配置 ==========

async def get_profession_configs(session: AsyncSession, guild_id: int | None) -> list[ProfessionConfig]:
    """获取帮会的职业配置列表。开发者账号无帮会时返回空列表。"""
    if guild_id is None:
        return []

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
    session: AsyncSession, guild_id: int | None, profession: str, target_count: int, remark: str | None = None
) -> ProfessionConfig:
    """更新单个职业的目标人数与说明。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")
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
            remark=remark,
        )
        session.add(config)
    else:
        config.target_count = target_count
        config.remark = remark

    await session.commit()
    await session.refresh(config)
    return config


async def batch_update_profession_configs(
    session: AsyncSession, guild_id: int | None, configs_data: list[dict]
) -> int:
    """批量更新职业配置。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")
    count = 0
    for item in configs_data:
        profession = item.get("profession")
        target_count = item.get("target_count", 0)
        remark = item.get("remark")

        if profession not in PROFESSIONS:
            continue

        await update_profession_config(session, guild_id, profession, target_count, remark)
        count += 1

    return count


# ========== 账号管理 ==========

async def list_accounts(session: AsyncSession, guild_id: int | None) -> list[User]:
    """获取帮会的账号列表。开发者可查看所有账号。"""
    stmt = select(User).order_by(User.role.desc(), User.username)
    if guild_id is not None:
        stmt = stmt.where(User.guild_id == guild_id)
    return list((await session.execute(stmt)).scalars().all())


async def create_account(
    session: AsyncSession, target_guild_id: int | None, username: str, password: str, role: str = "member"
) -> User:
    """创建账号。target_guild_id 为目标帮会（admin 用自身帮会，developer 用表单指定帮会）。"""
    if target_guild_id is None:
        raise ConfigServiceError("请选择目标帮会后再创建账号")
    if role not in ["admin", "member"]:
        raise ConfigServiceError("无效的角色")

    # 检查用户名是否已存在
    existing = (
        await session.execute(select(User).where(User.username == username))
    ).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"用户名「{username}」已存在")

    user = User(
        guild_id=target_guild_id,
        username=username,
        password_hash=hash_password(password),
        plain_password=password,
        role=role,
        status="active",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_account(
    session: AsyncSession, guild_id: int | None, user_id: int, username: str | None, password: str | None
) -> User:
    """更新账号信息。"""
    user = await session.get(User, user_id)
    if user is None:
        raise ConfigServiceError("账号不存在", 404)
    if guild_id is not None and user.guild_id != guild_id:
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
        user.plain_password = password

    await session.commit()
    await session.refresh(user)
    return user


async def update_account_status(
    session: AsyncSession, guild_id: int | None, user_id: int, status: str
) -> User:
    """更新账号状态（启用/禁用）。"""
    if status not in ["active", "disabled"]:
        raise ConfigServiceError("无效的状态")

    user = await session.get(User, user_id)
    if user is None:
        raise ConfigServiceError("账号不存在", 404)
    if guild_id is not None and user.guild_id != guild_id:
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
    admin_password = "123456"
    admin_user = User(
        guild_id=guild.id,
        username=f"{name}_admin",
        password_hash=hash_password(admin_password),
        plain_password=admin_password,
        role="admin",
        status="active",
    )
    session.add(admin_user)

    # 创建帮众账号
    member_password = "123456"
    member_user = User(
        guild_id=guild.id,
        username=f"{name}_member",
        password_hash=hash_password(member_password),
        plain_password=member_password,
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


async def delete_account(session: AsyncSession, guild_id: int | None, user_id: int) -> None:
    """删除账号（不能删除开发者账号）。"""
    user = await session.get(User, user_id)
    if user is None:
        raise ConfigServiceError("账号不存在", 404)
    if guild_id is not None and user.guild_id != guild_id:
        raise ConfigServiceError("账号不存在", 404)
    if user.role == "developer":
        raise ConfigServiceError("不能删除开发者账号")

    await session.delete(user)
    await session.commit()


async def delete_guild(session: AsyncSession, guild_id: int) -> None:
    """删除帮会，级联删除其全部关联数据（账号/成员/赛程/出勤/排表/录屏/数据/职业配置）。"""
    guild = await session.get(Guild, guild_id)
    if guild is None:
        raise ConfigServiceError("帮会不存在", 404)

    # 该帮会全部赛程下的子表数据
    schedule_ids = list(
        (await session.execute(select(Schedule.id).where(Schedule.guild_id == guild_id))).scalars().all()
    )
    if schedule_ids:
        await session.execute(delete(Recording).where(Recording.schedule_id.in_(schedule_ids)))
        await session.execute(delete(AttendanceRecord).where(AttendanceRecord.schedule_id.in_(schedule_ids)))
        await session.execute(delete(Lineup).where(Lineup.schedule_id.in_(schedule_ids)))
        await session.execute(delete(MatchData).where(MatchData.schedule_id.in_(schedule_ids)))
        await session.execute(delete(Schedule).where(Schedule.guild_id == guild_id))

    await session.execute(delete(Member).where(Member.guild_id == guild_id))
    await session.execute(delete(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id))
    await session.execute(delete(User).where(User.guild_id == guild_id))
    await session.delete(guild)
    await session.commit()

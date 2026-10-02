"""帮会管理业务：列表、创建（含初始账号与职业配置）、删除、更名、图标。

由 config_service 拆出；异常沿用 ConfigServiceError。
"""
import asyncio

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.password_policy import PasswordPolicyError, validate_password
from app.core.security import hash_password
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.match_data import MatchData
from app.models.member import Member
from app.models.profession import ProfessionConfig
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.models.squad_adjustment import SquadAdjustment
from app.models.user import User
from app.services.config_service import ConfigServiceError
from app.services.game_id_request_lifecycle import purge_guild
from app.utils.constants import PROFESSIONS


async def list_guilds(session: AsyncSession) -> list[Guild]:
    """获取所有帮会列表（超级管理员功能）。"""
    return list(
        (await session.execute(select(Guild).order_by(Guild.name))).scalars().all()
    )


async def create_guild(
    session: AsyncSession, name: str, admin_password: str, member_password: str
) -> Guild:
    """创建帮会，并自动生成管理员和帮众账号（初始密码由创建者指定）。"""
    # 检查帮会名是否已存在
    existing = (
        await session.execute(select(Guild).where(Guild.name == name))
    ).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"帮会「{name}」已存在")

    guild = Guild(name=name)
    session.add(guild)
    await session.flush()

    # 服务层口令兜底（2026-10-03，见 F-88）：schema 之外的调用也要受口令策略约束。
    for _password in (admin_password, member_password):
        try:
            validate_password(_password)
        except PasswordPolicyError as exc:
            raise ConfigServiceError(str(exc)) from exc

    # bcrypt 哈希为 CPU 密集操作：两个初始密码哈希并行放线程池，避免阻塞事件循环
    admin_hash, member_hash = await asyncio.gather(
        asyncio.to_thread(hash_password, admin_password),
        asyncio.to_thread(hash_password, member_password),
    )

    # 创建管理员账号（初始密码由创建者指定）
    admin_user = User(
        guild_id=guild.id,
        username=f"{name}_admin",
        password_hash=admin_hash,
        plain_password=admin_password,
        role="admin",
        status="active",
    )
    session.add(admin_user)

    # 创建帮众账号（初始密码由创建者指定）
    member_user = User(
        guild_id=guild.id,
        username=f"{name}_member",
        password_hash=member_hash,
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


async def delete_guild(session: AsyncSession, guild_id: int) -> None:
    """删除帮会，级联删除其全部关联数据（账号/成员/赛程/出勤/排表/录屏/分析数据/分析调整/职业配置/改名申请）。"""
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
        # 分析调整副本：与 delete_schedule 同源的遗漏（2026-10-03 修复，见 F-77）；
        # 不清会留孤儿行，且 schedules.id 可能被复用 → 新赛程继承旧分析调整
        await session.execute(delete(SquadAdjustment).where(SquadAdjustment.schedule_id.in_(schedule_ids)))
        await session.execute(delete(Schedule).where(Schedule.guild_id == guild_id))

    await session.execute(delete(Member).where(Member.guild_id == guild_id))
    # 改名申请先于成员/账号删除（成员、账号删除后其引用会被置空，记录不再可清理）
    await purge_guild(session, guild_id)
    await session.execute(delete(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id))
    await session.execute(delete(User).where(User.guild_id == guild_id))
    await session.delete(guild)
    await session.commit()


async def rename_guild(session: AsyncSession, guild_id: int, name: str) -> Guild:
    """帮会更名（仅开发者）。"""
    guild = await session.get(Guild, guild_id)
    if guild is None:
        raise ConfigServiceError("帮会不存在", 404)
    existing = (
        await session.execute(select(Guild).where(Guild.name == name, Guild.id != guild_id))
    ).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"帮会「{name}」已存在")
    guild.name = name
    await session.commit()
    await session.refresh(guild)
    return guild


async def update_guild_icon(session: AsyncSession, guild_id: int, icon_char: str) -> Guild:
    """设置帮会图标字（管理员，仅本帮会）。空串清除。"""
    guild = await session.get(Guild, guild_id)
    if guild is None:
        raise ConfigServiceError("帮会不存在", 404)
    guild.icon_char = icon_char.strip() or None
    await session.commit()
    await session.refresh(guild)
    return guild

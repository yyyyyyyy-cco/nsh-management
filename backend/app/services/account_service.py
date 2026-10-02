"""账号管理业务：列表、创建、更新、状态切换与删除。

由 config_service 拆出；异常沿用 ConfigServiceError。
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.guild import Guild
from app.models.user import User
from app.services.config_service import ConfigServiceError
from app.services.game_id_request_lifecycle import detach_user


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
    if target_guild_id < 1 or await session.get(Guild, target_guild_id) is None:
        raise ConfigServiceError("目标帮会不存在", 404)

    # 检查用户名是否已存在
    existing = (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()
    if existing:
        raise ConfigServiceError(f"用户名「{username}」已存在")

    user = User(
        guild_id=target_guild_id,
        username=username,
        # bcrypt 哈希为 CPU 密集操作（约 170ms/次），放线程池避免阻塞事件循环
        password_hash=await asyncio.to_thread(hash_password, password),
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
            await session.execute(select(User).where(User.username == username, User.id != user_id))
        ).scalar_one_or_none()
        if existing:
            raise ConfigServiceError(f"用户名「{username}」已存在")
        user.username = username

    if password is not None:
        # bcrypt 哈希为 CPU 密集操作，放线程池避免阻塞事件循环
        user.password_hash = await asyncio.to_thread(hash_password, password)
        user.plain_password = password
        # 改密后吊销该账号所有已签发 Token（旧 Token 立即失效）
        user.token_version += 1

    await session.commit()
    await session.refresh(user)
    return user


async def update_account_status(session: AsyncSession, guild_id: int | None, user_id: int, status: str) -> User:
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


async def delete_account(session: AsyncSession, guild_id: int | None, user_id: int) -> None:
    """删除账号（不能删除开发者账号）。"""
    user = await session.get(User, user_id)
    if user is None:
        raise ConfigServiceError("账号不存在", 404)
    if guild_id is not None and user.guild_id != guild_id:
        raise ConfigServiceError("账号不存在", 404)
    if user.role == "developer":
        raise ConfigServiceError("不能删除开发者账号")

    # 账号删除：清空改名申请的申请人/审核人引用（保留账号名快照），同事务提交
    await detach_user(session, user_id)
    await session.delete(user)
    await session.commit()

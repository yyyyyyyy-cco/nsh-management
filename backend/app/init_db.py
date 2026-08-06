"""初始化数据：创建默认帮会及管理员/帮众账号。

用法：python -m app.init_db
（需先执行 alembic upgrade head 完成建表）
"""
import asyncio

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models import Guild, User

DEFAULT_GUILD = "默认帮会"
DEFAULT_ADMIN = ("admin", "admin123")
DEFAULT_MEMBER = ("member", "member123")


async def init() -> None:
    async with async_session_factory() as session:
        guild = (await session.execute(select(Guild).where(Guild.name == DEFAULT_GUILD))).scalar_one_or_none()
        if guild is None:
            guild = Guild(name=DEFAULT_GUILD)
            session.add(guild)
            await session.flush()

        if (await session.execute(select(User).where(User.username == DEFAULT_ADMIN[0]))).scalar_one_or_none() is None:
            session.add(
                User(
                    guild_id=guild.id,
                    username=DEFAULT_ADMIN[0],
                    password_hash=hash_password(DEFAULT_ADMIN[1]),
                    role="admin",
                )
            )
        if (await session.execute(select(User).where(User.username == DEFAULT_MEMBER[0]))).scalar_one_or_none() is None:
            session.add(
                User(
                    guild_id=guild.id,
                    username=DEFAULT_MEMBER[0],
                    password_hash=hash_password(DEFAULT_MEMBER[1]),
                    role="member",
                )
            )
        await session.commit()
        print(f"初始化完成：帮会「{DEFAULT_GUILD}」，账号 {DEFAULT_ADMIN[0]}/{DEFAULT_ADMIN[1]}（管理员）、{DEFAULT_MEMBER[0]}/{DEFAULT_MEMBER[1]}（帮众）")


if __name__ == "__main__":
    asyncio.run(init())

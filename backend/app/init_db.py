"""初始化数据：创建开发者账号及默认帮会。

用法：python -m app.init_db
（需先执行 alembic upgrade head 完成建表）

环境变量：
  DEVELOPER_USERNAME - 开发者用户名（可选，默认"developer"）
  DEVELOPER_PASSWORD - 开发者密码（必填，首次运行时设置）
  DEFAULT_GUILD_NAME - 默认帮会名称（可选，默认"默认帮会"）
  ADMIN_USERNAME     - 管理员用户名（可选，默认"admin"）
  ADMIN_PASSWORD     - 管理员密码（必填，首次运行时设置）
  MEMBER_USERNAME    - 帮众用户名（可选，默认"member"）
  MEMBER_PASSWORD    - 帮众密码（必填，首次运行时设置）
"""
import asyncio
import os
import sys

from sqlalchemy import select

from app.core.database import async_session_factory
from app.core.security import hash_password
from app.models import Guild, User

DEVELOPER_USERNAME = os.getenv("DEVELOPER_USERNAME", "developer")
DEVELOPER_PASSWORD = os.getenv("DEVELOPER_PASSWORD")
DEFAULT_GUILD_NAME = os.getenv("DEFAULT_GUILD_NAME", "默认帮会")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
MEMBER_USERNAME = os.getenv("MEMBER_USERNAME", "member")
MEMBER_PASSWORD = os.getenv("MEMBER_PASSWORD")


async def init() -> None:
    if not DEVELOPER_PASSWORD or not ADMIN_PASSWORD or not MEMBER_PASSWORD:
        print("错误：请设置环境变量 DEVELOPER_PASSWORD、ADMIN_PASSWORD 和 MEMBER_PASSWORD")
        sys.exit(1)

    async with async_session_factory() as session:
        # 创建开发者账号（不绑定帮会）
        if (await session.execute(select(User).where(User.username == DEVELOPER_USERNAME))).scalar_one_or_none() is None:
            session.add(
                User(
                    guild_id=None,
                    username=DEVELOPER_USERNAME,
                    password_hash=hash_password(DEVELOPER_PASSWORD),
                    role="developer",
                )
            )
            print(f"创建开发者账号：{DEVELOPER_USERNAME}")

        # 创建默认帮会
        guild = (await session.execute(select(Guild).where(Guild.name == DEFAULT_GUILD_NAME))).scalar_one_or_none()
        if guild is None:
            guild = Guild(name=DEFAULT_GUILD_NAME)
            session.add(guild)
            await session.flush()
            print(f"创建默认帮会：{DEFAULT_GUILD_NAME}")

        # 创建管理员账号
        if (await session.execute(select(User).where(User.username == ADMIN_USERNAME))).scalar_one_or_none() is None:
            session.add(
                User(
                    guild_id=guild.id,
                    username=ADMIN_USERNAME,
                    password_hash=hash_password(ADMIN_PASSWORD),
                    role="admin",
                )
            )
            print(f"创建管理员账号：{ADMIN_USERNAME}")

        # 创建帮众账号
        if (await session.execute(select(User).where(User.username == MEMBER_USERNAME))).scalar_one_or_none() is None:
            session.add(
                User(
                    guild_id=guild.id,
                    username=MEMBER_USERNAME,
                    password_hash=hash_password(MEMBER_PASSWORD),
                    role="member",
                )
            )
            print(f"创建帮众账号：{MEMBER_USERNAME}")

        await session.commit()
        print(f"\n初始化完成！")
        print(f"开发者：{DEVELOPER_USERNAME}（可创建帮会、派发账号）")
        print(f"帮会「{DEFAULT_GUILD_NAME}」：{ADMIN_USERNAME}（管理员）、{MEMBER_USERNAME}（帮众）")


if __name__ == "__main__":
    asyncio.run(init())

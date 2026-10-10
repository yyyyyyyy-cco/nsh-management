"""测试公共基类与工具（W2-2）。

`DbTestCase` 提供：
- 内存 SQLite 引擎（每个用例独立，互不污染）
- 已 create_all 的 schema
- 一个 AsyncSession（用例可直接用）
可选地通过 `seed_users()` 播种角色矩阵所需的账号。

刻意不引入 pytest-asyncio：异步用例继承 `unittest.IsolatedAsyncioTestCase` 即可被 pytest 收集，
与既有 `backend/scripts/selfcheck_*.py` 保持同一风格，降低测试工具链的额外依赖。
"""

from __future__ import annotations

import unittest

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.core.security import create_access_token
from app.models.guild import Guild
from app.models.profession import Profession
from app.models.user import User

# 角色矩阵：与 design-document-v2 §3 的权限定义对应
SEED_USERS = (
    # (id, username, role, guild_id)
    (1, "admin_bound", "admin", 1),
    (2, "dev", "developer", None),
    (3, "member_bound", "member", 1),
    (4, "admin_unbound", "admin", None),
    (5, "disabled_admin", "admin", 1),
)

# 职业目录种子（与迁移 q1r2s3t4u5v6 的 SEED 逐字段一致）：测试基座默认播种，
# 因为成员/出勤/职业配置/Excel 导入等校验自本次迭代起均以目录为准
PROFESSION_SEED: tuple[tuple[str, int, str], ...] = (
    ("铁衣", 1, "#ffc800"),
    ("素问", 2, "#FF9CF2"),
    ("神相", 3, "#3E6BF4"),
    ("碎梦", 4, "#00FFFB"),
    ("血河", 5, "#F04545"),
    ("玄机", 6, "#f6ff00"),
    ("九灵", 7, "#8B5CF6"),
    ("潮光", 8, "#4F95FF"),
    ("龙吟", 9, "#3fe155"),
    ("鸿音", 10, "#C6834D"),
    ("沧澜", 11, "#605EF0"),
)


def profession_seed_rows() -> list[Profession]:
    """职业目录种子行（与迁移种子一致）。"""
    return [Profession(name=name, sort_order=order, color=color) for name, order, color in PROFESSION_SEED]


class DbTestCase(unittest.IsolatedAsyncioTestCase):
    """内存库 + 最小数据集的异步用例基类。"""

    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session: AsyncSession = async_sessionmaker(self.engine, expire_on_commit=False)()
        # 职业目录默认播种：职业相关的服务校验依赖目录存在（与迁移种子一致）
        self.session.add_all(profession_seed_rows())
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def seed_users(self) -> dict[int, User]:
        """播种帮会与角色矩阵账号，返回 {user_id: User}。"""
        self.session.add_all([Guild(id=1, name="测试帮会")])
        await self.session.flush()
        users: dict[int, User] = {}
        for uid, username, role, gid in SEED_USERS:
            user = User(
                id=uid,
                username=username,
                role=role,
                guild_id=gid,
                password_hash="unused-in-tests",
                status="disabled" if username.startswith("disabled") else "active",
                token_version=0,
            )
            self.session.add(user)
            users[uid] = user
        await self.session.commit()
        return users

    @staticmethod
    def token_for(user: User) -> str:
        """签发与账号 token_version 一致的访问令牌。"""
        return create_access_token(user.id, user.role, user.token_version)

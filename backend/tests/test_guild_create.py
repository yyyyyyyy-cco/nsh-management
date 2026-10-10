"""帮会创建路径的回归测试（F-88）。

`create_guild` 此前**没有任何测试**。本文件锁定：
- 单次事务创建：帮会 + 管理员账号 + 帮众账号 + **全部职业配置（target_count=0）**；
- 账号命名（`{帮会名}_admin` / `{帮会名}_member`）、角色、状态与 `guild_id` 绑定；
- 初始密码以 **bcrypt 哈希**落库（明文列 `plain_password` 属已接受风险，见 security-review）；
- **原子性**：中途失败（如账号名冲突）必须整体回滚，不留半个帮会；
- 帮会重名 → 业务错误；
- 初始密码受口令策略约束（schema 层；service 层另有兜底）。
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from support import PROFESSION_SEED, profession_seed_rows

from app.core.database import Base
from app.core.password_policy import PasswordPolicyError
from app.core.security import verify_password
from app.models.guild import Guild
from app.models.profession import ProfessionConfig
from app.models.user import User
from app.schemas.config import GuildCreate
from app.services import guild_service
from app.services.config_service import ConfigServiceError

STRONG = "Tq7#vLm2Zr9p"


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        # 职业目录种子：create_guild 按启用目录初始化职业配置
        self.session.add_all(profession_seed_rows())
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _count(self, model) -> int:
        return (await self.session.execute(select(func.count()).select_from(model))).scalar()


class GuildCreateSchemaTest(unittest.TestCase):
    def test_name_length_and_password_policy(self) -> None:
        with self.assertRaises((ValidationError, PasswordPolicyError)):
            GuildCreate(name="甲", admin_password=STRONG, member_password=STRONG)  # 名称过短
        with self.assertRaises((ValidationError, PasswordPolicyError)):
            # 常见弱口令（CONTEXT_WORDS 内）
            GuildCreate(name="测试帮会", admin_password="admin123", member_password=STRONG)
        with self.assertRaises((ValidationError, PasswordPolicyError)):
            GuildCreate(name="测试帮会", admin_password=STRONG, member_password="member")
        ok = GuildCreate(name="测试帮会", admin_password=STRONG, member_password=STRONG + "x")
        self.assertEqual(ok.name, "测试帮会")


class GuildCreateServiceTest(_Base):
    async def test_creates_guild_accounts_and_profession_configs(self) -> None:
        guild = await guild_service.create_guild(self.session, "帮会甲", STRONG, STRONG + "x")

        users = (
            (await self.session.execute(select(User).where(User.guild_id == guild.id).order_by(User.username)))
            .scalars()
            .all()
        )
        self.assertEqual([u.username for u in users], ["帮会甲_admin", "帮会甲_member"])
        self.assertEqual({u.role for u in users}, {"admin", "member"})
        self.assertEqual({u.status for u in users}, {"active"})

        configs = (
            (await self.session.execute(select(ProfessionConfig).where(ProfessionConfig.guild_id == guild.id)))
            .scalars()
            .all()
        )
        self.assertEqual(len(configs), len(PROFESSION_SEED), "应为全部启用职业建配置")
        self.assertEqual({c.target_count for c in configs}, {0})

    async def test_passwords_hashed_and_verifiable(self) -> None:
        guild = await guild_service.create_guild(self.session, "帮会乙", STRONG, STRONG)
        admin = (
            (await self.session.execute(select(User).where(User.guild_id == guild.id, User.role == "admin")))
            .scalars()
            .one()
        )
        member = (
            (await self.session.execute(select(User).where(User.guild_id == guild.id, User.role == "member")))
            .scalars()
            .one()
        )
        self.assertTrue(verify_password(STRONG, admin.password_hash), "哈希应可校验原口令")
        self.assertNotEqual(admin.password_hash, STRONG, "不得明文落库")
        self.assertTrue(admin.password_hash.startswith("sha256$"), "应为 sha256$ 预哈希方案（W1-12 / F-57）")
        self.assertTrue(admin.password_hash[len("sha256$") :].startswith("$2b$"), "预哈希之后应接 bcrypt（$2b$）")
        self.assertNotEqual(admin.password_hash, member.password_hash, "相同口令的哈希应因盐不同而不同")
        self.assertEqual(admin.plain_password, STRONG, "明文列按已接受风险保留")

    async def test_duplicate_guild_name_is_business_error(self) -> None:
        await guild_service.create_guild(self.session, "帮会丙", STRONG, STRONG)
        with self.assertRaises(ConfigServiceError):
            await guild_service.create_guild(self.session, "帮会丙", STRONG, STRONG)
        await self.session.rollback()
        self.assertEqual(await self._count(Guild), 1)

    async def test_failure_rolls_back_entirely(self) -> None:
        """原子性：账号名冲突（非帮会名冲突）时不得留下半个帮会。"""
        self.session.add(User(username="帮会丁_admin", password_hash="x", role="admin", status="active"))
        await self.session.commit()
        with self.assertRaises(Exception):
            await guild_service.create_guild(self.session, "帮会丁", STRONG, STRONG)
        await self.session.rollback()
        self.assertEqual(await self._count(Guild), 0, "帮会不得残留")
        self.assertEqual(await self._count(User), 1, "只应有预先插入的那个账号")
        self.assertEqual(await self._count(ProfessionConfig), 0, "职业配置不得残留")

    async def test_service_level_password_policy_fallback(self) -> None:
        """schema 之外的调用也要被拦住（服务层兜底）。"""
        with self.assertRaises(ConfigServiceError):
            await guild_service.create_guild(self.session, "帮会戊", "admin123", STRONG)
        await self.session.rollback()
        self.assertEqual(await self._count(Guild), 0)


if __name__ == "__main__":
    unittest.main()

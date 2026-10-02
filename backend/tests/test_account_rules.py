"""账号管理安全行为的回归测试（F-89）。

`selfcheck_security_fixes.py` 已覆盖**帮会边界**（管理员不得为他帮会建号 403、开发者须指定有效目标帮会、
未绑定帮会者不得建号、成员/匿名被拒）——**本文件不重复**。

本文件补的是**尚未被任何测试覆盖**的两组安全行为：
- **白名单**：`create_account` 只接受 `admin` / `member`（传 `developer` 必须被拒，防提权 ✗）；
  `update_account_status` 只接受 `active` / `disabled`；**不能删除开发者账号**；
- **明文脱敏**：`plain_password` 仅对 `developer` 返回，`admin` / `member` 一律置 `None`
  （见 `security-review.md` 的已定方案）；
- 顺带锁定：管理员对**他帮会**账号的更新/删除按「账号不存在」处理（服务层 `guild_id` 过滤）。
"""
from __future__ import annotations

import unittest
from types import SimpleNamespace

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1.accounts import _build_account_out, list_accounts
from app.core.database import Base
from app.models.guild import Guild
from app.models.user import User
from app.services import account_service
from app.services.config_service import ConfigServiceError

STRONG = "Tq7#vLm2Zr9p"


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        self.session.add_all([Guild(id=1, name="甲帮"), Guild(id=2, name="乙帮")])
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _count_users(self) -> int:
        return (await self.session.execute(select(func.count()).select_from(User))).scalar()


class AccountServiceRulesTest(_Base):
    async def test_role_whitelist_rejects_developer(self) -> None:
        """防提权：不得通过账号接口创建 developer。"""
        with self.assertRaises(ConfigServiceError):
            await account_service.create_account(self.session, 1, "escalate", STRONG, "developer")
        await self.session.rollback()
        self.assertEqual(await self._count_users(), 0, "被拒的创建不得落库")
        for role in ("admin", "member"):
            user = await account_service.create_account(self.session, 1, f"u_{role}", STRONG, role)
            self.assertEqual(user.role, role)

    async def test_unbound_target_guild_rejected(self) -> None:
        with self.assertRaises(ConfigServiceError):
            await account_service.create_account(self.session, None, "nobody", STRONG, "member")
        await self.session.rollback()

    async def test_status_whitelist(self) -> None:
        user = await account_service.create_account(self.session, 1, "u1", STRONG, "member")
        user_id = user.id  # 回滚会过期实例，先取 id（否则异步下读属性触发懒加载 -> MissingGreenlet）
        with self.assertRaises(ConfigServiceError):
            await account_service.update_account_status(self.session, 1, user_id, "bogus")
        await self.session.rollback()
        updated = await account_service.update_account_status(self.session, 1, user_id, "disabled")
        self.assertEqual(updated.status, "disabled")

    async def test_cannot_delete_developer(self) -> None:
        self.session.add(User(id=99, username="dev", password_hash="x", role="developer", status="active"))
        await self.session.commit()
        with self.assertRaises(ConfigServiceError):
            await account_service.delete_account(self.session, None, 99)
        await self.session.rollback()
        still = (await self.session.execute(select(User).where(User.id == 99))).scalars().one_or_none()
        self.assertIsNotNone(still, "开发者账号不得被删除")

    async def test_admin_cannot_touch_other_guild_account(self) -> None:
        other = await account_service.create_account(self.session, 2, "other", STRONG, "member")
        other_id = other.id  # 同上：回滚前取 id
        with self.assertRaises(ConfigServiceError):
            await account_service.update_account(self.session, 1, other_id, "hacked", None)
        await self.session.rollback()
        with self.assertRaises(ConfigServiceError):
            await account_service.delete_account(self.session, 1, other_id)
        await self.session.rollback()


class AccountDesensitizationTest(_Base):
    async def test_plaintext_hidden_from_admin_and_member(self) -> None:
        user = await account_service.create_account(self.session, 1, "u_admin", STRONG, "admin")
        for role in ("admin", "member"):
            out = _build_account_out(user, SimpleNamespace(role=role, guild_id=1))
            self.assertIsNone(out.plain_password, f"{role} 不应看到明文密码")

    async def test_plaintext_visible_to_developer_and_scope_is_global(self) -> None:
        await account_service.create_account(self.session, 1, "u1", STRONG, "member")
        await account_service.create_account(self.session, 2, "u2", STRONG, "member")
        dev = SimpleNamespace(role="developer", guild_id=None)
        rows = await list_accounts(current_user=dev, session=self.session)
        self.assertEqual(len(rows), 2, "开发者应能看到全部帮会的账号")
        self.assertTrue(all(r.plain_password == STRONG for r in rows), "开发者可见明文（已接受风险）")
        admin_rows = await list_accounts(current_user=SimpleNamespace(role="admin", guild_id=1),
                                         session=self.session)
        self.assertEqual(len(admin_rows), 1, "管理员只看到本帮会账号")
        self.assertIsNone(admin_rows[0].plain_password)


if __name__ == "__main__":
    unittest.main()
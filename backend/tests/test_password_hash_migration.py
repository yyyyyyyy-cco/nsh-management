# -*- coding: utf-8 -*-
"""登录时旧方案哈希的**惰性升级**（合规化计划 W1-12）。

**背景**：2026-10-03 引入 `sha256$` 新方案（先 `base64(SHA-256(口令))` 再 bcrypt，解决 F-57 的 72 字节截断）。
但库内既有哈希**没有前缀**、必须继续可用（否则用户无法登录）。因此登录成功后若发现哈希仍是旧方案，
就用新方案重写一次——用户无感，库内哈希随登录逐步迁移。

**为什么必须有这个文件**：迁移路径是本次改动里最容易"看起来对、实际把人锁在门外"的地方：
- 若升级写错了（比如把口令写成了别的东西）→ 该用户下次登录失败；
- 若把**新方案**哈希也重写 → 白做一次 bcrypt（且会掩盖 bug）。
所以这里同时断言「旧哈希被升级为新方案且仍可校验」与「新方案哈希保持原样」。
"""

import unittest

try:
    import bcrypt

    from app.core.security import _SCHEME_PREFIX, hash_password, verify_password
    from app.services import auth_service
    from app.services.auth_service import AuthError
    from tests.support import DbTestCase
except ImportError as exc:  # pragma: no cover — 无依赖环境
    raise unittest.SkipTest(f"缺少运行依赖（bcrypt），跳过本模块：{exc}") from exc

PASSWORD = "legacy-login-pw-123"


def _legacy_hash(password: str) -> str:
    """构造旧方案哈希：直连 bcrypt、无前缀（等价于 passlib 时代与 W1-10 产出的哈希）。"""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


class PasswordHashMigrationTest(DbTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.users = await self.seed_users()
        auth_service._unknown_login_failures.clear()

    async def _set_hash(self, user_id: int, hashed: str) -> None:
        self.users[user_id].password_hash = hashed
        await self.session.commit()

    async def test_legacy_hash_is_upgraded_on_successful_login(self) -> None:
        user = self.users[1]  # admin_bound，status=active
        await self._set_hash(1, _legacy_hash(PASSWORD))
        self.assertFalse(user.password_hash.startswith(_SCHEME_PREFIX), "前置：应为旧方案哈希")

        token, logged_in = await auth_service.authenticate(self.session, "admin_bound", PASSWORD)

        self.assertTrue(token, "登录应返回令牌")
        self.assertTrue(
            logged_in.password_hash.startswith(_SCHEME_PREFIX),
            "登录成功后，旧方案哈希应被升级为 sha256$ 新方案",
        )
        self.assertTrue(
            verify_password(PASSWORD, logged_in.password_hash),
            "升级后的哈希必须仍能校验同一口令（否则用户下次登录即被锁）",
        )

    async def test_new_scheme_hash_is_not_rewritten(self) -> None:
        original = hash_password(PASSWORD)
        await self._set_hash(1, original)

        _, logged_in = await auth_service.authenticate(self.session, "admin_bound", PASSWORD)

        self.assertEqual(logged_in.password_hash, original, "已是新方案的哈希不应被重写（避免无谓 bcrypt 与掩盖问题）")

    async def test_wrong_password_does_not_upgrade(self) -> None:
        legacy = _legacy_hash(PASSWORD)
        await self._set_hash(1, legacy)

        with self.assertRaises(AuthError):
            await auth_service.authenticate(self.session, "admin_bound", "wrong-password")

        self.assertEqual(self.users[1].password_hash, legacy, "登录失败时不得改动哈希")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

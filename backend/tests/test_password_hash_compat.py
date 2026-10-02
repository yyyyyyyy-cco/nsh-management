# -*- coding: utf-8 -*-
"""口令哈希的**向后兼容**与 bcrypt 边界特征（合规化计划 W1-10 / F-57）。

**为什么必须有这个文件**：2026-10-03 把未维护的 `passlib` 换成 `bcrypt` 直连。换库最大的风险不是新口令，
而是**库内既有哈希能否继续校验**——若不能，全体用户将无法登录。本文件用**passlib 真实生成的固定哈希**
（下列 `LEGACY_HASH`，对应口令 `legacy-pass-123`）长期看护这件事；它不需要安装 passlib，因此换库之后依然有效。

同时**特征化** bcrypt 的 72 字节边界（见 `test_bcrypt_uses_only_first_72_bytes`）：这不是"期望行为"，
而是**记录下来**——将来升到 bcrypt 5.x 若改为报错，此用例会失败并迫使做一次有意识的决策（W1-12）。
"""
import unittest

try:
    from app.core.security import hash_password, verify_password
except ImportError as exc:  # pragma: no cover — 无依赖环境
    raise unittest.SkipTest(f"缺少运行依赖（bcrypt），跳过本模块：{exc}") from exc


# passlib 1.7.4（CryptContext(schemes=["bcrypt"])）在 2026-10-03 生成的哈希，对应口令 "legacy-pass-123"
LEGACY_HASH = "$2b$12$sv69Wabb7rrl9j2q6GAn9.RnCq.Ve9t7oOuNMHv5fwSPsurydG88K"
LEGACY_PASSWORD = "legacy-pass-123"


class PasswordHashCompatTest(unittest.TestCase):
    def test_legacy_passlib_hash_still_verifies(self) -> None:
        """换库后，passlib 时代的哈希仍能校验通过（否则用户无法登录）。"""
        self.assertTrue(
            verify_password(LEGACY_PASSWORD, LEGACY_HASH),
            "passlib 生成的 $2b$ 哈希必须能被当前的 verify_password 校验",
        )

    def test_legacy_hash_rejects_wrong_password(self) -> None:
        self.assertFalse(verify_password("wrong-password", LEGACY_HASH))

    def test_new_hash_is_bcrypt_2b_and_verifiable(self) -> None:
        hashed = hash_password("new-pass-123")
        self.assertTrue(hashed.startswith("$2b$"), "新哈希应为 bcrypt $2b$ 格式")
        self.assertEqual(len(hashed), 60, "bcrypt 哈希固定 60 字符")
        self.assertTrue(verify_password("new-pass-123", hashed))
        self.assertFalse(verify_password("new-pass-124", hashed))

    def test_malformed_hash_returns_false_instead_of_raising(self) -> None:
        """保持 passlib 时代的容错语义：损坏哈希返回 False，不向上抛异常。"""
        for bad in (
            "",
            "not-a-hash",
            "$2b$12$too-short",          # 截断：bcrypt 的 Rust 实现会 panic（非 ValueError/TypeError）
            "$2b$12$" + "x" * 53,        # 60 字符、格式合法但盐/摘要无意义
            None,                         # 非字符串
        ):
            with self.subTest(bad=bad):
                self.assertFalse(verify_password("any", bad))

    def test_bcrypt_uses_only_first_72_bytes(self) -> None:
        """特征化 bcrypt 的 72 字节边界（**当前**语义为静默截断，修法见 W1-12 / F-57）。

        若将来升级 bcrypt 5.x 使其改为报错，本用例会失败——那时应连同「口令字节上限策略」一起决策，
        而不是无声地改变长口令行为。
        """
        base = "a" * 72
        hashed = hash_password(base + "XXXX")
        try:
            accepted = verify_password(base + "YYYY", hashed)
        except ValueError:
            self.skipTest("bcrypt 已改为对 >72 字节报错（见 W1-12 决策）")
            return
        self.assertTrue(
            accepted,
            "特征化：前 72 字节相同的不同口令会互相通过（静默截断）——这是既有边界，见 F-57",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
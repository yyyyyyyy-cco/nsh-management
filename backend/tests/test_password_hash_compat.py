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

    def test_new_hash_uses_sha256_prefix_and_verifies(self) -> None:
        """新方案（W1-12）：`sha256$<bcrypt>`；前缀之后仍是标准 bcrypt `$2b$` 哈希。"""
        hashed = hash_password("new-pass-123")
        self.assertTrue(hashed.startswith("sha256$"), "新哈希应带 sha256$ 方案前缀")
        payload = hashed[len("sha256$") :]
        self.assertTrue(payload.startswith("$2b$"), "前缀之后应为 bcrypt $2b$")
        self.assertEqual(len(payload), 60, "bcrypt 部分固定 60 字符")
        self.assertEqual(len(hashed), 67, "总长度 = 7 字符前缀 + 60")
        self.assertTrue(verify_password("new-pass-123", hashed))
        self.assertFalse(verify_password("new-pass-124", hashed))

    def test_malformed_hash_returns_false_instead_of_raising(self) -> None:
        """保持 passlib 时代的容错语义：损坏哈希返回 False，不向上抛异常。"""
        for bad in (
            "",
            "not-a-hash",
            "$2b$12$too-short",  # 截断：bcrypt 的 Rust 实现会 panic（非 ValueError/TypeError）
            "$2b$12$" + "x" * 53,  # 60 字符、格式合法但盐/摘要无意义
            None,  # 非字符串
        ):
            with self.subTest(bad=bad):
                self.assertFalse(verify_password("any", bad))

    def test_new_scheme_uses_full_password_beyond_72_bytes(self) -> None:
        """**F-57 回归看护**：新方案下，前 72 字节相同、后缀不同的口令**不得**互相通过。"""
        base = "a" * 72
        hashed = hash_password(base + "XXXX")
        self.assertFalse(
            verify_password(base + "YYYY", hashed),
            "新方案必须先预哈希：超过 72 字节的后缀也参与校验（否则 F-57 未修复）",
        )
        self.assertTrue(verify_password(base + "XXXX", hashed))

    def test_new_scheme_handles_multibyte_long_password(self) -> None:
        """中文长口令（300 字节）能被完整使用；且与同前缀的其它口令互不通过。"""
        pw = "测" * 100  # 300 字节，远超 bcrypt 的 72 字节
        hashed = hash_password(pw)
        self.assertTrue(verify_password(pw, hashed))
        self.assertFalse(verify_password("测" * 99 + "试", hashed))

    def test_legacy_direct_bcrypt_hash_still_truncates_at_72_bytes(self) -> None:
        """**特征化旧行为**（仅适用于迁移前的历史哈希）：直连 bcrypt 只取前 72 字节。

        该行为**不是新期望**，而是记录：①历史哈希必须继续可用（不锁用户）；
        ②登录时的惰性升级（W1-12）会把它们逐个迁移到新方案，迁移完成后此特征自然消失。
        若将来升级 bcrypt 5.0.0（对 >72 字节**报错**），必须确认库内已无此类历史哈希，否则用户会被锁在门外。
        """
        import bcrypt

        base = "b" * 72
        legacy = bcrypt.hashpw((base + "XXXX").encode("utf-8"), bcrypt.gensalt()).decode("ascii")
        self.assertFalse(legacy.startswith("sha256$"), "构造的应是旧方案哈希（无前缀）")
        self.assertTrue(verify_password(base + "XXXX", legacy))
        self.assertTrue(
            verify_password(base + "YYYY", legacy),
            "特征化：旧方案哈希会静默截断，故后缀不同的口令也能通过——这正是 F-57，新方案已不再如此",
        )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()

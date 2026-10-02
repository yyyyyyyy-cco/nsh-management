"""安全工具单测（W2-2）：bcrypt 哈希/校验 + JWT 签发/解码。

权威源：`backend/app/core/security.py`；权限链路见 `backend/app/api/deps.py`。
说明：bcrypt 较慢（约 0.2-0.4s/次），故用例刻意只做必要次数的哈希。
"""
import unittest
from datetime import UTC, datetime, timedelta

try:
    from jose import jwt

    from app.core.config import settings
    from app.core.security import create_access_token, decode_access_token, hash_password, verify_password
except ImportError as exc:  # pragma: no cover — 本地无依赖环境（如 Python 3.14 装不上 pydantic-core）
    # 模块级跳过：避免无依赖环境在收集阶段 ImportError 报错（pytest 退出码 2）而非干净跳过
    import unittest

    raise unittest.SkipTest(f"缺少运行依赖（python-jose/bcrypt），跳过本模块：{exc}") from exc


class PasswordHashTests(unittest.TestCase):
    def test_hash_differs_from_plaintext_and_verifies(self):
        hashed = hash_password("s3cret-pw")
        self.assertNotEqual(hashed, "s3cret-pw")
        self.assertTrue(hashed.startswith("sha256$"), "新哈希应带 sha256$ 方案前缀（W1-12）")
        self.assertTrue(hashed[len("sha256$"):].startswith("$2b$"), "前缀之后应为 bcrypt $2b$ 哈希")
        self.assertTrue(verify_password("s3cret-pw", hashed))

    def test_wrong_password_is_rejected(self):
        hashed = hash_password("s3cret-pw")
        self.assertFalse(verify_password("s3cret-pW", hashed))
        self.assertFalse(verify_password("", hashed))

    def test_salt_makes_hashes_differ_per_call(self):
        first, second = hash_password("same-pw"), hash_password("same-pw")
        self.assertNotEqual(first, second, "bcrypt 每次加盐，哈希不应相同")
        self.assertTrue(verify_password("same-pw", first) and verify_password("same-pw", second))


class AccessTokenTests(unittest.TestCase):
    def test_roundtrip_carries_subject_role_and_version(self):
        payload = decode_access_token(create_access_token(42, "admin", token_version=3))
        self.assertIsNotNone(payload)
        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["role"], "admin")
        self.assertEqual(payload["ver"], 3)

    def test_tampered_signature_returns_none(self):
        token = create_access_token(1, "admin")
        tampered = token[:-4] + ("aaaa" if not token.endswith("aaaa") else "bbbb")
        self.assertIsNone(decode_access_token(tampered))

    def test_token_signed_with_other_secret_returns_none(self):
        forged = jwt.encode(
            {"sub": "1", "role": "developer", "ver": 0,
             "exp": datetime.now(UTC) + timedelta(minutes=5)},
            "attacker-secret",
            algorithm=settings.ALGORITHM,
        )
        self.assertIsNone(decode_access_token(forged))

    def test_expired_token_returns_none(self):
        expired = jwt.encode(
            {"sub": "1", "role": "admin", "ver": 0,
             "exp": datetime.now(UTC) - timedelta(minutes=1)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        self.assertIsNone(decode_access_token(expired))

    def test_garbage_returns_none(self):
        for bad in ("", "not-a-token", "a.b.c"):
            with self.subTest(token=bad):
                self.assertIsNone(decode_access_token(bad))
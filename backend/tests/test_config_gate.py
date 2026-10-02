"""生产弱密钥启动门禁回归（W2-2）。

权威源：`backend/app/core/config.py`（判定函数）+ `DEPLOY.md` §六（门禁说明）。
"""
import os
import unittest
from unittest import mock

from app.core.config import _is_production, _secret_key_is_weak

# 构造一个「32 字符、不含可猜片段、不含 20xx 年份」的强密钥用例
STRONG_MIXED_KEY = "Kj7#mQ2!vX9@bN4$wZ8%tR6^yU1&pL5*"


class SecretKeyStrengthTests(unittest.TestCase):
    """弱密钥判定：明显弱值一律拦截，强值不误杀。"""

    def test_dev_default_and_placeholders_are_weak(self):
        for key in (
            "dev-secret-key-change-in-production",
            "your-secret-key-change-this",
            "please-change-me-with-openssl-rand-hex-32",
        ):
            with self.subTest(key=key):
                self.assertTrue(_secret_key_is_weak(key))

    def test_empty_and_short_keys_are_weak(self):
        for key in ("", "a", "a" * 31):
            with self.subTest(length=len(key)):
                self.assertTrue(_secret_key_is_weak(key))

    def test_guessable_fragment_is_weak_even_if_long(self):
        # 长而可猜：长度足够但含 fragment（password）→ 仍判弱
        self.assertTrue(_secret_key_is_weak("Zq7!" + "x" * 24 + "password" + "y" * 8))

    def test_year_like_substring_is_weak(self):
        self.assertTrue(_secret_key_is_weak("Ab3!Cd5&" + "y" * 24 + "2019"))

    def test_strong_mixed_key_is_accepted(self):
        self.assertEqual(len(STRONG_MIXED_KEY), 32)
        self.assertFalse(_secret_key_is_weak(STRONG_MIXED_KEY))

    def test_64_hex_is_exempt_from_year_and_fragment_scan(self):
        # 豁免通道：≥64 位纯十六进制恒判强（避免随机 hex 偶含 20xx 被误杀）
        hex64 = "2012" + "abcdef" * 10          # 64 位十六进制，且含「2012」年份样式
        self.assertEqual(len(hex64), 64)
        self.assertFalse(_secret_key_is_weak(hex64))


class ProductionDetectionTests(unittest.TestCase):
    """生产环境判定：只断言显式 APP_ENV 的确定行为。"""

    def test_explicit_production_env(self):
        for value in ("production", "prod", " PRODUCTION "):
            with self.subTest(app_env=value), mock.patch.dict(os.environ, {"APP_ENV": value}):
                self.assertTrue(_is_production())

    def test_explicit_development_env(self):
        for value in ("development", "dev", "test"):
            with self.subTest(app_env=value), mock.patch.dict(os.environ, {"APP_ENV": value}):
                self.assertFalse(_is_production())

    def test_unset_env_result_is_environment_dependent(self):
        # 未声明 APP_ENV 时按容器特征兜底（/.dockerenv、/proc/1/cgroup），
        # 本地 Windows 与 CI 容器结果不同 —— 故只断言「返回布尔值、不抛异常」，不锁定具体值。
        environ = {k: v for k, v in os.environ.items() if k != "APP_ENV"}
        with mock.patch.dict(os.environ, environ, clear=True):
            self.assertIsInstance(_is_production(), bool)
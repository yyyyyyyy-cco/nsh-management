# -*- coding: utf-8 -*-
"""口令策略回归（合规化计划 W4-10 / ASVS 5.0.0 V6）。

**本模块只依赖标准库**（策略实现 `app/core/password_policy.py` 是纯逻辑），
因此无第三方依赖的环境也能真跑——不是「跳过」。

覆盖要点：
- 长度边界 8 / 128（6.2.1、6.2.9）与 **64+ 必须被接受**；
- **6.2.5：不得限制字符组成**——纯字母、纯数字、纯符号都必须通过（这正是本轮删掉旧规则的依据）；
- 上下文词表与常见弱口令拦截（6.1.2 / 6.2.11）；
- 不得含登录名、不得为单一重复字符。
"""
import unittest

from app.core.password_policy import MAX_LENGTH, MIN_LENGTH, PasswordPolicyError, validate_password


class PasswordLengthTests(unittest.TestCase):
    def test_below_minimum_is_rejected(self):
        with self.assertRaises(PasswordPolicyError) as ctx:
            validate_password("abcd123")  # 7 位
        self.assertIn(str(MIN_LENGTH), str(ctx.exception))

    def test_minimum_is_accepted(self):
        validate_password("abcd1234")  # 8 位

    def test_at_least_64_is_allowed(self):
        """6.2.9：至少允许 64 位（不能因为上限把长口令挡住）。"""
        validate_password("Ab3!" * 16)  # 64 位且非单一重复

    def test_maximum_is_accepted_and_beyond_rejected(self):
        long_ok = "A3" + "x" * (MAX_LENGTH - 2)
        validate_password(long_ok)
        with self.assertRaises(PasswordPolicyError):
            validate_password("A3" + "y" * MAX_LENGTH)


class CompositionIsNotRestrictedTests(unittest.TestCase):
    """ASVS 6.2.5：口令可使用任意组成——这三条是本轮**行为变更**的关键证据。"""

    def test_letters_only_is_accepted(self):
        validate_password("abcdefgh")

    def test_digits_only_is_accepted_when_not_common(self):
        validate_password("92713465")  # 不在词表里的纯数字

    def test_symbols_only_is_accepted(self):
        validate_password("!@#$%^&*")


class WeakPasswordTests(unittest.TestCase):
    def test_common_password_is_rejected(self):
        for weak in ("password", "Password", "12345678", "qwerty123", "admin123"):
            with self.subTest(weak=weak):
                with self.assertRaises(PasswordPolicyError):
                    validate_password(weak)

    def test_context_words_are_rejected(self):
        for weak in ("nishuihan", "qingshan", "developer"):
            with self.subTest(weak=weak):
                with self.assertRaises(PasswordPolicyError):
                    validate_password(weak)

    def test_single_repeated_character_is_rejected(self):
        with self.assertRaises(PasswordPolicyError):
            validate_password("aaaaaaaa")

    def test_password_containing_username_is_rejected(self):
        with self.assertRaises(PasswordPolicyError):
            validate_password("zhangsan-2026", username="zhangsan")
        with self.assertRaises(PasswordPolicyError):
            validate_password("zhangsan", username="zhangsan-2026")

    def test_username_check_is_case_insensitive(self):
        with self.assertRaises(PasswordPolicyError):
            validate_password("ZhangSan2026x", username="zhangsan")

    def test_unrelated_username_does_not_block(self):
        validate_password("abcdefgh", username="zzz")


if __name__ == "__main__":
    unittest.main(verbosity=2)
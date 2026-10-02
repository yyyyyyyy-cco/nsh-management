"""姓名规范化规则回归（W2-2）。

权威源：`backend/app/utils/member_names.py`（出勤与排表共用）；
历史背景：出勤库姓名与排表槽位姓名精确匹配失败曾导致槽位职业为空（见 progress.md 2026-09-15）。
"""
import unittest

from app.utils.member_names import normalize_member_name


class NormalizeMemberNameTests(unittest.TestCase):
    def test_none_and_empty_become_empty_string(self):
        for value in (None, "", "   ", "\u3000"):
            with self.subTest(value=repr(value)):
                self.assertEqual(normalize_member_name(value), "")

    def test_trims_leading_and_trailing_whitespace(self):
        self.assertEqual(normalize_member_name("  张三  "), "张三")
        self.assertEqual(normalize_member_name("\t王五\n"), "王五")

    def test_trims_full_width_space(self):
        # 中文输入法常见的全角空格（U+3000）也必须去掉
        self.assertEqual(normalize_member_name("\u3000李四\u3000"), "李四")

    def test_internal_space_and_case_are_preserved(self):
        # 规则只是「去首尾空白」：内部空格与大小写必须原样保留（游戏 ID 大小写敏感）
        self.assertEqual(normalize_member_name(" 张 三 "), "张 三")
        self.assertEqual(normalize_member_name("AbC_Dd"), "AbC_Dd")

    def test_idempotent(self):
        once = normalize_member_name("  赵六 ")
        self.assertEqual(normalize_member_name(once), once)
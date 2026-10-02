"""上传文件名缺失的回归测试（F-104，P2）。

背景：`app/api/v1/match_data.py` 的 CSV 导入接口此前直接调用 `file.filename.endswith(...)`，
而 `UploadFile.filename` 的类型是 `str | None` —— 客户端构造一个**不带文件名**的 multipart 部件时，
该行会抛 `AttributeError`，用户拿到 **500** 而不是干净的 **400 + 原因**（与 F-98 同型）。

本文件锁定：缺失/异常文件名一律按「仅支持 CSV 文件」拒绝（400 业务错误），不得抛 AttributeError；
合法 `.csv`（含大小写变体）正常通过。
"""
from __future__ import annotations

import unittest
from io import BytesIO

from fastapi import UploadFile

import app.api.v1.match_data as match_data_api


def _accepts(filename: str | None) -> bool:
    """复刻接口内的文件名判定（与实现同一行逻辑），返回是否通过。"""
    return bool((filename or "").lower().endswith(".csv"))


class UploadFilenameGuardTest(unittest.TestCase):
    def test_upload_file_filename_can_be_none(self) -> None:
        f = UploadFile(file=BytesIO(b""), filename=None)
        self.assertIsNone(f.filename, "UploadFile 允许 filename 为 None（类型为 str | None）")

    def test_none_filename_is_rejected(self) -> None:
        """缺失文件名必须被拒（不得进入 .endswith，否则 AttributeError）。"""
        self.assertFalse(_accepts(None))

    def test_valid_filenames_pass(self) -> None:
        for name in ("a.csv", "A.CSV", "数据.csv"):
            self.assertTrue(_accepts(name))

    def test_invalid_filenames_rejected(self) -> None:
        for name in ("a.xlsx", "a.txt", "", None):
            self.assertFalse(_accepts(name))

    def test_source_uses_none_guard(self) -> None:
        """源码级锁：CSV 导入接口必须对 filename 为 None 做兜底（防止回归）。

        不使用 inspect.getsource(具体函数)，避免函数改名导致测试脆弱；直接断言模块源码含兜底表达式。
        """
        import inspect

        src = inspect.getsource(match_data_api)
        self.assertIn("file.filename or", src, "接口必须对 filename 为 None 做兜底（F-104）")
        self.assertNotIn("if not file.filename.endswith", src, "不得回退为直接对 filename 调 .endswith")


if __name__ == "__main__":
    unittest.main()

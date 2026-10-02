"""ExcelImportError 携带 message 的回归测试（F-98）。

背景（F-98，P2）：`ExcelImportError` 是**唯一**没有定义 `self.message` 的服务层错误类
（其余 11 个错误类都有），而 `app/main.py` 的专用错误处理器会取 `exc.message` →
Excel 导入失败时抛出的异常在处理器里会再触发 `AttributeError`，用户看到的将是 **500** 而非 **400**。

本文件锁定：
- `ExcelImportError(msg).message` 与 `str(exc)`；
- `main.excel_import_error_handler` 返回 **400** 且响应体带上原始消息（不再 AttributeError）。
"""
from __future__ import annotations

import json
import unittest

from app.main import excel_import_error_handler
from app.utils.excel_import import ExcelImportError


class ExcelImportErrorMessageTest(unittest.TestCase):
    def test_message_attribute_matches_argument(self) -> None:
        exc = ExcelImportError("仅支持 .xlsx 格式的 Excel 文件")
        self.assertEqual(exc.message, "仅支持 .xlsx 格式的 Excel 文件")
        self.assertEqual(str(exc), "仅支持 .xlsx 格式的 Excel 文件")

    def test_default_message_is_empty_string(self) -> None:
        exc = ExcelImportError()
        self.assertEqual(exc.message, "")
        self.assertEqual(str(exc), "")

    def test_handler_returns_400_with_message(self) -> None:
        """处理器不再 AttributeError；响应体 message 即异常消息（request 未被使用，可传 None）。"""
        import asyncio

        resp = asyncio.run(excel_import_error_handler(None, ExcelImportError("Excel 文件解析失败，请检查格式")))
        self.assertEqual(resp.status_code, 400)
        body = json.loads(bytes(resp.body).decode("utf-8"))
        self.assertEqual(body.get("message"), "Excel 文件解析失败，请检查格式")
        self.assertEqual(body.get("code"), 400)


if __name__ == "__main__":
    unittest.main()
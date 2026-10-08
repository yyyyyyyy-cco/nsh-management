"""职业配置批量更新的契约回归测试（F-105，P2）。

背景：`PUT /config/professions` 曾**实际不可用** —— 服务 `batch_update_profession_configs` 的签名与
服务体是 dict 式（`item.get("profession")` / `item.get("target_count", 0)`），而路由把
`list[ProfessionConfigItem]`（pydantic 模型）直接传进去；pydantic BaseModel **没有 `.get`**，
运行时抛 `AttributeError` -> 500（本应由 mypy 的 arg-type 拦下，属"类型谎言暴露运行时故障"）。

本文件锁定：路由侧必须做 `model_dump()` 转换，与服务契约一致；并显式记录"模型没有 .get"这一成因。
"""

from __future__ import annotations

import inspect
import unittest

from app.api.v1 import config as config_api
from app.schemas.config import ProfessionConfigItem


class ProfessionConfigContractTest(unittest.TestCase):
    def test_pydantic_item_has_no_get(self) -> None:
        """成因锁定：pydantic 模型没有 dict 式 .get，直接传模型必然 AttributeError。"""
        item = ProfessionConfigItem(profession="铁衣", target_count=6, remark=None)
        self.assertFalse(hasattr(item, "get"), "ProfessionConfigItem 不应有 .get；服务端按 dict 契约实现")
        self.assertEqual(item.profession, "铁衣")

    def test_service_is_dict_based(self) -> None:
        """服务契约锁定：服务体按 dict 访问（.get），因此调用方必须传 dict。"""
        from app.services import config_service

        src = inspect.getsource(config_service.batch_update_profession_configs)
        self.assertIn('.get("profession")', src)
        self.assertIn('.get("target_count"', src)

    def test_route_converts_models_to_dicts(self) -> None:
        """路由必须转换：源码含 model_dump()（防止回退为直接传模型）。"""
        src = inspect.getsource(config_api)
        self.assertIn("model_dump()", src, "路由必须把 ProfessionConfigItem 转为 dict 再调用服务（F-105）")


if __name__ == "__main__":
    unittest.main()

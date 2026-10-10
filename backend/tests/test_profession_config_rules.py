"""职业配置目标人数值域的回归测试（F-84）。

背景：2026-10-03 前，单职业端点只有 `ge=0` 无上限、**批量端点用 `list[dict]` 等于零校验**，
而每赛程覆盖在另一条路径上校验 0–60——同一语义三层不一致。
修复后统一为 **0～999**（与前端输入 `:min=0 :max=999` 一致）：schema 层 + service 层兜底均校验。
"""

from __future__ import annotations

import unittest

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from support import PROFESSION_SEED, profession_seed_rows

from app.core.database import Base
from app.models.guild import Guild
from app.models.profession import ProfessionConfig
from app.schemas.config import (
    ProfessionConfigBatchUpdate,
    ProfessionConfigItem,
    ProfessionConfigUpdate,
)
from app.services import config_service
from app.services.config_service import ConfigServiceError
from app.utils.constants import MAX_PROFESSION_TARGET

# 职业名从种子推导，避免硬编码（与迁移种子一致）
PROF = sorted(name for name, _, _ in PROFESSION_SEED)[0]


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        self.session.add(Guild(id=1, name="职业配置测试"))
        self.session.add_all(profession_seed_rows())
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()


class ProfessionConfigSchemaTest(unittest.TestCase):
    def test_single_endpoint_bounds(self) -> None:
        self.assertEqual(ProfessionConfigUpdate(target_count=0).target_count, 0)
        self.assertEqual(ProfessionConfigUpdate(target_count=MAX_PROFESSION_TARGET).target_count, MAX_PROFESSION_TARGET)
        with self.assertRaises(ValidationError):
            ProfessionConfigUpdate(target_count=-1)
        with self.assertRaises(ValidationError):
            ProfessionConfigUpdate(target_count=MAX_PROFESSION_TARGET + 1)

    def test_batch_items_are_typed(self) -> None:
        """批量入口不再是 list[dict]：逐项类型化校验。"""
        ok = ProfessionConfigBatchUpdate(configs=[{"profession": PROF, "target_count": 12}])
        self.assertEqual(ok.configs[0].target_count, 12)
        for bad in (
            {"profession": PROF, "target_count": -1},
            {"profession": PROF, "target_count": MAX_PROFESSION_TARGET + 1},
            {"profession": PROF, "target_count": "abc"},
        ):
            with self.assertRaises(ValidationError):
                ProfessionConfigBatchUpdate(configs=[bad])
        with self.assertRaises(ValidationError):
            ProfessionConfigItem(profession=PROF, target_count=MAX_PROFESSION_TARGET + 1)


class ProfessionConfigServiceTest(_Base):
    async def test_single_path_validates_bounds(self) -> None:
        """service 层兜底：越界值不写库。"""
        with self.assertRaises(ConfigServiceError):
            await config_service.update_profession_config(self.session, 1, PROF, MAX_PROFESSION_TARGET + 1)
        await self.session.rollback()
        saved = await config_service.update_profession_config(self.session, 1, PROF, 42)
        self.assertEqual(saved.target_count, 42)

    async def test_batch_path_validates_bounds(self) -> None:
        with self.assertRaises(ConfigServiceError):
            await config_service.batch_update_profession_configs(
                self.session, 1, [{"profession": PROF, "target_count": MAX_PROFESSION_TARGET + 1}]
            )
        await self.session.rollback()
        count = await config_service.batch_update_profession_configs(
            self.session, 1, [{"profession": PROF, "target_count": 7, "remark": "测试"}]
        )
        self.assertEqual(count, 1)
        row = (
            (await self.session.execute(select(ProfessionConfig).where(ProfessionConfig.guild_id == 1)))
            .scalars()
            .first()
        )
        self.assertEqual(row.target_count, 7)

    async def test_unbound_guild_rejected(self) -> None:
        """未绑定帮会的开发者账号不能改职业配置（两条路径都拒绝）。"""
        with self.assertRaises(ConfigServiceError):
            await config_service.update_profession_config(self.session, None, PROF, 1)
        with self.assertRaises(ConfigServiceError):
            await config_service.batch_update_profession_configs(
                self.session, None, [{"profession": PROF, "target_count": 1}]
            )


if __name__ == "__main__":
    unittest.main()

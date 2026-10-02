"""系统配置接口：职业配置（账号管理见 accounts.py，帮会管理见 guilds.py）。"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.config import (
    ProfessionConfigBatchUpdate,
    ProfessionConfigOut,
    ProfessionConfigUpdate,
)
from app.services import config_service

router = APIRouter(prefix="/config", tags=["系统配置"])


# ========== 职业配置 ==========

@router.get("/professions", response_model=list[ProfessionConfigOut])
async def get_profession_configs(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[ProfessionConfigOut]:
    """获取职业配置列表。"""
    configs = await config_service.get_profession_configs(session, current_user.guild_id)
    # 缺失职业为未落库的默认配置（GET 不写库）：补 id 展示占位，首次批量保存时才会真正插入
    for c in configs:
        if c.id is None:
            c.id = 0
    return [ProfessionConfigOut.model_validate(c) for c in configs]


@router.put("/professions/{profession}", response_model=ProfessionConfigOut)
async def update_profession_config(
    profession: str,
    body: ProfessionConfigUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ProfessionConfigOut:
    """更新单个职业的目标人数（管理员）。"""
    config = await config_service.update_profession_config(
        session, current_user.guild_id, profession, body.target_count
    )
    return ProfessionConfigOut.model_validate(config)


@router.put("/professions", response_model=dict)
async def batch_update_profession_configs(
    body: ProfessionConfigBatchUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    """批量更新职业配置（管理员）。"""
    count = await config_service.batch_update_profession_configs(
        session, current_user.guild_id, [c.model_dump() for c in body.configs]
    )
    return {"message": f"已更新 {count} 个职业配置"}

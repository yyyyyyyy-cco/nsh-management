"""分析调整副本业务：仅存储「未排表成员 → 目标队伍」映射，不改动正式排表。"""
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.squad_adjustment import SquadAdjustment
from app.services.schedule_service import get_schedule

# 目标队伍 key 形如 "进攻1:0"（category:team_index）
TEAM_KEY_PATTERN = re.compile(r"^[^:]+:\d+$")


class SquadAdjustmentError(Exception):
    """分析调整业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_squad_adjustment(
    session: AsyncSession, guild_id: int, schedule_id: int,
) -> SquadAdjustment:
    """获取调整副本；无记录时落库空副本，保证结构稳定。"""
    await get_schedule(session, guild_id, schedule_id)
    adj = (
        await session.execute(
            select(SquadAdjustment).where(SquadAdjustment.schedule_id == schedule_id)
        )
    ).scalar_one_or_none()
    if adj is None:
        adj = SquadAdjustment(schedule_id=schedule_id, data={})
        session.add(adj)
        await session.commit()
        await session.refresh(adj)
    return adj


async def save_squad_adjustment(
    session: AsyncSession, guild_id: int, schedule_id: int, data: dict[str, str],
) -> SquadAdjustment:
    """保存调整副本：校验目标队伍 key 格式与成员名非空。"""
    adj = await get_squad_adjustment(session, guild_id, schedule_id)
    cleaned: dict[str, str] = {}
    for name, key in data.items():
        name = (name or "").strip()
        key = (key or "").strip()
        if not name:
            continue
        if not TEAM_KEY_PATTERN.match(key):
            raise SquadAdjustmentError(f"目标队伍格式不合法: {key}")
        cleaned[name] = key
    adj.data = cleaned
    await session.commit()
    await session.refresh(adj)
    return adj

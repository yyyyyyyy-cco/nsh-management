"""个人战绩查询接口：按游戏 ID 聚合历史比赛数据，支持已确认的新旧 ID 合并查询。

名称归属解析（merged/exact 与冲突 409）见 design-game-id-change.md §4.3/§5。
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_member_or_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.my_stats import (
    MyStatsResponse,
    PlayerNameList,
    PlayerRecordOut,
    PlayerSummary,
)
from app.services import my_stats_service

router = APIRouter(prefix="/my-stats", tags=["个人战绩"])


@router.get("/player-names", response_model=PlayerNameList)
async def get_player_names(
    q: str = Query(..., min_length=1, max_length=32, description="搜索关键词"),
    current_user: User = Depends(require_member_or_admin),
    session: AsyncSession = Depends(get_db),
) -> PlayerNameList:
    """模糊搜索本帮会候选名称（比赛数据名称 + 已确认改名关系的新旧名称与当前名）。"""
    names = await my_stats_service.search_player_names(session, current_user.guild_id, q)
    return PlayerNameList(names=names)


@router.get("", response_model=MyStatsResponse)
async def get_my_stats(
    player_name: str = Query(..., min_length=1, max_length=32, description="游戏 ID"),
    merge_aliases: bool = Query(True, description="是否合并该成员已确认的历史 ID；false 为仅查此 ID"),
    current_user: User = Depends(require_member_or_admin),
    session: AsyncSession = Depends(get_db),
) -> MyStatsResponse:
    """按游戏 ID 查询历史战绩（帮众/管理员）；合并冲突返回 409，可改用 merge_aliases=false。"""
    data = await my_stats_service.query_player_stats(session, current_user.guild_id, player_name, merge_aliases)
    identity = data["identity"]
    return MyStatsResponse(
        records=[PlayerRecordOut(**r) for r in data["records"]],
        summary=PlayerSummary(**data["summary"]),
        identity={
            "mode": identity.mode,
            "query_player_name": identity.query_player_name,
            "member_id": identity.member_id,
            "current_game_id": identity.current_game_id,
            "aliases": identity.aliases,
        },
    )

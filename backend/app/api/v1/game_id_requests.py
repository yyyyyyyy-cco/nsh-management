"""游戏 ID 改名申请接口（薄路由）：候选、提交、历史、审核列表与审核。

路径统一挂在 /members 前缀下；注册时须先于 members.router，避免被 /{member_id} 捕获。
设计依据：memory-bank/design-game-id-change.md §4。
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin_strict, require_member, require_member_or_admin
from app.core.database import get_db
from app.models.member import Member
from app.models.user import User
from app.schemas.game_id_request import (
    GameIdOptionPage,
    GameIdRequestAdminHistoryPage,
    GameIdRequestAdminOut,
    GameIdRequestAdminPage,
    GameIdRequestAudit,
    GameIdRequestCreate,
    GameIdRequestMemberOut,
    GameIdRequestMemberPage,
    MemberMinimal,
)
from app.services import game_id_request_service

router = APIRouter(prefix="/members", tags=["游戏 ID 改名"])


@router.get("/game-id-options", response_model=GameIdOptionPage)
async def list_game_id_options(
    q: str | None = Query(None, max_length=32, description="按 ID 关键词筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    current_user: User = Depends(require_member),
    session: AsyncSession = Depends(get_db),
) -> GameIdOptionPage:
    """本帮会常驻成员最小候选（帮众选择要改名的成员）。"""
    items, total = await game_id_request_service.list_options(
        session, current_user.guild_id, q, page, page_size
    )
    return GameIdOptionPage(
        items=[MemberMinimal.model_validate(m) for m in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/{member_id}/game-id-requests", response_model=GameIdRequestMemberOut, status_code=status.HTTP_201_CREATED)
async def create_game_id_request(
    member_id: int,
    body: GameIdRequestCreate,
    current_user: User = Depends(require_member),
    session: AsyncSession = Depends(get_db),
) -> GameIdRequestMemberOut:
    """提交改名申请（帮众）；成功不改变常驻库。"""
    record = await game_id_request_service.create_request(
        session, current_user.guild_id, member_id, current_user, body
    )
    return GameIdRequestMemberOut.model_validate(record)


@router.get("/{member_id}/game-id-requests")
async def list_member_game_id_requests(
    member_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_member_or_admin),
    session: AsyncSession = Depends(get_db),
):
    """某成员的改名申请历史；帮众返回脱敏模型，管理员额外含账号快照与当前成员名。"""
    member, items, total = await game_id_request_service.get_member_history(
        session, current_user.guild_id, member_id, page, page_size
    )
    minimal = MemberMinimal.model_validate(member)
    if current_user.role == "admin":
        return GameIdRequestAdminHistoryPage(
            member=minimal,
            items=[_admin_out(r, member.name) for r in items],
            total=total,
            page=page,
            page_size=page_size,
        )
    return GameIdRequestMemberPage(
        member=minimal,
        items=[GameIdRequestMemberOut.model_validate(r) for r in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/game-id-requests", response_model=GameIdRequestAdminPage)
async def list_game_id_requests(
    request_status: str = Query("pending", alias="status", description="pending/approved/rejected/invalidated/all"),
    keyword: str | None = Query(None, max_length=32, description="按原/新 ID 关键词筛选"),
    member_id: int | None = Query(None, ge=1, description="按目标成员筛选"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_admin_strict),
    session: AsyncSession = Depends(get_db),
) -> GameIdRequestAdminPage:
    """帮会改名审核列表（仅管理员），默认待审核。"""
    records, total, name_map = await game_id_request_service.list_requests(
        session, current_user.guild_id, request_status, keyword, member_id, page, page_size
    )
    items = [
        _admin_out(r, name_map.get(r.member_id) if r.member_id is not None else None)
        for r in records
    ]
    return GameIdRequestAdminPage(items=items, total=total, page=page, page_size=page_size)


@router.put("/game-id-requests/{request_id}/audit", response_model=GameIdRequestAdminOut)
async def audit_game_id_request(
    request_id: int,
    body: GameIdRequestAudit,
    current_user: User = Depends(require_admin_strict),
    session: AsyncSession = Depends(get_db),
) -> GameIdRequestAdminOut:
    """审核改名申请（仅管理员）：通过与成员改名同一事务提交。"""
    record = await game_id_request_service.audit_request(
        session, current_user.guild_id, request_id, current_user, body
    )
    return _admin_out(
        record, await _current_member_name(session, current_user.guild_id, record.member_id)
    )


async def _current_member_name(session: AsyncSession, guild_id: int, member_id: int | None) -> str | None:
    """审核后回显目标成员当前名称（成员已删除时为空）。"""
    if member_id is None:
        return None
    member = await session.get(Member, member_id)
    if member is None or member.guild_id != guild_id:
        return None
    return member.name


def _admin_out(record, current_game_id: str | None) -> GameIdRequestAdminOut:
    data = GameIdRequestMemberOut.model_validate(record).model_dump()
    return GameIdRequestAdminOut(
        **data,
        requester_username=record.requester_username,
        reviewer_username=record.reviewer_username,
        current_game_id=current_game_id,
    )

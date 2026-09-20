"""游戏 ID 修改申请的关联维护：成员直接改名（失效待审 + 记录已确认关联）/删除、账号删除、整帮会删除。

只依赖模型，不导入其他业务服务，避免循环依赖；辅助函数一律不自行 commit，
由调用方（member_service / account_service / guild_service）统一提交或回滚。
"""
from datetime import datetime, timezone

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_id_request import MemberGameIdRequest

# 管理员直接在常驻库改名的自动记录备注（用于与帮众申请审核记录区分）
ADMIN_DIRECT_RENAME_REMARK = "管理员直接在常驻库改名（自动记录，无提交申请）"


def _now() -> datetime:
    return datetime.now(timezone.utc)


async def invalidate_pending_by_member(session: AsyncSession, member_id: int) -> None:
    """成员被管理员直接改名：该成员待审申请置失效（member_renamed）。

    已审核终态不受影响；非待审状态不会被覆盖。
    """
    await session.execute(
        update(MemberGameIdRequest)
        .where(
            MemberGameIdRequest.member_id == member_id,
            MemberGameIdRequest.status == "pending",
        )
        .values(
            status="invalidated",
            invalidated_reason="member_renamed",
            updated_at=_now(),
        )
    )


async def record_admin_rename(
    session: AsyncSession,
    *,
    guild_id: int,
    member_id: int,
    old_game_id: str,
    new_game_id: str,
    operator_id: int,
    operator_username: str,
) -> None:
    """管理员直接在常驻库改名：写入一条 approved 关联记录（不自行 commit）。

    该记录与帮众申请审核通过同口径，作为个人战绩新旧 ID 合并的已确认关系来源；
    提交/审核人均为操作管理员，备注标注来源便于审核列表区分。
    调用方须同时失效该成员的 pending 申请，避免旧申请在改名后仍可被审核。
    """
    now = _now()
    session.add(
        MemberGameIdRequest(
            guild_id=guild_id,
            member_id=member_id,
            old_game_id=old_game_id,
            new_game_id=new_game_id,
            requester_id=operator_id,
            requester_username=operator_username,
            status="approved",
            reviewer_id=operator_id,
            reviewer_username=operator_username,
            review_remark=ADMIN_DIRECT_RENAME_REMARK,
            reviewed_at=now,
            updated_at=now,
        )
    )
    await session.flush()


async def detach_member(session: AsyncSession, member_ids: list[int]) -> None:
    """成员被删除（单个/批量）：待审申请先置失效，随后将该成员全部申请的 member_id 置空。

    保留原/新 ID 快照与审核记录作为历史证据，避免主键复用导致误关联。
    """
    if not member_ids:
        return
    await session.execute(
        update(MemberGameIdRequest)
        .where(
            MemberGameIdRequest.member_id.in_(member_ids),
            MemberGameIdRequest.status == "pending",
        )
        .values(
            status="invalidated",
            invalidated_reason="member_deleted",
            updated_at=_now(),
        )
    )
    await session.execute(
        update(MemberGameIdRequest)
        .where(MemberGameIdRequest.member_id.in_(member_ids))
        .values(member_id=None)
    )


async def detach_user(session: AsyncSession, user_id: int) -> None:
    """账号被删除：清空申请人/审核人引用，保留账号名快照（待审申请不丢失）。"""
    await session.execute(
        update(MemberGameIdRequest)
        .where(MemberGameIdRequest.requester_id == user_id)
        .values(requester_id=None)
    )
    await session.execute(
        update(MemberGameIdRequest)
        .where(MemberGameIdRequest.reviewer_id == user_id)
        .values(reviewer_id=None)
    )


async def purge_guild(session: AsyncSession, guild_id: int) -> None:
    """删除整个帮会：先删本帮会申请记录，再由调用方删除成员与账号。"""
    await session.execute(
        delete(MemberGameIdRequest).where(MemberGameIdRequest.guild_id == guild_id)
    )

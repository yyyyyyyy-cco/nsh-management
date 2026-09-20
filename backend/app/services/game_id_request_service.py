"""游戏 ID 修改申请业务：成员候选、提交、审核列表与原子审核。

设计依据：memory-bank/design-game-id-change.md（状态机 / 事务 / 冲突边界）。
"""
from datetime import datetime, timezone

from sqlalchemy import func, or_, select, update
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_id_request import REQUEST_STATUSES, MemberGameIdRequest
from app.models.member import Member
from app.models.user import User
from app.schemas.game_id_request import GameIdRequestAudit, GameIdRequestCreate, normalize_new_game_id


class GameIdRequestError(Exception):
    """改名申请业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _is_unique_violation(exc: IntegrityError) -> bool:
    return "unique" in str(exc.orig).lower()


def _is_busy_error(exc: OperationalError) -> bool:
    text = str(exc.orig).lower()
    return "locked" in text or "busy" in text


async def _commit_or_raise(
    session: AsyncSession,
    duplicate_message: str | None = None,
) -> None:
    """统一提交：唯一约束冲突按 409、SQLite 写锁繁忙按 503，其余异常原样抛出。"""
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if duplicate_message and _is_unique_violation(exc):
            raise GameIdRequestError(duplicate_message, 409) from exc
        raise
    except OperationalError as exc:
        await session.rollback()
        if _is_busy_error(exc):
            raise GameIdRequestError("系统繁忙，请稍后刷新重试", 503) from exc
        raise


async def list_options(
    session: AsyncSession,
    guild_id: int,
    keyword: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Member], int]:
    """本帮会常驻成员最小候选（按名称排序，稳定分页）。"""
    stmt = select(Member).where(Member.guild_id == guild_id)
    if keyword:
        stmt = stmt.where(Member.name.contains(keyword))
    total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (
        (await session.execute(stmt.order_by(Member.name.asc(), Member.id.asc()).offset((page - 1) * page_size).limit(page_size)))
        .scalars()
        .all()
    )
    return list(items), int(total)


async def create_request(
    session: AsyncSession,
    guild_id: int,
    member_id: int,
    requester: User,
    data: GameIdRequestCreate,
) -> MemberGameIdRequest:
    """提交改名申请：校验归属/旧值/重名/重复待审，提交成功不改变常驻库。"""
    member = await session.get(Member, member_id)
    if member is None or member.guild_id != guild_id:
        raise GameIdRequestError("成员不存在", 404)
    # 旧值以数据库为准：页面快照过期（已被直接改名）时拒绝
    if member.name != data.expected_old_game_id:
        raise GameIdRequestError("该成员 ID 已变更，请刷新后重新提交", 409)

    new_game_id = normalize_new_game_id(data.new_game_id)
    if new_game_id == member.name:
        raise GameIdRequestError("新 ID 与当前 ID 相同", 422)

    occupied = (
        await session.execute(
            select(func.count())
            .select_from(Member)
            .where(Member.guild_id == guild_id, Member.name == new_game_id, Member.id != member.id)
        )
    ).scalar_one()
    if occupied:
        raise GameIdRequestError(f"常驻库已存在 ID「{new_game_id}」，请勿重复", 409)

    pending = (
        await session.execute(
            select(func.count())
            .select_from(MemberGameIdRequest)
            .where(
                MemberGameIdRequest.guild_id == guild_id,
                MemberGameIdRequest.member_id == member.id,
                MemberGameIdRequest.status == "pending",
            )
        )
    ).scalar_one()
    duplicate_message = "该成员已有待审核申请，请等待审核结果"
    if pending:
        raise GameIdRequestError(duplicate_message, 409)

    record = MemberGameIdRequest(
        guild_id=guild_id,
        member_id=member.id,
        old_game_id=member.name,
        new_game_id=new_game_id,
        requester_id=requester.id,
        requester_username=requester.username,
        status="pending",
    )
    session.add(record)
    await _commit_or_raise(session, duplicate_message)
    await session.refresh(record)
    return record


async def get_member_history(
    session: AsyncSession,
    guild_id: int,
    member_id: int,
    page: int,
    page_size: int,
) -> tuple[Member, list[MemberGameIdRequest], int]:
    """某成员的申请历史（含成员最小信息，按时间倒序稳定分页）。"""
    member = await session.get(Member, member_id)
    if member is None or member.guild_id != guild_id:
        raise GameIdRequestError("成员不存在", 404)
    stmt = select(MemberGameIdRequest).where(
        MemberGameIdRequest.guild_id == guild_id,
        MemberGameIdRequest.member_id == member_id,
    )
    total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (
        (
            await session.execute(
                stmt.order_by(MemberGameIdRequest.created_at.desc(), MemberGameIdRequest.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    return member, list(items), int(total)


async def list_requests(
    session: AsyncSession,
    guild_id: int,
    status: str,
    keyword: str | None,
    member_id: int | None,
    page: int,
    page_size: int,
) -> tuple[list[MemberGameIdRequest], int, dict[int, str]]:
    """帮会审核列表：默认待审，可按状态/成员/关键词筛选；附带当前成员名称映射。"""
    if status != "all" and status not in REQUEST_STATUSES:
        raise GameIdRequestError("无效的状态筛选值", 422)
    stmt = select(MemberGameIdRequest).where(MemberGameIdRequest.guild_id == guild_id)
    if status != "all":
        stmt = stmt.where(MemberGameIdRequest.status == status)
    if member_id is not None:
        stmt = stmt.where(MemberGameIdRequest.member_id == member_id)
    if keyword:
        stmt = stmt.where(
            or_(
                MemberGameIdRequest.old_game_id.contains(keyword),
                MemberGameIdRequest.new_game_id.contains(keyword),
            )
        )
    total = (await session.execute(select(func.count()).select_from(stmt.subquery()))).scalar_one()
    items = (
        (
            await session.execute(
                stmt.order_by(MemberGameIdRequest.created_at.desc(), MemberGameIdRequest.id.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            )
        )
        .scalars()
        .all()
    )
    records = list(items)
    member_ids = {r.member_id for r in records if r.member_id is not None}
    name_map: dict[int, str] = {}
    if member_ids:
        rows = (
            await session.execute(
                select(Member.id, Member.name).where(Member.guild_id == guild_id, Member.id.in_(member_ids))
            )
        ).all()
        name_map = {mid: name for mid, name in rows}
    return records, int(total), name_map


async def audit_request(
    session: AsyncSession,
    guild_id: int,
    request_id: int,
    reviewer: User,
    data: GameIdRequestAudit,
) -> MemberGameIdRequest:
    """审核申请：条件更新申请状态 + 通过时同事务更新成员名称，任一步失败整体回滚。"""
    record = (
        await session.execute(
            select(MemberGameIdRequest).where(
                MemberGameIdRequest.id == request_id,
                MemberGameIdRequest.guild_id == guild_id,
            )
        )
    ).scalar_one_or_none()
    if record is None:
        raise GameIdRequestError("申请不存在", 404)
    if record.status != "pending":
        raise GameIdRequestError("该申请已处理，请刷新列表", 409)

    # 回滚会使 ORM 实例过期（异步下再读属性会触发 IO），所需字段先取快照
    target_member_id = record.member_id
    old_game_id = record.old_game_id
    new_game_id = record.new_game_id

    now = datetime.now(timezone.utc)
    values = {
        "status": "approved" if data.action == "approve" else "rejected",
        "reviewer_id": reviewer.id,
        "reviewer_username": reviewer.username,
        "review_remark": data.review_remark,
        "reviewed_at": now,
        "updated_at": now,
    }
    if data.action == "approve" and target_member_id is None:
        raise GameIdRequestError("目标成员已被删除，该申请无法通过", 409)

    # 1) 原子占用申请（并发双审核只有一次成功）
    claimed = await session.execute(
        update(MemberGameIdRequest)
        .where(
            MemberGameIdRequest.id == request_id,
            MemberGameIdRequest.guild_id == guild_id,
            MemberGameIdRequest.status == "pending",
        )
        .values(**values)
    )
    if claimed.rowcount != 1:
        await session.rollback()
        raise GameIdRequestError("该申请已被处理，请刷新列表", 409)

    if data.action == "approve":
        # 2) 同事务内检查名称占用（排除目标成员自身）
        occupied = (
            await session.execute(
                select(func.count())
                .select_from(Member)
                .where(
                    Member.guild_id == guild_id,
                    Member.name == new_game_id,
                    Member.id != target_member_id,
                )
            )
        ).scalar_one()
        if occupied:
            await session.rollback()
            raise GameIdRequestError(f"常驻库已存在 ID「{new_game_id}」，请驳回后让帮众重新申请", 409)
        # 3) 条件更新成员旧值 → 新值（旧值已被直接改名时失败）
        updated = await session.execute(
            update(Member)
            .where(
                Member.id == target_member_id,
                Member.guild_id == guild_id,
                Member.name == old_game_id,
            )
            .values(name=new_game_id)
        )
        if updated.rowcount != 1:
            await session.rollback()
            raise GameIdRequestError("该成员 ID 已变更，请刷新后重新审核", 409)

    await _commit_or_raise(session)
    await session.refresh(record)
    return record

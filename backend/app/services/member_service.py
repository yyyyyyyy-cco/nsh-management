"""常驻库业务：CRUD、搜索筛选、出勤率统计。Excel 导入见 utils/excel_import.py。"""
from sqlalchemy import Select, case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.member import Member
from app.schemas.member import MemberCreate, MemberUpdate
from app.utils.constants import MEMBER_STATUSES, PROFESSIONS


class MemberServiceError(Exception):
    """常驻库业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def validate_profession(main: str, sub: str | None) -> None:
    if main not in PROFESSIONS:
        raise MemberServiceError(f"无效的主职业：{main}")
    if sub and sub not in PROFESSIONS:
        raise MemberServiceError(f"无效的副职业：{sub}")


async def get_member(session: AsyncSession, guild_id: int, member_id: int) -> Member:
    member = await session.get(Member, member_id)
    if member is None or member.guild_id != guild_id:
        raise MemberServiceError("成员不存在", 404)
    return member


def apply_filters(stmt: Select, guild_id: int, keyword: str | None, profession: str | None, status: str | None) -> Select:
    stmt = stmt.where(Member.guild_id == guild_id)
    if keyword:
        stmt = stmt.where(Member.name.contains(keyword))
    if profession:
        stmt = stmt.where((Member.main_profession == profession) | (Member.sub_profession == profession))
    if status:
        if status not in MEMBER_STATUSES:
            raise MemberServiceError("无效的状态筛选值")
        stmt = stmt.where(Member.status == status)
    return stmt


async def list_members(
    session: AsyncSession,
    guild_id: int,
    page: int,
    page_size: int,
    keyword: str | None = None,
    profession: str | None = None,
    status: str | None = None,
) -> tuple[list[Member], int, dict]:
    base = apply_filters(select(Member), guild_id, keyword, profession, status)
    total = (await session.execute(select(func.count()).select_from(base.subquery()))).scalar_one()
    # 正式/替补人数（跟随当前筛选条件，供列表页统计展示）
    # 注意：必须引用子查询列 sub.c.status，若引用 ORM 列 Member.status 会令原始表加入 FROM 产生笛卡尔积
    sub = base.subquery()
    status_rows = (
        await session.execute(
            select(sub.c.status, func.count()).select_from(sub).group_by(sub.c.status)
        )
    ).all()
    status_counts = dict(status_rows)
    stats = {
        "formal_count": int(status_counts.get("formal", 0)),
        "substitute_count": int(status_counts.get("substitute", 0)),
    }
    stmt = base.order_by(Member.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = (await session.execute(stmt)).scalars().all()
    return list(items), total, stats


async def profession_stats(session: AsyncSession, guild_id: int) -> list[dict]:
    """职业分布统计（首页仪表盘聚合，避免全量拉取成员）。"""
    rows = (
        await session.execute(
            select(Member.main_profession, func.count())
            .where(Member.guild_id == guild_id)
            .group_by(Member.main_profession)
        )
    ).all()
    return [{"profession": p, "count": c} for p, c in rows]


async def create_member(session: AsyncSession, guild_id: int, data: MemberCreate) -> Member:
    validate_profession(data.main_profession, data.sub_profession)
    if data.status not in MEMBER_STATUSES:
        raise MemberServiceError("无效的成员状态")
    member = Member(guild_id=guild_id, **data.model_dump())
    session.add(member)
    await session.commit()
    await session.refresh(member)
    return member


async def update_member(session: AsyncSession, guild_id: int, member_id: int, data: MemberUpdate) -> Member:
    member = await get_member(session, guild_id, member_id)
    changes = data.model_dump(exclude_unset=True)
    if "main_profession" in changes or "sub_profession" in changes:
        validate_profession(
            changes.get("main_profession", member.main_profession),
            changes.get("sub_profession", member.sub_profession),
        )
    if "status" in changes and changes["status"] not in MEMBER_STATUSES:
        raise MemberServiceError("无效的成员状态")
    for field, value in changes.items():
        setattr(member, field, value)
    await session.commit()
    await session.refresh(member)
    return member


async def delete_member(session: AsyncSession, guild_id: int, member_id: int) -> None:
    member = await get_member(session, guild_id, member_id)
    await session.delete(member)
    await session.commit()


async def batch_delete(session: AsyncSession, guild_id: int, ids: list[int]) -> int:
    members = (
        (await session.execute(select(Member).where(Member.guild_id == guild_id, Member.id.in_(ids)))).scalars().all()
    )
    for member in members:
        await session.delete(member)
    await session.commit()
    return len(members)


async def attendance_rate(session: AsyncSession, guild_id: int) -> list[dict]:
    """各成员出勤率：正常/(正常+请假)，无记录为 None，按出勤率升序。"""
    stats = (
        await session.execute(
            select(
                AttendanceRecord.member_id,
                func.sum(case((AttendanceRecord.status == "normal", 1), else_=0)).label("normal_count"),
                func.sum(case((AttendanceRecord.status == "leave", 1), else_=0)).label("leave_count"),
            )
            .where(AttendanceRecord.is_filler.is_(False), AttendanceRecord.member_id.is_not(None))
            .group_by(AttendanceRecord.member_id)
        )
    ).all()
    stat_map = {member_id: (normal, leave) for member_id, normal, leave in stats}

    members = (await session.execute(select(Member).where(Member.guild_id == guild_id))).scalars().all()
    result = []
    for member in members:
        normal, leave = stat_map.get(member.id, (0, 0))
        rate = round(normal / (normal + leave), 4) if (normal + leave) > 0 else None
        result.append(
            {
                "member_id": member.id,
                "name": member.name,
                "main_profession": member.main_profession,
                "status": member.status,
                "normal_count": int(normal),
                "leave_count": int(leave),
                "attendance_rate": rate,
            }
        )
    result.sort(key=lambda item: (item["attendance_rate"] is None, item["attendance_rate"] or 0))
    return result

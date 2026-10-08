"""出勤导入：一键导入正式成员、替补候选与导入。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.member import Member
from app.services.attendance_service import check_normal_capacity
from app.services.schedule_service import get_schedule


async def _imported_member_ids(session: AsyncSession, schedule_id: int) -> set[int]:
    rows = (
        (
            await session.execute(
                select(AttendanceRecord.member_id).where(
                    AttendanceRecord.schedule_id == schedule_id,
                    AttendanceRecord.member_id.is_not(None),
                )
            )
        )
        .scalars()
        .all()
    )
    # 查询已过滤 NULL；此处再做 None 安全网，保证返回类型确为 set[int]
    return {int(x) for x in rows if x is not None}


async def import_formal(session: AsyncSession, guild_id: int, schedule_id: int) -> dict:
    """一键导入常驻库正式成员（幂等，已导入跳过）。"""
    await get_schedule(session, guild_id, schedule_id)
    imported_ids = await _imported_member_ids(session, schedule_id)
    formal_members = list(
        (await session.execute(select(Member).where(Member.guild_id == guild_id, Member.status == "formal")))
        .scalars()
        .all()
    )
    new_members = [m for m in formal_members if m.id not in imported_ids]
    await check_normal_capacity(session, schedule_id, len(new_members))
    for member in new_members:
        session.add(
            AttendanceRecord(
                schedule_id=schedule_id,
                member_id=member.id,
                member_name=member.name,
                profession=member.main_profession,
                status="normal",
                is_filler=False,
                remark=member.remark,  # 导入时带出常驻库备注（后续可在出勤库内单独修改）
            )
        )
    await session.commit()
    return {"imported": len(new_members), "skipped": len(formal_members) - len(new_members)}


async def substitute_candidates(session: AsyncSession, guild_id: int, schedule_id: int) -> list[Member]:
    """可导入的替补成员：常驻库替补且未导入本场。"""
    await get_schedule(session, guild_id, schedule_id)
    imported_ids = await _imported_member_ids(session, schedule_id)
    substitutes = list(
        (await session.execute(select(Member).where(Member.guild_id == guild_id, Member.status == "substitute")))
        .scalars()
        .all()
    )
    return [m for m in substitutes if m.id not in imported_ids]


async def all_member_candidates(session: AsyncSession, guild_id: int, schedule_id: int) -> list[Member]:
    """常驻库所有成员（正式+替补），已导入本场的排除。"""
    await get_schedule(session, guild_id, schedule_id)
    imported_ids = await _imported_member_ids(session, schedule_id)
    all_members = list((await session.execute(select(Member).where(Member.guild_id == guild_id))).scalars().all())
    return [m for m in all_members if m.id not in imported_ids]


async def import_members(session: AsyncSession, guild_id: int, schedule_id: int, member_ids: list[int]) -> dict:
    """导入选中的常驻库成员（正式/替补均可），已导入的跳过。"""
    await get_schedule(session, guild_id, schedule_id)
    imported_ids = await _imported_member_ids(session, schedule_id)
    members = list(
        (
            await session.execute(
                select(Member).where(
                    Member.guild_id == guild_id,
                    Member.id.in_(member_ids),
                )
            )
        )
        .scalars()
        .all()
    )
    new_members = [m for m in members if m.id not in imported_ids]
    await check_normal_capacity(session, schedule_id, len(new_members))
    for member in new_members:
        session.add(
            AttendanceRecord(
                schedule_id=schedule_id,
                member_id=member.id,
                member_name=member.name,
                profession=member.main_profession,
                status="normal",
                is_filler=False,
                remark=member.remark,  # 导入时带出常驻库备注（后续可在出勤库内单独修改）
            )
        )
    await session.commit()
    return {"imported": len(new_members), "skipped": len(members) - len(new_members)}


async def import_substitutes(session: AsyncSession, guild_id: int, schedule_id: int, member_ids: list[int]) -> dict:
    """导入选中的替补成员。"""
    await get_schedule(session, guild_id, schedule_id)
    imported_ids = await _imported_member_ids(session, schedule_id)
    members = list(
        (
            await session.execute(
                select(Member).where(
                    Member.guild_id == guild_id,
                    Member.status == "substitute",
                    Member.id.in_(member_ids),
                )
            )
        )
        .scalars()
        .all()
    )
    new_members = [m for m in members if m.id not in imported_ids]
    await check_normal_capacity(session, schedule_id, len(new_members))
    for member in new_members:
        session.add(
            AttendanceRecord(
                schedule_id=schedule_id,
                member_id=member.id,
                member_name=member.name,
                profession=member.main_profession,
                status="normal",
                is_filler=False,
                remark=member.remark,  # 导入时带出常驻库备注（后续可在出勤库内单独修改）
            )
        )
    await session.commit()
    return {"imported": len(new_members), "skipped": len(members) - len(new_members)}

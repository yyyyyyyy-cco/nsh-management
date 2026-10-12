"""成员档案查询：出勤明细 / 录屏记录 / 排表历史（成员详情页，仅管理员）。

设计依据：memory-bank/design-member-archive.md §3（数据口径与正确性）：
- 三档案均按 member_id 关联，改名只更新 members.name、历史行不变，天然跨改名正确；
- 排表 JSON 槽位无数据库级清理，须叠加「该场出勤库存在同 member_id」双条件过滤，
  与 lineup_service._purge_deleted_members 判定口径一致（防主键复用误关联，
  见 database-design.md §1.3「主键与 ID 复用口径」）。
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.services import member_service


async def attendance_history(session: AsyncSession, guild_id: int, member_id: int) -> list[dict]:
    """该成员每场出勤明细（按比赛时间倒序，同场唯一）。"""
    await member_service.get_member(session, guild_id, member_id)
    rows = (
        await session.execute(
            select(AttendanceRecord, Schedule)
            .join(Schedule, AttendanceRecord.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, AttendanceRecord.member_id == member_id)
            .order_by(Schedule.match_time.desc(), Schedule.id.desc())
        )
    ).all()
    return [
        {
            "schedule_id": schedule.id,
            "opponent": schedule.opponent,
            "match_time": schedule.match_time,
            "schedule_result": schedule.result,
            "status": record.status,
            "remark": record.remark,
        }
        for record, schedule in rows
    ]


async def recording_history(session: AsyncSession, guild_id: int, member_id: int) -> list[dict]:
    """该成员每场每局录屏提交与审核状态（按比赛时间倒序、同场局号升序；含未提交行）。"""
    await member_service.get_member(session, guild_id, member_id)
    rows = (
        await session.execute(
            select(Recording, Schedule)
            .join(Schedule, Recording.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, Recording.member_id == member_id)
            .order_by(Schedule.match_time.desc(), Schedule.id.desc(), Recording.round_number.asc())
        )
    ).all()
    return [
        {
            "schedule_id": schedule.id,
            "opponent": schedule.opponent,
            "match_time": schedule.match_time,
            "round_number": record.round_number,
            "url": record.url,
            "status": record.status,
            "review_remark": record.review_remark,
        }
        for record, schedule in rows
    ]


async def lineup_history(session: AsyncSession, guild_id: int, member_id: int) -> list[dict]:
    """该成员每场排表位置（按比赛时间倒序，同场唯一）。

    排表槽位 JSON 无数据库级清理：叠加「该场出勤库存在同 member_id」双条件过滤
    （与 _purge_deleted_members 同口径），避免陈旧 member_id 被新成员复用后误算归属。
    """
    await member_service.get_member(session, guild_id, member_id)
    rows = (
        await session.execute(
            select(Lineup.data, Schedule)
            .join(Schedule, Lineup.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id)
            .order_by(Schedule.match_time.desc(), Schedule.id.desc())
        )
    ).all()

    items: list[dict] = []
    for data, schedule in rows:
        for team in data or []:
            for slot in team.get("slots", []):
                if slot.get("member_id") == member_id:
                    items.append(
                        {
                            "schedule_id": schedule.id,
                            "opponent": schedule.opponent,
                            "match_time": schedule.match_time,
                            "category": team.get("category", ""),
                            "team_index": team.get("team_index", 0),
                            "slot_index": slot.get("slot_index", 0),
                            "slot_remark": (slot.get("remark") or "").strip() or None,
                        }
                    )
    if not items:
        return []

    # 双条件过滤：仅保留「该场出勤库存在同 member_id 行」的记录
    schedule_ids = {item["schedule_id"] for item in items}
    valid_ids = set(
        (
            await session.execute(
                select(AttendanceRecord.schedule_id).where(
                    AttendanceRecord.schedule_id.in_(schedule_ids),
                    AttendanceRecord.member_id == member_id,
                )
            )
        ).scalars()
    )
    return [item for item in items if item["schedule_id"] in valid_ids]

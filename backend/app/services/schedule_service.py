"""联赛日程业务：CRUD、级联创建（空排表）、级联删除。"""
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.match_data import MatchData
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate

SCHEDULE_RESULTS = ["win", "lose", "draw", "pending"]


class ScheduleServiceError(Exception):
    """赛程业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_schedule(session: AsyncSession, guild_id: int, schedule_id: int) -> Schedule:
    schedule = await session.get(Schedule, schedule_id)
    if schedule is None or schedule.guild_id != guild_id:
        raise ScheduleServiceError("赛程不存在", 404)
    return schedule


async def list_schedules(
    session: AsyncSession,
    guild_id: int,
    start: datetime | None = None,
    end: datetime | None = None,
) -> list[Schedule]:
    stmt = select(Schedule).where(Schedule.guild_id == guild_id)
    if start:
        stmt = stmt.where(Schedule.match_time >= start)
    if end:
        stmt = stmt.where(Schedule.match_time < end)
    stmt = stmt.order_by(Schedule.match_time)
    return list((await session.execute(stmt)).scalars().all())


async def create_schedule(session: AsyncSession, guild_id: int, data: ScheduleCreate) -> Schedule:
    """创建赛程并级联创建空排表（1:1）。"""
    schedule = Schedule(guild_id=guild_id, **data.model_dump())
    session.add(schedule)
    await session.flush()
    session.add(Lineup(schedule_id=schedule.id, data=[]))
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def update_schedule(session: AsyncSession, guild_id: int, schedule_id: int, data: ScheduleUpdate) -> Schedule:
    schedule = await get_schedule(session, guild_id, schedule_id)
    changes = data.model_dump(exclude_unset=True)
    if "result" in changes and changes["result"] not in SCHEDULE_RESULTS:
        raise ScheduleServiceError("无效的比赛结果")
    if "round_results" in changes:
        round_results = changes["round_results"]
        if not round_results or len(round_results) != schedule.rounds:
            raise ScheduleServiceError(f"每局结果数量必须与局数（{schedule.rounds}）一致")
        if any(r not in SCHEDULE_RESULTS for r in round_results):
            raise ScheduleServiceError("无效的局结果")
    for field, value in changes.items():
        setattr(schedule, field, value)
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def delete_schedule(session: AsyncSession, guild_id: int, schedule_id: int) -> None:
    """级联删除：录屏 → 分析 → 出勤 → 排表 → 赛程（database-design §3.2）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)
    await session.execute(delete(Recording).where(Recording.schedule_id == schedule_id))
    await session.execute(delete(MatchData).where(MatchData.schedule_id == schedule_id))
    await session.execute(delete(AttendanceRecord).where(AttendanceRecord.schedule_id == schedule_id))
    await session.execute(delete(Lineup).where(Lineup.schedule_id == schedule_id))
    await session.delete(schedule)
    await session.commit()

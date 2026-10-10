"""联赛日程业务：CRUD、级联创建（空排表）、级联删除。"""

from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.match_data import MatchData
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.models.squad_adjustment import SquadAdjustment
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.services import profession_service

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
    stmt = stmt.order_by(Schedule.match_time.desc())
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


async def update_profession_config(
    session: AsyncSession, guild_id: int, schedule_id: int, configs: dict[str, int] | None
) -> Schedule:
    """设置/清除单场职业配置覆盖。configs 为 None 时恢复默认（沿用系统配置）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)
    if configs is not None:
        # 旧值豁免：该赛程既有覆盖键允许保留（对应职业可能已停用），新增键必须为启用职业
        existing = set((schedule.profession_config or {}).keys())
        active = await profession_service.active_names(session)
        for profession, target in configs.items():
            if profession not in active and profession not in existing:
                raise ScheduleServiceError(f"无效的职业：{profession}")
            if not isinstance(target, int) or not 0 <= target <= 60:
                raise ScheduleServiceError(f"职业「{profession}」的目标人数无效（0-60）")
    schedule.profession_config = configs
    await session.commit()
    await session.refresh(schedule)
    return schedule


async def delete_schedule(session: AsyncSession, guild_id: int, schedule_id: int) -> None:
    """级联删除：录屏 → 分析 → 出勤 → 排表 → 赛程（database-design §3.2）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)
    await session.execute(delete(Recording).where(Recording.schedule_id == schedule_id))
    await session.execute(delete(MatchData).where(MatchData.schedule_id == schedule_id))
    # 分析调整副本必须先于赛程删除，否则成为孤儿行；且 SQLite 未启用 sqlite_autoincrement 时
    # schedules.id 可能被复用，新赛程会"继承"旧分析调整（2026-10-03 修复，见 F-75 / database-design §3.2）
    await session.execute(delete(SquadAdjustment).where(SquadAdjustment.schedule_id == schedule_id))
    await session.execute(delete(AttendanceRecord).where(AttendanceRecord.schedule_id == schedule_id))
    await session.execute(delete(Lineup).where(Lineup.schedule_id == schedule_id))
    await session.delete(schedule)
    await session.commit()

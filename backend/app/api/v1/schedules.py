"""联赛日程接口：赛程 CRUD，创建级联建空排表，删除级联清理关联数据。"""
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_admin
from app.core.database import get_db
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleOut, ScheduleUpdate
from app.services import schedule_service

router = APIRouter(prefix="/schedules", tags=["联赛日程"])


@router.get("", response_model=list[ScheduleOut])
async def list_schedules(
    start: datetime | None = Query(None),
    end: datetime | None = Query(None),
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> list[ScheduleOut]:
    schedules = await schedule_service.list_schedules(session, current_user.guild_id, start, end)
    return [ScheduleOut.model_validate(s) for s in schedules]


@router.post("", response_model=ScheduleOut)
async def create_schedule(
    body: ScheduleCreate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ScheduleOut:
    schedule = await schedule_service.create_schedule(session, current_user.guild_id, body)
    return ScheduleOut.model_validate(schedule)


@router.get("/{schedule_id}", response_model=ScheduleOut)
async def get_schedule(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ScheduleOut:
    schedule = await schedule_service.get_schedule(session, current_user.guild_id, schedule_id)
    return ScheduleOut.model_validate(schedule)


@router.put("/{schedule_id}", response_model=ScheduleOut)
async def update_schedule(
    schedule_id: int,
    body: ScheduleUpdate,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> ScheduleOut:
    schedule = await schedule_service.update_schedule(session, current_user.guild_id, schedule_id, body)
    return ScheduleOut.model_validate(schedule)


@router.delete("/{schedule_id}")
async def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(require_admin),
    session: AsyncSession = Depends(get_db),
) -> dict:
    await schedule_service.delete_schedule(session, current_user.guild_id, schedule_id)
    return {"message": "删除成功"}

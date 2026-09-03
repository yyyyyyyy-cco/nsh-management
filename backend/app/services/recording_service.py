"""录屏审核业务：列表、提交、审核、批量审核、进度统计。"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.services.schedule_service import get_schedule

RECORDING_STATUSES = ["pending", "approved", "rejected"]


class RecordingServiceError(Exception):
    """录屏审核业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def ensure_recordings(session: AsyncSession, schedule: Schedule, attendance_records: list[AttendanceRecord]) -> list[Recording]:
    """确保录屏占位记录存在，如果不存在则创建。"""
    # 查询已有录屏记录
    existing = (
        await session.execute(
            select(Recording).where(Recording.schedule_id == schedule.id)
        )
    ).scalars().all()

    # 索引键与数据库唯一约束 (schedule_id, member_id, round_number) 对齐：
    # 有 member_id 的按 member_id 匹配（成员改名后仍能命中旧记录，避免撞唯一约束），
    # member_id 为空的按姓名兜底
    existing_map = {}
    for r in existing:
        if r.member_id is not None:
            key = (f"id:{r.member_id}", r.round_number)
        else:
            key = (f"name:{r.member_name}", r.round_number)
        existing_map.setdefault(key, r)

    # 同一成员只处理一次（按 member_id 去重，防止同名多条出勤导致重复占位）
    seen_members = set()
    recordings = []
    name_changed = False
    for record in attendance_records:
        if record.member_id is not None:
            member_key = f"id:{record.member_id}"
        else:
            member_key = f"name:{record.member_name}"
        if member_key in seen_members:
            continue
        seen_members.add(member_key)
        for round_num in range(1, schedule.rounds + 1):
            key = (member_key, round_num)
            found = existing_map.get(key)
            if found is not None:
                # 成员改名：跟随出勤库刷新姓名，而不是新建占位
                if found.member_name != record.member_name:
                    found.member_name = record.member_name
                    name_changed = True
                recordings.append(found)
            else:
                # 创建新的占位记录，并写回索引防止重复创建
                new_recording = Recording(
                    schedule_id=schedule.id,
                    member_id=record.member_id,
                    member_name=record.member_name,
                    round_number=round_num,
                    url=None,
                    status="pending",
                )
                session.add(new_recording)
                existing_map[key] = new_recording
                recordings.append(new_recording)

    if any(r.id is None for r in recordings) or name_changed:
        await session.commit()
        # 刷新新创建的记录以获取 ID
        for r in recordings:
            if r.id is None:
                await session.refresh(r)

    return recordings


async def list_recordings(
    session: AsyncSession, guild_id: int, schedule_id: int
) -> tuple[list[Recording], list[dict]]:
    """获取录屏列表和各局审核进度。"""
    schedule = await get_schedule(session, guild_id, schedule_id)

    # 录屏审核范围：正式/替补（非补人）且状态正常的人员（补人与请假无需提交录屏）
    attendance_records = list(
        (
            await session.execute(
                select(AttendanceRecord).where(
                    AttendanceRecord.schedule_id == schedule_id,
                    AttendanceRecord.status == "normal",
                    AttendanceRecord.is_filler.is_(False),
                )
            )
        )
        .scalars()
        .all()
    )

    # 确保录屏占位记录存在
    recordings = await ensure_recordings(session, schedule, attendance_records)

    # 填充职业快照（按姓名匹配出勤库，补人与常驻成员均适用）
    prof_map = {a.member_name: a.profession for a in attendance_records}
    for r in recordings:
        r.profession = prof_map.get(r.member_name)

    # 按 member_name 和 round_number 排序
    recordings.sort(key=lambda r: (r.member_name, r.round_number))

    # 计算各局进度
    progress = []
    for round_num in range(1, schedule.rounds + 1):
        round_records = [r for r in recordings if r.round_number == round_num]
        total = len(round_records)
        approved = sum(1 for r in round_records if r.status == "approved")
        rejected = sum(1 for r in round_records if r.status == "rejected")
        # 待审 = 已填写链接且未审核；未填链接的占位记录不计入
        pending = sum(1 for r in round_records if r.status == "pending" and r.url)
        progress.append({
            "round_number": round_num,
            "total": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
        })

    return recordings, progress


async def submit_recording(
    session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int, url: str
) -> Recording:
    """提交录屏链接（帮众可操作）。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    recording.url = url
    recording.status = "pending"  # 重新提交回到待审核
    recording.review_remark = None
    recording.reviewed_at = None
    await session.commit()
    await session.refresh(recording)
    return recording


async def approve_recording(
    session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int, remark: str | None = None
) -> Recording:
    """审核通过（管理员）。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    if not recording.url:
        raise RecordingServiceError("该录屏尚未提交链接")

    recording.status = "approved"
    recording.review_remark = remark
    recording.reviewed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(recording)
    return recording


async def reject_recording(
    session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int, remark: str | None = None
) -> Recording:
    """审核驳回（管理员）。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    if not recording.url:
        raise RecordingServiceError("该录屏尚未提交链接")

    recording.status = "rejected"
    recording.review_remark = remark
    recording.reviewed_at = datetime.now(timezone.utc)
    await session.commit()
    await session.refresh(recording)
    return recording


async def batch_approve(
    session: AsyncSession, guild_id: int, schedule_id: int, ids: list[int]
) -> int:
    """批量审核通过（管理员）。"""
    await get_schedule(session, guild_id, schedule_id)

    recordings = list(
        (
            await session.execute(
                select(Recording).where(
                    Recording.schedule_id == schedule_id,
                    Recording.id.in_(ids),
                    Recording.url.isnot(None),  # 只审核已提交的
                )
            )
        )
        .scalars()
        .all()
    )

    now = datetime.now(timezone.utc)
    for recording in recordings:
        recording.status = "approved"
        recording.reviewed_at = now

    await session.commit()
    return len(recordings)


async def get_recording_by_id(
    session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int
) -> Recording:
    """获取单条录屏记录。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    return recording

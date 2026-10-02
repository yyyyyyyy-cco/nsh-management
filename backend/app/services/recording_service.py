"""录屏审核业务：列表、提交、审核、批量审核、进度统计。"""

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
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


def _recording_key(r: Recording) -> tuple:
    """索引键与数据库唯一约束 (schedule_id, member_id, round_number) 对齐：
    有 member_id 的按 member_id 匹配（成员改名后仍能命中旧记录，避免撞唯一约束），
    member_id 为空的按姓名兜底。"""
    if r.member_id is not None:
        return (f"id:{r.member_id}", r.round_number)
    return (f"name:{r.member_name}", r.round_number)


async def _load_recording_map(session: AsyncSession, schedule_id: int) -> dict[tuple, Recording]:
    existing = (await session.execute(select(Recording).where(Recording.schedule_id == schedule_id))).scalars().all()
    existing_map: dict[tuple, Recording] = {}
    for r in existing:
        existing_map.setdefault(_recording_key(r), r)
    return existing_map


async def ensure_recordings(
    session: AsyncSession, schedule: Schedule, attendance_records: list[AttendanceRecord]
) -> list[Recording]:
    """确保录屏占位记录存在。

    缺失占位用单条 INSERT OR IGNORE 批量插入（并发下撞唯一约束时静默跳过，避免 500），
    随后重新查询取回全部记录（含 id）。
    """
    existing_map = await _load_recording_map(session, schedule.id)

    # 同一成员只处理一次（按 member_id 去重，防止同名多条出勤导致重复占位）
    seen_members = set()
    planned: list[tuple[tuple, AttendanceRecord]] = []
    to_insert = []
    for record in attendance_records:
        member_key = f"id:{record.member_id}" if record.member_id is not None else f"name:{record.member_name}"
        if member_key in seen_members:
            continue
        seen_members.add(member_key)
        for round_num in range(1, schedule.rounds + 1):
            key = (member_key, round_num)
            planned.append((key, record))
            if key not in existing_map:
                to_insert.append(
                    {
                        "schedule_id": schedule.id,
                        "member_id": record.member_id,
                        "member_name": record.member_name,
                        "round_number": round_num,
                        "url": None,
                        "status": "pending",
                    }
                )

    if to_insert:
        await session.execute(sqlite_insert(Recording).values(to_insert).on_conflict_do_nothing())
        await session.commit()
        # 重新查询：取回本请求前已存在的记录与刚插入的记录（含数据库生成的 id）
        existing_map = await _load_recording_map(session, schedule.id)

    name_changed = False
    recordings = []
    for key, record in planned:
        found = existing_map.get(key)
        if found is None:
            continue
        # 成员改名：跟随出勤库刷新姓名，而不是新建占位
        if found.member_name != record.member_name:
            found.member_name = record.member_name
            name_changed = True
        recordings.append(found)

    if name_changed:
        await session.commit()

    return recordings


async def list_recordings(session: AsyncSession, guild_id: int, schedule_id: int) -> tuple[list[Recording], list[dict]]:
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
        progress.append(
            {
                "round_number": round_num,
                "total": total,
                "approved": approved,
                "rejected": rejected,
                "pending": pending,
            }
        )

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


async def submit_note(
    session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int, note: str
) -> Recording:
    """提交备注（帮众可操作；自由内容，不改变审核状态）。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    note = note.strip()
    if not note:
        raise RecordingServiceError("备注内容不能为空")

    recording.note = note
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
    recording.reviewed_at = datetime.now(UTC)
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
    recording.reviewed_at = datetime.now(UTC)
    await session.commit()
    await session.refresh(recording)
    return recording


async def batch_approve(session: AsyncSession, guild_id: int, schedule_id: int, ids: list[int]) -> int:
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

    now = datetime.now(UTC)
    for recording in recordings:
        recording.status = "approved"
        recording.reviewed_at = now

    await session.commit()
    return len(recordings)


async def get_recording_by_id(session: AsyncSession, guild_id: int, schedule_id: int, recording_id: int) -> Recording:
    """获取单条录屏记录。"""
    await get_schedule(session, guild_id, schedule_id)

    recording = await session.get(Recording, recording_id)
    if recording is None or recording.schedule_id != schedule_id:
        raise RecordingServiceError("录屏记录不存在", 404)

    return recording

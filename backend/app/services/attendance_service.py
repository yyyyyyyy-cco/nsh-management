"""出勤库业务：列表统计、添加补人、状态切换、删除与保存校验。导入逻辑见 utils/attendance_import.py。"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.member import Member
from app.services.schedule_service import get_schedule
from app.utils.constants import PROFESSIONS
from app.utils.member_names import normalize_member_name

MAX_NORMAL_COUNT = 60  # 出勤表正常状态人数上限（v2 §6.2）

ATTENDANCE_STATUSES = ["normal", "leave"]


class AttendanceServiceError(Exception):
    """出勤库业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def calc_stats(records: list[AttendanceRecord]) -> dict:
    normal = sum(1 for r in records if r.status == "normal")
    leave = len(records) - normal
    return {
        "total": len(records),
        "normal_count": normal,
        "leave_count": leave,
        "gap": max(0, MAX_NORMAL_COUNT - normal),
    }


async def check_normal_capacity(session: AsyncSession, schedule_id: int, add_count: int) -> None:
    """校验新增后正常人数不超过 60 人上限。"""
    normal = (
        await session.execute(
            select(func.count())
            .select_from(AttendanceRecord)
            .where(AttendanceRecord.schedule_id == schedule_id, AttendanceRecord.status == "normal")
        )
    ).scalar_one()
    if normal + add_count > MAX_NORMAL_COUNT:
        raise AttendanceServiceError(
            f"正常状态人数已达上限（{MAX_NORMAL_COUNT} 人），当前 {normal} 人，最多还能添加 {MAX_NORMAL_COUNT - normal} 人"  # noqa: E501
        )


async def list_attendance(
    session: AsyncSession, guild_id: int, schedule_id: int
) -> tuple[list[AttendanceRecord], dict]:
    await get_schedule(session, guild_id, schedule_id)
    rows = (
        await session.execute(
            select(AttendanceRecord, Member.status, Member.main_profession, Member.sub_profession)
            .outerjoin(Member, Member.id == AttendanceRecord.member_id)
            .where(AttendanceRecord.schedule_id == schedule_id)
            .order_by(AttendanceRecord.is_filler, AttendanceRecord.member_name)
        )
    ).all()
    records: list[AttendanceRecord] = []
    for record, member_status, main_profession, sub_profession in rows:
        record.member_status = member_status  # 供响应输出正式/替补标记
        # 可选职业：主+副去重（与 update_record_profession 校验口径一致，切换后仍保留另一职业）；
        # 当前快照不在主/副中时补齐，保证下拉框能正确回显（补人仅当前职业）
        options: list[str] = []
        if main_profession:
            options.append(main_profession)
        if sub_profession and sub_profession not in options:
            options.append(sub_profession)
        if record.profession and record.profession not in options:
            options.append(record.profession)
        record.professions = options
        records.append(record)
    return records, calc_stats(records)


async def update_record_profession(
    session: AsyncSession, guild_id: int, schedule_id: int, record_id: int, profession: str
) -> AttendanceRecord:
    """更新出勤记录的职业快照（主/副职业之一）。"""
    await get_schedule(session, guild_id, schedule_id)
    record = await session.get(AttendanceRecord, record_id)
    if record is None or record.schedule_id != schedule_id:
        raise AttendanceServiceError("出勤记录不存在", 404)
    if profession not in PROFESSIONS:
        raise AttendanceServiceError(f"无效的职业：{profession}")
    # 校验职业在该成员可选范围内（常驻成员主/副，补人仅当前）
    if record.member_id is not None:
        member = await session.get(Member, record.member_id)
        allowed = {member.main_profession, member.sub_profession} if member else {record.profession}
        allowed.discard(None)
        if profession not in allowed:
            raise AttendanceServiceError("只能选择该成员的主职业或副职业")
    elif profession != record.profession:
        raise AttendanceServiceError("补人职业不可修改")
    record.profession = profession
    await session.commit()
    await session.refresh(record)
    return record


async def update_record_remark(
    session: AsyncSession, guild_id: int, schedule_id: int, record_id: int, remark: str
) -> AttendanceRecord:
    """更新出勤记录备注（管理员；留空清除）。导入时带出常驻库备注，此处可单独修改。"""
    await get_schedule(session, guild_id, schedule_id)
    record = await session.get(AttendanceRecord, record_id)
    if record is None or record.schedule_id != schedule_id:
        raise AttendanceServiceError("出勤记录不存在", 404)
    normalized = (remark or "").strip()
    if len(normalized) > 255:
        raise AttendanceServiceError("备注长度不能超过 255 字")
    record.remark = normalized or None
    await session.commit()
    await session.refresh(record)
    return record


async def add_filler(
    session: AsyncSession, guild_id: int, schedule_id: int, name: str, profession: str
) -> AttendanceRecord:
    """添加补人：仅当前场次，不录入常驻库。"""
    await get_schedule(session, guild_id, schedule_id)
    name = normalize_member_name(name)
    if not name:
        raise AttendanceServiceError("请输入补人名称，不能只包含空白字符")
    if len(name) > 32:
        raise AttendanceServiceError("补人姓名不能超过 32 字符")
    if profession not in PROFESSIONS:
        raise AttendanceServiceError(f"无效的职业：{profession}")
    existing_names = (
        (await session.execute(select(AttendanceRecord.member_name).where(AttendanceRecord.schedule_id == schedule_id)))
        .scalars()
        .all()
    )
    # Python 统一处理全角等空白；同时兼容历史记录，防止与常驻成员的姓名映射冲突。
    if any(normalize_member_name(existing) == name for existing in existing_names):
        raise AttendanceServiceError(f"姓名「{name}」已在本场出勤表中（忽略首尾空白）")
    await check_normal_capacity(session, schedule_id, 1)
    record = AttendanceRecord(
        schedule_id=schedule_id,
        member_id=None,
        member_name=name,
        profession=profession,
        status="normal",
        is_filler=True,
    )
    session.add(record)
    await session.commit()
    await session.refresh(record)
    return record


async def update_status(
    session: AsyncSession, guild_id: int, schedule_id: int, record_id: int, status: str
) -> AttendanceRecord:
    """切换单条出勤状态（正常/请假），帮众可操作。"""
    await get_schedule(session, guild_id, schedule_id)
    if status not in ATTENDANCE_STATUSES:
        raise AttendanceServiceError("无效的出勤状态")
    record = await session.get(AttendanceRecord, record_id)
    if record is None or record.schedule_id != schedule_id:
        raise AttendanceServiceError("出勤记录不存在", 404)
    record.status = status
    await session.commit()
    await session.refresh(record)
    return record


async def batch_update_status(
    session: AsyncSession, guild_id: int, schedule_id: int, ids: list[int], status: str
) -> int:
    """批量切换出勤状态（管理员）。"""
    await get_schedule(session, guild_id, schedule_id)
    if status not in ATTENDANCE_STATUSES:
        raise AttendanceServiceError("无效的出勤状态")
    records = list(
        (
            await session.execute(
                select(AttendanceRecord).where(
                    AttendanceRecord.schedule_id == schedule_id,
                    AttendanceRecord.id.in_(ids),
                )
            )
        )
        .scalars()
        .all()
    )
    for record in records:
        record.status = status
    await session.commit()
    return len(records)


async def delete_record(session: AsyncSession, guild_id: int, schedule_id: int, record_id: int) -> None:
    """删除出勤记录（管理员，用于移除误添加的补人等）。"""
    await get_schedule(session, guild_id, schedule_id)
    record = await session.get(AttendanceRecord, record_id)
    if record is None or record.schedule_id != schedule_id:
        raise AttendanceServiceError("出勤记录不存在", 404)
    await session.delete(record)
    await session.commit()

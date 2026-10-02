"""排表的出勤关联：职业映射、姓名冲突检查与候选池。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.member import Member
from app.services.schedule_service import get_schedule
from app.utils.member_names import normalize_member_name


class LineupServiceError(Exception):
    """排表业务异常，由 lineup_service 继续导出供原调用方使用。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_profession_map(session: AsyncSession, schedule_id: int) -> dict[str, str | None]:
    """按规范化姓名关联职业；历史重名必须明确报错，不能静默覆盖。"""
    rows = (
        await session.execute(
            select(AttendanceRecord.member_name, AttendanceRecord.profession).where(
                AttendanceRecord.schedule_id == schedule_id
            )
        )
    ).all()
    professions: dict[str, str | None] = {}
    for name, profession in rows:
        normalized = normalize_member_name(name)
        if not normalized:
            raise LineupServiceError("出勤库存在空白姓名，请先处理对应记录后重试", 409)
        if normalized in professions:
            raise LineupServiceError(
                f"出勤库姓名「{normalized}」去除首尾空白后存在重名，请先处理冲突记录后重试", 409
            )
        professions[normalized] = profession
    return professions


async def candidate_pool(session: AsyncSession, guild_id: int, schedule_id: int) -> list[dict]:
    """候选池：出勤正常成员；补人姓名与排表读取、保存使用相同规则。"""
    await get_schedule(session, guild_id, schedule_id)
    # 包含请假记录的全场次校验，避免同名补人被错误归并或清空。
    await get_profession_map(session, schedule_id)
    rows = (
        await session.execute(
            select(
                AttendanceRecord.member_id,
                AttendanceRecord.member_name,
                AttendanceRecord.profession,
                Member.status,
                AttendanceRecord.remark,
            )
            .outerjoin(Member, Member.id == AttendanceRecord.member_id)
            .where(AttendanceRecord.schedule_id == schedule_id, AttendanceRecord.status == "normal")
            .order_by(AttendanceRecord.is_filler, AttendanceRecord.member_name)
        )
    ).all()
    return [
        {
            "member_id": mid,
            "member_name": normalize_member_name(name) if mid is None else name,
            "profession": profession,
            "member_status": "filler" if member_status is None else member_status,
            "attendance_remark": attendance_remark,
        }
        for mid, name, profession, member_status, attendance_remark in rows
    ]

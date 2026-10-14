"""排表的出勤关联：职业映射、姓名冲突检查、候选池与失效槽位清理。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
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
            raise LineupServiceError(f"出勤库姓名「{normalized}」去除首尾空白后存在重名，请先处理冲突记录后重试", 409)
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
                AttendanceRecord.is_filler,
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
            # 三档判定：真补人 → filler；非补人但关联不到常驻库（成员已删除的姓名快照）→ deleted；
            # 其余取常驻库状态（formal / substitute）
            "member_status": "filler" if is_filler else ("deleted" if member_status is None else member_status),
            "attendance_remark": attendance_remark,
        }
        for mid, name, profession, is_filler, member_status, attendance_remark in rows
    ]


async def purge_leave_members(session: AsyncSession, lineup: Lineup, schedule_id: int) -> None:
    """将出勤库中已请假成员从排表槽位清空（正式按 ID、补人按姓名匹配）。

    自 lineup_service 迁入（2026-10-14，该服务临近 300 行硬限；与失效槽位清理同属「出勤→排表」联动）。
    """
    leave_ids: set[int] = set()
    leave_names: set[str] = set()
    rows = (
        await session.execute(
            select(AttendanceRecord.member_id, AttendanceRecord.member_name, AttendanceRecord.is_filler).where(
                AttendanceRecord.schedule_id == schedule_id,
                AttendanceRecord.status == "leave",
            )
        )
    ).all()
    for mid, name, is_filler in rows:
        if mid is not None:
            leave_ids.add(mid)
        elif is_filler:
            leave_names.add(normalize_member_name(name))

    if not leave_ids and not leave_names:
        return

    changed = False
    new_data = []
    for team in lineup.data:
        slots = []
        for slot in team["slots"]:
            mid = slot.get("member_id")
            name = normalize_member_name(slot.get("member_name"))
            if mid is not None and mid in leave_ids:
                changed = True
                slot = {**slot, "member_id": None, "member_name": ""}
            elif mid is None and name in leave_names:
                changed = True
                slot = {**slot, "member_name": ""}
            slots.append(slot)
        new_data.append({**team, "slots": slots})

    if changed:
        # JSON 列嵌套修改需整体替换才能触发变更检测
        lineup.data = new_data
        await session.commit()


async def purge_stale_slots(session: AsyncSession, lineup: Lineup, schedule_id: int) -> None:
    """将「本场出勤库中已不存在」的成员与补人从排表槽位清空（排表以出勤库为准）。

    两类失效（均按本场出勤库判定）：
    - 正式槽位（member_id 非空）：id 不在出勤库；其中成员已删除的姓名快照
      （member_id 为空且 is_filler=False）仍在时，转补人形态保留（历史排表不丢人且不残留悬空 member_id），
      无快照则清空；
    - 补人/快照槽位（member_id 为空且有姓名）：规范化姓名在本场出勤库完全不存在
      （对应出勤记录已被删除）→ 清空（2026-10-14，与正式成员口径统一）。
    """
    ids = {slot.get("member_id") for team in lineup.data for slot in team["slots"] if slot.get("member_id")}
    has_named_slot = any(
        slot.get("member_id") is None and normalize_member_name(slot.get("member_name"))
        for team in lineup.data
        for slot in team["slots"]
    )
    if not ids and not has_named_slot:
        return

    valid_ids: set[int] = set()
    if ids:
        valid_ids = set(
            (
                await session.execute(
                    select(AttendanceRecord.member_id).where(
                        AttendanceRecord.schedule_id == schedule_id,
                        AttendanceRecord.member_id.in_(ids),
                    )
                )
            ).scalars()
        )
    stale_ids = ids - valid_ids

    # 成员已删除的残留姓名快照（非补人；与出勤库真补人 is_filler=True 区分）
    deleted_names: set[str] = set()
    if stale_ids:
        deleted_names = {
            normalize_member_name(name)
            for name in (
                await session.execute(
                    select(AttendanceRecord.member_name).where(
                        AttendanceRecord.schedule_id == schedule_id,
                        AttendanceRecord.member_id.is_(None),
                        AttendanceRecord.is_filler.is_(False),
                    )
                )
            ).scalars()
        }

    # 本场出勤库全部姓名（正式/补人/快照/请假均计入）：补人槽位的有效性依据
    valid_names: set[str] = set()
    if has_named_slot:
        valid_names = {
            normalize_member_name(name)
            for name in (
                await session.execute(
                    select(AttendanceRecord.member_name).where(AttendanceRecord.schedule_id == schedule_id)
                )
            ).scalars()
        }

    changed = False
    new_data = []
    for team in lineup.data:
        slots = []
        for slot in team["slots"]:
            mid = slot.get("member_id")
            name = normalize_member_name(slot.get("member_name"))
            if mid is not None and mid in stale_ids:
                changed = True
                if name and name in deleted_names:
                    # 姓名快照在库：保留为补人形态（历史排表不丢人，也不残留悬空 member_id）
                    slot = {**slot, "member_id": None, "member_name": name}
                else:
                    slot = {**slot, "member_id": None, "member_name": ""}
            elif mid is None and name and name not in valid_names:
                # 补人/快照的出勤记录已被删除：同步清空（与正式成员口径统一）
                changed = True
                slot = {**slot, "member_name": ""}
            slots.append(slot)
        new_data.append({**team, "slots": slots})

    if changed:
        lineup.data = new_data
        await session.commit()

"""排表业务：候选池（出勤库正常成员）、排表读写与保存校验。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.member import Member
from app.models.schedule import Schedule
from app.services.schedule_service import get_schedule
from app.utils.constants import LINEUP_LAYOUT, SLOTS_PER_TEAM


class LineupServiceError(Exception):
    """排表业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def empty_lineup_data() -> list[dict]:
    """生成标准空排表结构：10 队 × 6 槽。"""
    data = []
    for category, team_count in LINEUP_LAYOUT:
        for team_index in range(team_count):
            data.append(
                {
                    "category": category,
                    "team_index": team_index,
                    "remark": "",
                    "slots": [
                        {"slot_index": i, "member_id": None, "member_name": "", "remark": ""}
                        for i in range(SLOTS_PER_TEAM)
                    ],
                }
            )
    return data


def _validate_structure(data: list[dict]) -> None:
    """校验排表结构与固定布局一致（分类、队序、槽位）。"""
    if len(data) != sum(count for _, count in LINEUP_LAYOUT):
        raise LineupServiceError("排表队伍数量必须为 10 队")
    expected = [(cat, idx) for cat, count in LINEUP_LAYOUT for idx in range(count)]
    for team, (cat, idx) in zip(data, expected):
        if team.get("category") != cat or team.get("team_index") != idx:
            raise LineupServiceError("排表队伍分类或顺序与固定结构不一致")
        slots = team.get("slots", [])
        if len(slots) != SLOTS_PER_TEAM:
            raise LineupServiceError(f"{cat} 第 {idx + 1} 队槽位数必须为 {SLOTS_PER_TEAM}")
        for slot, slot_index in zip(slots, range(SLOTS_PER_TEAM)):
            if slot.get("slot_index") != slot_index:
                raise LineupServiceError(f"{cat} 第 {idx + 1} 队槽位序号不合法")


async def _purge_leave_members(session: AsyncSession, lineup: Lineup, schedule_id: int) -> None:
    """将出勤库中已请假成员从排表槽位清空（正式按 ID、补人按姓名匹配）。"""
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
            leave_names.add(name)

    if not leave_ids and not leave_names:
        return

    changed = False
    new_data = []
    for team in lineup.data:
        slots = []
        for slot in team["slots"]:
            mid = slot.get("member_id")
            name = slot.get("member_name") or ""
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


async def _purge_deleted_members(session: AsyncSession, lineup: Lineup, schedule_id: int) -> None:
    """将本场出勤库中已不存在的成员从排表槽位清空（按 member_id 匹配）。"""
    ids = {slot.get("member_id") for team in lineup.data for slot in team["slots"] if slot.get("member_id")}
    if not ids:
        return
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
    if not stale_ids:
        return

    changed = False
    new_data = []
    for team in lineup.data:
        slots = []
        for slot in team["slots"]:
            if slot.get("member_id") in stale_ids:
                changed = True
                slot = {**slot, "member_id": None, "member_name": ""}
            slots.append(slot)
        new_data.append({**team, "slots": slots})

    if changed:
        lineup.data = new_data
        await session.commit()


async def get_lineup(session: AsyncSession, guild_id: int, schedule_id: int) -> Lineup:
    """获取排表；无数据时落库标准空结构（保证 1:1 存在且结构稳定）。"""
    await get_schedule(session, guild_id, schedule_id)
    lineup = (
        await session.execute(select(Lineup).where(Lineup.schedule_id == schedule_id))
    ).scalar_one_or_none()
    if lineup is None:
        lineup = Lineup(schedule_id=schedule_id, data=[])
        session.add(lineup)
        await session.commit()
        await session.refresh(lineup)
    if not lineup.data:
        lineup.data = empty_lineup_data()
        await session.commit()
        await session.refresh(lineup)
    # 请假成员自动移出排表（出勤库状态变动后同步）
    await _purge_leave_members(session, lineup, schedule_id)
    # 出勤库中已不存在的成员自动移出排表
    await _purge_deleted_members(session, lineup, schedule_id)
    return lineup


async def get_profession_map(session: AsyncSession, schedule_id: int) -> dict[str, str | None]:
    """出勤库职业快照映射（按姓名，供排表读取时填充槽位职业）。"""
    rows = (
        await session.execute(
            select(AttendanceRecord.member_name, AttendanceRecord.profession).where(
                AttendanceRecord.schedule_id == schedule_id
            )
        )
    ).all()
    return {name: prof for name, prof in rows}


async def save_lineup(
    session: AsyncSession, guild_id: int, schedule_id: int, data: list[dict],
    title_remark: str = "", groups_remark: dict | None = None,
) -> Lineup:
    """保存排表：校验结构、成员归属本帮会、按数据库规范化姓名，同时保存团/标题备注。"""
    lineup = await get_lineup(session, guild_id, schedule_id)
    _validate_structure(data)

    member_ids = {s["member_id"] for team in data for s in team["slots"] if s.get("member_id")}
    name_map: dict[int, str] = {}
    if member_ids:
        # 槽位成员必须来自本场出勤库（排表以出勤库为准，而非常驻库）
        rows = (
            await session.execute(
                select(AttendanceRecord.member_id, AttendanceRecord.member_name).where(
                    AttendanceRecord.schedule_id == schedule_id,
                    AttendanceRecord.member_id.in_(member_ids),
                )
            )
        ).all()
        name_map = {mid: name for mid, name in rows}
        missing = member_ids - set(name_map)
        if missing:
            raise LineupServiceError("排表包含本场出勤库中不存在的成员，请刷新后重试", 400)

    for team in data:
        team["remark"] = (team.get("remark") or "").strip()
        for slot in team["slots"]:
            if slot.get("member_id") is not None:
                slot["member_name"] = name_map[slot["member_id"]]
            else:
                slot["member_name"] = (slot.get("member_name") or "").strip()
                if len(slot["member_name"]) > 32:
                    raise LineupServiceError("补人姓名过长")
            slot["remark"] = (slot.get("remark") or "").strip()

    lineup.data = data
    lineup.title_remark = (title_remark or "").strip()
    lineup.groups_remark = groups_remark or {}
    await session.commit()
    await session.refresh(lineup)
    return lineup


async def candidate_pool(session: AsyncSession, guild_id: int, schedule_id: int) -> list[dict]:
    """候选池：出勤库中状态为正常的成员（含正式/替补/补人），最多 60 人。"""
    await get_schedule(session, guild_id, schedule_id)
    rows = (
        await session.execute(
            select(
                AttendanceRecord.member_id,
                AttendanceRecord.member_name,
                AttendanceRecord.profession,
                Member.status,
            )
            .outerjoin(Member, Member.id == AttendanceRecord.member_id)
            .where(AttendanceRecord.schedule_id == schedule_id, AttendanceRecord.status == "normal")
            .order_by(AttendanceRecord.is_filler, AttendanceRecord.member_name)
        )
    ).all()
    return [
        {
            "member_id": mid,
            "member_name": name,
            "profession": profession,
            "member_status": "filler" if member_status is None else member_status,
        }
        for mid, name, profession, member_status in rows
    ]


async def list_lineup_history(
    session: AsyncSession, guild_id: int, schedule_id: int
) -> list[dict]:
    """列出本帮会其他有排表数据的赛程（供一键导入，按比赛时间倒序）。"""
    await get_schedule(session, guild_id, schedule_id)
    rows = (
        await session.execute(
            select(Schedule, Lineup)
            .join(Lineup, Lineup.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, Schedule.id != schedule_id)
            .order_by(Schedule.match_time.desc())
        )
    ).all()
    return [
        {
            "schedule_id": schedule.id,
            "opponent": schedule.opponent,
            "match_time": schedule.match_time,
            "teams": lineup.data,
        }
        for schedule, lineup in rows
        if lineup.data
    ]


async def import_lineup(
    session: AsyncSession,
    guild_id: int,
    schedule_id: int,
    source_schedule_id: int,
    team_keys: list[str],
) -> tuple[Lineup, int]:
    """从历史排表导入选中小队：仅保留当前候选池（出勤正常）出现的成员，其余槽位留空。"""
    current = await get_lineup(session, guild_id, schedule_id)
    if source_schedule_id == schedule_id:
        raise LineupServiceError("不能从当前赛程导入")
    await get_schedule(session, guild_id, source_schedule_id)  # 校验来源赛程归属本帮会
    source = (
        await session.execute(select(Lineup).where(Lineup.schedule_id == source_schedule_id))
    ).scalar_one_or_none()
    if source is None or not source.data:
        raise LineupServiceError("来源赛程没有排表数据", 404)

    # 候选池成员集合：正式按 member_id、补人按姓名
    candidates = await candidate_pool(session, guild_id, schedule_id)
    pool_mids = {c["member_id"] for c in candidates if c["member_id"] is not None}
    pool_names = {c["member_name"] for c in candidates if c["member_id"] is None}

    keys = set(team_keys)
    source_map = {(t["category"], t["team_index"]): t for t in source.data}
    new_data = []
    imported = 0
    for team in current.data:
        key = (team["category"], team["team_index"])
        if f"{team['category']}:{team['team_index']}" not in keys:
            new_data.append(team)
            continue
        src_team = source_map.get(key)
        slots = []
        for slot in team["slots"]:
            if src_team is None:
                slots.append({**slot, "member_id": None, "member_name": ""})
                continue
            src = src_team["slots"][slot["slot_index"]] if slot["slot_index"] < len(src_team["slots"]) else {}
            mid = src.get("member_id")
            name = (src.get("member_name") or "").strip()
            if mid is not None and mid in pool_mids:
                slots.append(
                    {**slot, "member_id": mid, "member_name": name, "remark": src.get("remark") or ""}
                )
                imported += 1
            elif mid is None and name and name in pool_names:
                slots.append(
                    {**slot, "member_id": None, "member_name": name, "remark": src.get("remark") or ""}
                )
                imported += 1
            else:
                slots.append({**slot, "member_id": None, "member_name": ""})
        new_data.append({**team, "slots": slots})

    current.data = new_data
    await session.commit()
    await session.refresh(current)
    return current, imported

"""排表业务：候选池（出勤库正常成员）、排表读写与保存校验。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.schedule import Schedule
from app.services.lineup_attendance import LineupServiceError, candidate_pool, get_profession_map
from app.services.schedule_service import get_schedule
from app.utils.constants import LINEUP_LAYOUT, SLOTS_PER_TEAM
from app.utils.member_names import normalize_member_name


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
    """获取排表。

    无数据时返回内存中的标准空结构（GET 不写库，避免读请求占用写锁与并发唯一约束竞态），
    首次保存（save_lineup / import_lineup）时才真正插入。
    """
    await get_schedule(session, guild_id, schedule_id)
    # 清理或保存排表前先拒绝歧义姓名，避免误清同名补人的槽位。
    await get_profession_map(session, schedule_id)
    lineup = (
        await session.execute(select(Lineup).where(Lineup.schedule_id == schedule_id))
    ).scalar_one_or_none()
    if lineup is None:
        return Lineup(schedule_id=schedule_id, data=empty_lineup_data(), title_remark="", groups_remark={})
    if not lineup.data:
        lineup.data = empty_lineup_data()
        await session.commit()
        await session.refresh(lineup)
    # 请假成员自动移出排表（出勤库状态变动后同步）
    await _purge_leave_members(session, lineup, schedule_id)
    # 出勤库中已不存在的成员自动移出排表
    await _purge_deleted_members(session, lineup, schedule_id)
    return lineup


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
                slot["member_name"] = normalize_member_name(slot.get("member_name"))
                if len(slot["member_name"]) > 32:
                    raise LineupServiceError("补人姓名过长")
            slot["remark"] = (slot.get("remark") or "").strip()

    lineup.data = data
    lineup.title_remark = (title_remark or "").strip()
    lineup.groups_remark = groups_remark or {}
    # 无记录时 get_lineup 返回内存对象：首次保存时插入（已持久化对象 add 为幂等操作）
    session.add(lineup)
    await session.commit()
    await session.refresh(lineup)
    return lineup


async def list_lineup_history(
    session: AsyncSession, guild_id: int, schedule_id: int
) -> list[dict]:
    """列出本帮会其他有排表数据的赛程（供一键导入，按比赛时间倒序，最多 50 条）。

    每条含完整 60 槽位 JSON，限制条数避免赛程积累后响应体积失控。
    """
    await get_schedule(session, guild_id, schedule_id)
    rows = (
        await session.execute(
            select(Schedule, Lineup)
            .join(Lineup, Lineup.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, Schedule.id != schedule_id)
            .order_by(Schedule.match_time.desc())
            .limit(50)
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
    # member_id → 出勤库最新姓名：成员改名后用新名替换历史排表里的旧名快照
    mid_name = {c["member_id"]: c["member_name"] for c in candidates if c["member_id"] is not None}

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
            name = normalize_member_name(src.get("member_name"))
            if mid is not None and mid in pool_mids:
                slots.append(
                    {**slot, "member_id": mid, "member_name": mid_name.get(mid, name), "remark": src.get("remark") or ""}
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
    # 无记录时 get_lineup 返回内存对象：首次保存时插入（已持久化对象 add 为幂等操作）
    session.add(current)
    await session.commit()
    await session.refresh(current)
    return current, imported

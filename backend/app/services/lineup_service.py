"""排表业务：候选池（出勤库正常成员）、排表读写与保存校验。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.attendance import AttendanceRecord
from app.models.lineup import Lineup
from app.models.member import Member
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
    return lineup


async def save_lineup(
    session: AsyncSession, guild_id: int, schedule_id: int, data: list[dict]
) -> Lineup:
    """保存排表：校验结构、成员归属本帮会、按数据库规范化姓名。"""
    lineup = await get_lineup(session, guild_id, schedule_id)
    _validate_structure(data)

    member_ids = {s["member_id"] for team in data for s in team["slots"] if s.get("member_id")}
    name_map: dict[int, str] = {}
    if member_ids:
        rows = (
            await session.execute(
                select(Member.id, Member.name).where(
                    Member.id.in_(member_ids), Member.guild_id == guild_id
                )
            )
        ).all()
        name_map = {mid: name for mid, name in rows}
        missing = member_ids - set(name_map)
        if missing:
            raise LineupServiceError("排表包含非本帮会成员或已删除成员", 400)

    for team in data:
        for slot in team["slots"]:
            if slot.get("member_id") is not None:
                slot["member_name"] = name_map[slot["member_id"]]
            else:
                slot["member_name"] = (slot.get("member_name") or "").strip()
                if len(slot["member_name"]) > 32:
                    raise LineupServiceError("补人姓名过长")
            slot["remark"] = (slot.get("remark") or "").strip()

    lineup.data = data
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

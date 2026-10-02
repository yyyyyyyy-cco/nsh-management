"""比赛数据分析业务：CSV 导入、数据列表、排行榜、小队分析。

- CSV 解析与文件限制：match_data_csv
- 衍生指标与阵营汇总计算：match_data_stats
- 职业深度 / 指标列表 / 阵营对比聚合：match_data_aggregate
"""
import asyncio
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_data import MatchData
from app.services.lineup_service import get_lineup
from app.services.match_data_csv import MatchDataError, parse_csv
from app.services.match_data_stats import calculate_indicators, get_camp_totals
from app.services.schedule_service import get_schedule


async def import_csv(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int, content: str
) -> dict:
    """导入 CSV 比赛数据，覆盖该局已有数据（一局一表）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)

    # 校验局号范围（1 ~ schedule.rounds）
    if round_no < 1 or round_no > schedule.rounds:
        raise MatchDataError(f"局号无效：该赛程共 {schedule.rounds} 局，局号应为 1~{schedule.rounds}")

    # 解析 CSV（纯计算放线程池，避免大文件解析阻塞事件循环）
    data_list = await asyncio.to_thread(parse_csv, content)

    # 覆盖语义：先删除该局已有数据，保证一局只有一张表
    await session.execute(
        delete(MatchData).where(
            MatchData.schedule_id == schedule_id, MatchData.round_no == round_no
        )
    )

    # 创建比赛数据记录
    records = []
    for data in data_list:
        record = MatchData(
            schedule_id=schedule_id,
            round_no=round_no,
            player_name=data["player_name"],
            profession=data.get("profession"),
            camp=data["camp"],
            kills=data.get("kills", 0),
            springs=data.get("springs", 0),
            assists=data.get("assists", 0),
            resource=data.get("resource", 0),
            player_damage=data.get("player_damage", 0),
            armor_break_damage=data.get("armor_break_damage", 0),
            building_damage=data.get("building_damage", 0),
            tower_break_damage=data.get("tower_break_damage", 0),
            healing=data.get("healing", 0),
            damage_taken=data.get("damage_taken", 0),
            deaths=data.get("deaths", 0),
            revives=data.get("revives", 0),
            fen_gu=data.get("fen_gu", 0),
        )
        session.add(record)
        records.append(record)

    await session.commit()

    return {
        "message": f"成功导入 {len(records)} 条比赛数据",
        "count": len(records),
    }


async def _query_records(
    session: AsyncSession, schedule_id: int, round_no: int | None = None
) -> list[MatchData]:
    """按赛程（可选局）查询比赛数据。"""
    stmt = select(MatchData).where(MatchData.schedule_id == schedule_id)
    if round_no is not None:
        stmt = stmt.where(MatchData.round_no == round_no)
    stmt = stmt.order_by(MatchData.camp, MatchData.player_name)
    return list((await session.execute(stmt)).scalars().all())


def _record_base(r: MatchData) -> dict:
    """记录基础字段（不含 resource，遵循“资源忽略不显示”约束）。"""
    return {
        "id": r.id, "schedule_id": r.schedule_id, "round_no": r.round_no,
        "player_name": r.player_name, "profession": r.profession, "camp": r.camp,
        "kills": r.kills, "springs": r.springs, "assists": r.assists,
        "player_damage": r.player_damage, "armor_break_damage": r.armor_break_damage,
        "building_damage": r.building_damage, "tower_break_damage": r.tower_break_damage,
        "healing": r.healing, "damage_taken": r.damage_taken, "deaths": r.deaths,
        "revives": r.revives, "fen_gu": r.fen_gu,
    }


async def list_match_data(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None
) -> tuple[list[MatchData], list[dict], int, list[int], int]:
    """获取比赛数据列表、阵营统计、导入次数、已导入局号、总局数。"""
    schedule = await get_schedule(session, guild_id, schedule_id)

    # 查询比赛数据（可按局过滤）
    stmt = select(MatchData).where(MatchData.schedule_id == schedule_id)
    if round_no is not None:
        stmt = stmt.where(MatchData.round_no == round_no)
    stmt = stmt.order_by(MatchData.camp, MatchData.player_name)

    records = list((await session.execute(stmt)).scalars().all())

    # 计算阵营统计
    camps: dict[str, dict[str, Any]] = {}
    for r in records:
        if r.camp not in camps:
            camps[r.camp] = {
                "camp": r.camp,
                "player_count": 0,
                "total_kills": 0,
                "total_damage": 0,
                "total_healing": 0,
                "total_damage_taken": 0,
            }
        camp = camps[r.camp]
        camp["player_count"] += 1
        camp["total_kills"] += r.kills
        camp["total_damage"] += r.player_damage
        camp["total_healing"] += r.healing
        camp["total_damage_taken"] += r.damage_taken

    # 计算导入次数（按 created_at 去重）
    import_count = (
        await session.execute(
            select(func.count(func.distinct(func.date(MatchData.created_at))))
            .where(MatchData.schedule_id == schedule_id)
        )
    ).scalar_one()

    # 该赛程已导入的局号列表（用于前端标记切换项状态）
    imported_rounds = sorted(
        (
            await session.execute(
                select(MatchData.round_no)
                .where(MatchData.schedule_id == schedule_id)
                .distinct()
            )
        )
        .scalars()
        .all()
    )

    return records, list(camps.values()), import_count, imported_rounds, schedule.rounds


async def get_rankings(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None, camp: str | None = None, limit: int = 20
) -> dict:
    """获取排行榜数据（可按局过滤）。

    排序与截断下推 SQL（每维度只取前 limit 行），避免全量加载后内存排序 6 次。
    """
    await get_schedule(session, guild_id, schedule_id)

    async def _ranking(field: str) -> list[dict]:
        column = getattr(MatchData, field)
        stmt = select(
            MatchData.player_name, MatchData.profession, MatchData.camp, column
        ).where(MatchData.schedule_id == schedule_id)
        if round_no is not None:
            stmt = stmt.where(MatchData.round_no == round_no)
        if camp:
            stmt = stmt.where(MatchData.camp == camp)
        stmt = stmt.order_by(column.desc()).limit(limit)
        rows = (await session.execute(stmt)).all()
        return [
            {"player_name": name, "profession": profession, "camp": row_camp, "value": value}
            for name, profession, row_camp, value in rows
        ]

    return {
        "kills_ranking": await _ranking("kills"),
        "damage_ranking": await _ranking("player_damage"),
        "building_ranking": await _ranking("building_damage"),
        "healing_ranking": await _ranking("healing"),
        "taken_ranking": await _ranking("damage_taken"),
        "fen_gu_ranking": await _ranking("fen_gu"),
    }


async def get_squad_analysis(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None
) -> dict:
    """小队维度分析：仅分析我方阵营，按 player_name 关联排表（10 队 × 6 人），未匹配归入“未排表”。

    敌方阵营玩家不参与小队分析（排表只含我方成员，无法还原敌方队伍结构）。
    """
    await get_schedule(session, guild_id, schedule_id)
    records = await _query_records(session, schedule_id, round_no)
    lineup = await get_lineup(session, guild_id, schedule_id)

    # 玩家名 → 所属小队（category, team_index）
    name_to_squad: dict[str, tuple[str, int]] = {}
    for team in lineup.data:
        cat = team.get("category", "")
        idx = team.get("team_index", 0)
        for slot in team.get("slots", []):
            name = (slot.get("member_name") or "").strip()
            if name:
                name_to_squad.setdefault(name, (cat, idx))

    # 我方阵营判定：排表只含我方成员，取命中排表人数最多的阵营作为我方
    camp_hits: dict[str, int] = {}
    for r in records:
        if (r.player_name or "").strip() in name_to_squad:
            camp_hits[r.camp] = camp_hits.get(r.camp, 0) + 1
    our_camp = max(camp_hits, key=lambda c: camp_hits[c]) if camp_hits else (records[0].camp if records else None)
    if our_camp is not None:
        records = [r for r in records if r.camp == our_camp]

    camp_totals = get_camp_totals(records)
    groups: dict[tuple[str, int] | None, list[MatchData]] = {}
    for r in records:
        key = name_to_squad.get((r.player_name or "").strip())
        groups.setdefault(key, []).append(r)

    squad_keys = [(t.get("category", ""), t.get("team_index", 0)) for t in lineup.data] + [None]
    squads = []
    for key in squad_keys:
        recs = groups.get(key)
        if not recs:
            continue
        if key is None:
            category, team_index, squad_name = "-", -1, "未排表"
        else:
            category, team_index = key
            squad_name = f"{category} 第{team_index + 1}队"

        totals = {k: 0 for k in ("kills", "assists", "player_damage", "building_damage", "healing", "damage_taken", "deaths", "revives", "fen_gu")}
        members = []
        for r in recs:
            ind = calculate_indicators(r, camp_totals[r.camp])
            for k in totals:
                totals[k] += getattr(r, k)
            members.append({**_record_base(r), **ind})

        n = len(recs)
        indicator_keys = [
            "kda", "dps", "kpa_damage", "damage_per_death", "taken_per_death",
            "healing_per_death", "heal_conversion", "revive_rate", "fen_gu_rate",
        ]
        indicators = {k: round(sum(m[k] for m in members) / n, 2) for k in indicator_keys}
        squads.append({
            "squad_name": squad_name, "category": category, "team_index": team_index,
            "members": members, "totals": {"player_count": n, **totals}, "indicators": indicators,
        })
    return {"squads": squads}

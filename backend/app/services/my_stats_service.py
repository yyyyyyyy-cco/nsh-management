"""个人战绩查询业务：按游戏 ID 聚合历史比赛数据。"""
from collections import Counter

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_data import MatchData
from app.models.schedule import Schedule
from app.services.match_data_service import calculate_indicators, get_camp_totals

# 排行榜维度：字段名 → 显示标签
RANKING_FIELDS = {
    "kills": "击杀",
    "player_damage": "对玩家伤害",
    "building_damage": "对建筑伤害",
    "healing": "治疗",
    "damage_taken": "承伤",
    "deaths": "重伤",
}


async def query_player_stats(session: AsyncSession, guild_id: int, player_name: str) -> dict:
    """按游戏 ID 聚合该帮会下最近 10 场已导入比赛数据。

    返回：
    - records: 每局明细（含衍生指标 + 赛程元信息 + 该局排名）
    - summary: 概览统计
    """
    # 联查 match_data + schedules，按 guild_id 隔离
    stmt = (
        select(MatchData, Schedule)
        .join(Schedule, MatchData.schedule_id == Schedule.id)
        .where(Schedule.guild_id == guild_id, MatchData.player_name == player_name)
        .order_by(Schedule.match_time.desc(), MatchData.round_no.asc())
    )
    rows = (await session.execute(stmt)).all()
    if not rows:
        return {
            "records": [],
            "summary": _empty_summary(player_name),
        }

    # 限制最近 10 场比赛（按赛程去重）
    all_schedule_ids = list(dict.fromkeys(r.MatchData.schedule_id for r in rows))
    recent_schedule_ids = set(all_schedule_ids[:10])
    rows = [r for r in rows if r.MatchData.schedule_id in recent_schedule_ids]
    schedule_ids = list(recent_schedule_ids)

    # 按 schedule_id 加载全量记录，用于计算阵营汇总 + 排名
    round_records_map: dict[tuple[int, int], list[MatchData]] = {}  # (schedule_id, round_no) -> records
    round_camp_totals_map: dict[tuple[int, int, str], dict] = {}  # (schedule_id, round_no, camp) -> totals

    for sid in schedule_ids:
        all_records = list(
            (await session.execute(
                select(MatchData).where(MatchData.schedule_id == sid)
            )).scalars().all()
        )
        # 按局分组，每局独立计算阵营汇总（占比分母为同局同阵营）
        by_round: dict[int, list[MatchData]] = {}
        for r in all_records:
            by_round.setdefault(r.round_no, []).append(r)
            round_records_map.setdefault((sid, r.round_no), []).append(r)
        for rn, recs in by_round.items():
            totals = get_camp_totals(recs)
            for camp_name, ct in totals.items():
                round_camp_totals_map[(sid, rn, camp_name)] = ct

    # 逐局计算衍生指标 + 排名
    records = []
    for row in rows:
        md = row.MatchData
        sc = row.Schedule
        ct = round_camp_totals_map.get((md.schedule_id, md.round_no, md.camp), _zero_camp_totals(md.camp))
        indicators = calculate_indicators(md, ct)

        # 计算该局真实排名（全部 + 己方阵营）
        round_recs = round_records_map.get((md.schedule_id, md.round_no), [])
        total_players = len(round_recs)
        rankings_all = _calc_rankings(md, round_recs, total_players)

        camp_recs = [r for r in round_recs if r.camp == md.camp]
        camp_total = len(camp_recs)
        rankings_camp = _calc_rankings(md, camp_recs, camp_total)

        records.append({
            "schedule_id": md.schedule_id,
            "opponent": sc.opponent,
            "match_time": sc.match_time.isoformat(),
            "schedule_result": sc.result,
            "round_no": md.round_no,
            "player_name": md.player_name,
            "profession": md.profession,
            "camp": md.camp,
            "kills": md.kills,
            "springs": md.springs,
            "assists": md.assists,
            "player_damage": md.player_damage,
            "armor_break_damage": md.armor_break_damage,
            "building_damage": md.building_damage,
            "tower_break_damage": md.tower_break_damage,
            "healing": md.healing,
            "damage_taken": md.damage_taken,
            "deaths": md.deaths,
            "revives": md.revives,
            "fen_gu": md.fen_gu,
            **indicators,
            "rankings": rankings_all,
            "rankings_camp": rankings_camp,
        })

    # 概览统计
    total_rounds = len(records)
    total_matches = len(schedule_ids)
    professions = [r["profession"] for r in records if r["profession"]]
    main_profession = Counter(professions).most_common(1)[0][0] if professions else None
    total_kills = sum(r["kills"] for r in records)
    total_damage = sum(r["player_damage"] + r["building_damage"] for r in records)
    total_healing = sum(r["healing"] for r in records)
    total_deaths = sum(r["deaths"] for r in records)
    avg_kda = round(sum(r["kda"] for r in records) / total_rounds, 2)
    avg_kills = round(total_kills / total_rounds, 1)
    avg_damage = round(total_damage / total_rounds)
    avg_healing = round(total_healing / total_rounds)
    avg_deaths = round(total_deaths / total_rounds, 1)

    return {
        "records": records,
        "summary": {
            "player_name": player_name,
            "total_rounds": total_rounds,
            "total_matches": total_matches,
            "main_profession": main_profession,
            "avg_kda": avg_kda,
            "avg_kills": avg_kills,
            "avg_damage": avg_damage,
            "avg_healing": avg_healing,
            "avg_deaths": avg_deaths,
            "total_kills": total_kills,
            "total_damage": total_damage,
            "total_healing": total_healing,
        },
    }


def _calc_rankings(target: MatchData, all_recs: list[MatchData], total: int) -> list[dict]:
    """计算目标玩家在该局各维度的真实排名（降序，排名从 1 开始）。"""
    result = []
    for field, label in RANKING_FIELDS.items():
        val = getattr(target, field, 0) or 0
        # 统计排名：有多少人比 target 高
        rank = 1 + sum(1 for r in all_recs if (getattr(r, field, 0) or 0) > val)
        result.append({"label": label, "rank": rank, "total": total})
    return result


def _empty_summary(player_name: str) -> dict:
    """无数据时的空概览。"""
    return {
        "player_name": player_name,
        "total_rounds": 0,
        "total_matches": 0,
        "main_profession": None,
        "avg_kda": 0,
        "avg_kills": 0,
        "avg_damage": 0,
        "avg_healing": 0,
        "avg_deaths": 0,
        "total_kills": 0,
        "total_damage": 0,
        "total_healing": 0,
    }


def _zero_camp_totals(camp: str) -> dict:
    """阵营汇总兜底。"""
    return {
        "camp": camp, "player_count": 0, "kills": 0, "assists": 0,
        "player_damage": 0, "building_damage": 0, "healing": 0,
        "damage_taken": 0, "deaths": 0, "springs": 0, "revives": 0, "fen_gu": 0,
    }

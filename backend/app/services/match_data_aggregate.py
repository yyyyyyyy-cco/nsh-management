"""比赛数据聚合查询：职业深度统计、衍生指标列表、阵营对比。

由 match_data_service 拆出；复用其查询助手与 match_data_stats 的纯计算。
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_data import MatchData
from app.services.match_data_service import _query_records, _record_base
from app.services.match_data_stats import calculate_indicators, get_camp_totals
from app.services.schedule_service import get_schedule


async def get_profession_stats(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None, camp: str | None = None
) -> list[dict]:
    """获取职业深度统计：17 项指标（人数 + 16 项衍生指标均值），含分阵营对比（可按局/阵营过滤）。"""
    await get_schedule(session, guild_id, schedule_id)

    stmt = select(MatchData).where(MatchData.schedule_id == schedule_id)
    if round_no is not None:
        stmt = stmt.where(MatchData.round_no == round_no)
    if camp:
        stmt = stmt.where(MatchData.camp == camp)

    records = list((await session.execute(stmt)).scalars().all())
    if not records:
        return []

    # 占比分母为整个阵营：基于本查询范围内的全部记录计算阵营汇总
    camp_totals = get_camp_totals(records)

    # 按职业分组
    grouped: dict[str, list[MatchData]] = {}
    for r in records:
        prof = r.profession or "未知"
        grouped.setdefault(prof, []).append(r)

    result = []
    for prof, recs in grouped.items():
        count = len(recs)
        indicators = [calculate_indicators(r, camp_totals[r.camp]) for r in recs]

        # 17 项指标中的 16 项：衍生指标均值（avg_ 前缀）
        avg = {f"avg_{key}": round(sum(ind[key] for ind in indicators) / count, 4) for key in indicators[0]}

        # 兼容旧消费方的基础均值
        avg["avg_kills"] = round(sum(r.kills for r in recs) / count, 1)
        avg["avg_damage"] = round(sum(r.player_damage for r in recs) / count, 0)
        avg["avg_healing"] = round(sum(r.healing for r in recs) / count, 0)

        # 分阵营均值（供 我方/敌方 对比图表）
        camps = []
        by_camp: dict[str, list[MatchData]] = {}
        for r in recs:
            by_camp.setdefault(r.camp, []).append(r)
        for camp_name, camp_recs in by_camp.items():
            n = len(camp_recs)
            camp_inds = [calculate_indicators(r, camp_totals[r.camp]) for r in camp_recs]
            camps.append({
                "camp": camp_name,
                "count": n,
                "avg_kills": round(sum(r.kills for r in camp_recs) / n, 2),
                "avg_player_damage": round(sum(r.player_damage for r in camp_recs) / n, 0),
                "avg_building_damage": round(sum(r.building_damage for r in camp_recs) / n, 0),
                "avg_healing": round(sum(r.healing for r in camp_recs) / n, 0),
                "avg_damage_taken": round(sum(r.damage_taken for r in camp_recs) / n, 0),
                "avg_kda": round(sum(ind["kda"] for ind in camp_inds) / n, 2),
            })

        # 职业差值/波动值（基于分阵营均值，按记录出现顺序取前两个阵营）
        comparison = []
        if len(camps) >= 2:
            a, b = camps[0], camps[1]
            for metric in ("avg_kills", "avg_player_damage", "avg_building_damage", "avg_healing", "avg_damage_taken", "avg_kda"):
                v1, v2 = a[metric], b[metric]
                diff = round(v1 - v2, 4)
                base = min(v1, v2)
                wave = round(abs(diff) / base * 100, 2) if base > 0 else 0.0
                comparison.append({
                    "metric": metric, "camp1": a["camp"], "camp2": b["camp"],
                    "value1": v1, "value2": v2, "diff": diff, "wave": wave,
                })

        result.append({"profession": prof, "count": count, **avg, "camps": camps, "comparison": comparison})

    return sorted(result, key=lambda x: x["count"], reverse=True)


async def get_indicators(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None
) -> dict:
    """获取带 16 项衍生指标的数据列表（可按局过滤）。"""
    await get_schedule(session, guild_id, schedule_id)
    records = await _query_records(session, schedule_id, round_no)
    camp_totals = get_camp_totals(records)
    items = []
    for r in records:
        item = _record_base(r)
        item.update(calculate_indicators(r, camp_totals[r.camp]))
        items.append(item)
    return {"items": items, "camps": list(camp_totals.values())}


async def get_camp_comparison(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None
) -> dict:
    """获取阵营对比：各阵营汇总 + 每项指标的我方/敌方差值/波动值。"""
    await get_schedule(session, guild_id, schedule_id)
    records = await _query_records(session, schedule_id, round_no)
    camp_totals = get_camp_totals(records)

    metrics = [
        ("player_count", "人数"), ("kills", "总击杀"), ("assists", "总助攻"),
        ("player_damage", "玩家伤害"), ("building_damage", "建筑伤害"),
        ("healing", "治疗"), ("damage_taken", "承伤"), ("deaths", "死亡"),
        ("springs", "破泉"), ("revives", "化羽"), ("fen_gu", "焚骨"),
    ]
    names = list(camp_totals.keys())
    comparison = {}
    for key, label in metrics:
        row = {name: camp_totals[name][key] for name in names}
        if len(names) >= 2:
            a, b = names[0], names[1]
            diff = row[a] - row[b]
            base = min(row[a], row[b])
            row["差值"] = diff
            row["波动值"] = round(abs(diff) / base * 100, 2) if base > 0 else 0.0
        else:
            row["差值"] = 0
            row["波动值"] = 0.0
        comparison[label] = row
    return {"camps": camp_totals, "comparison": comparison}

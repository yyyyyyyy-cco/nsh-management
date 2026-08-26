"""比赛数据分析业务：CSV 导入、排行榜、职业统计、衍生指标、阵营对比、小队分析。"""
import csv
import io
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_data import MatchData
from app.services.lineup_service import get_lineup
from app.services.schedule_service import get_schedule

# CSV 表头映射（中文列名 → 字段名）
CSV_COLUMN_MAP = {
    "玩家名字": "player_name",
    "职业": "profession",
    "击败/清泉": "kills_springs",
    "助攻": "assists",
    "资源": "resource",
    "对玩家伤害": "player_damage",
    "人伤卸甲": "armor_break_damage",
    "对建筑伤害": "building_damage",
    "破塔卸甲": "tower_break_damage",
    "治疗值": "healing",
    "承受伤害": "damage_taken",
    "重伤": "deaths",
    "复活/清泉": "revives",
    "焚骨": "fen_gu",
}

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# 比赛时长固定 23 分钟（秒），用于秒伤/技能使用率等指标
MATCH_DURATION_SECONDS = 23 * 60


class MatchDataError(Exception):
    """比赛数据业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def parse_csv(content: str) -> list[dict]:
    """解析 CSV 文件内容，返回比赛数据列表。

    CSV 格式：
    - 多个阵营区块，每块结构：阵营名,人数 → 表头行 → N 条数据行
    - 第一个区块为己方阵营
    """
    reader = csv.reader(io.StringIO(content))
    rows = list(reader)

    if len(rows) < 3:
        raise MatchDataError("CSV 文件格式错误：内容不完整")

    result = []
    current_camp = None
    header = None
    i = 0

    while i < len(rows):
        row = rows[i]

        # 跳过空行
        if not row or all(not cell.strip() for cell in row):
            i += 1
            continue

        # 检测阵营标题行（第一列是阵营名，第二列是人数）
        if len(row) >= 2 and row[1].strip().isdigit():
            current_camp = row[0].strip()
            header = None
            i += 1
            continue

        # 检测表头行
        if len(row) >= 10 and row[0].strip() in ["玩家名字", "玩家名"]:
            header = [cell.strip() for cell in row]
            i += 1
            continue

        # 数据行
        if header and current_camp and len(row) >= len(header):
            data = {"camp": current_camp}
            for j, col_name in enumerate(header):
                field_name = CSV_COLUMN_MAP.get(col_name)
                if not field_name or j >= len(row):
                    continue

                value = row[j].strip()

                if field_name == "player_name":
                    data["player_name"] = value
                elif field_name == "profession":
                    data["profession"] = value
                elif field_name == "kills_springs":
                    # 解析 "击败/清泉" 格式，如 " 15/3"
                    parts = value.split("/")
                    if len(parts) == 2:
                        try:
                            raw_kills = int(parts[0].strip())
                            springs = int(parts[1].strip())
                            data["kills"] = raw_kills + springs  # 击败数 = 击败 + 清泉
                            data["springs"] = springs
                        except ValueError:
                            data["kills"] = 0
                            data["springs"] = 0
                    else:
                        try:
                            data["kills"] = int(value) if value else 0
                        except ValueError:
                            data["kills"] = 0
                        data["springs"] = 0
                elif field_name == "revives":
                    # "复活/清泉" 为单值
                    try:
                        data["revives"] = int(value) if value else 0
                    except ValueError:
                        data["revives"] = 0
                else:
                    try:
                        data[field_name] = int(value) if value else 0
                    except ValueError:
                        data[field_name] = 0

            if data.get("player_name"):
                result.append(data)

        i += 1

    if not result:
        raise MatchDataError("CSV 文件中没有解析到有效的比赛数据")

    return result


async def import_csv(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int, content: str
) -> dict:
    """导入 CSV 比赛数据，覆盖该局已有数据（一局一表）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)

    # 校验局号范围（1 ~ schedule.rounds）
    if round_no < 1 or round_no > schedule.rounds:
        raise MatchDataError(f"局号无效：该赛程共 {schedule.rounds} 局，局号应为 1~{schedule.rounds}")

    # 解析 CSV
    data_list = parse_csv(content)

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


def calculate_indicators(record, camp_totals: dict) -> dict:
    """计算单条记录的 16 项衍生指标。

    效率指标：KDA / 秒伤 / 参与击杀均伤
    生存指标：每死输出值 / 每死承伤 / 死亡治疗量 / 治疗转化率
    占比指标（分母=整个阵营）：击杀 / 助攻 / 人伤 / 拆塔 / 承伤 / 死亡 / 治疗占比
    技能指标：清泉/羽化使用率（revives）/ 焚骨使用率
    """
    kills = record.kills or 0
    assists = record.assists or 0
    deaths = record.deaths or 0
    player_damage = record.player_damage or 0
    building_damage = record.building_damage or 0  # 拆塔 = 对建筑伤害
    damage_taken = record.damage_taken or 0
    healing = record.healing or 0
    revives = record.revives or 0
    fen_gu = record.fen_gu or 0

    total_damage = player_damage + building_damage
    death_denom = max(deaths, 1)

    kda = round((kills + assists) / death_denom, 2)
    dps = round(total_damage / MATCH_DURATION_SECONDS)
    kpa_damage = round(total_damage / max(kills + assists, 1))
    damage_per_death = round(total_damage / death_denom)
    taken_per_death = round(damage_taken / death_denom)
    healing_per_death = round(healing / death_denom)
    heal_conversion = round(healing_per_death / max(taken_per_death, 1), 2)

    def ratio(part: int, total: int) -> float:
        return round(part / total, 4) if total else 0.0

    return {
        "kda": kda,
        "dps": dps,
        "kpa_damage": kpa_damage,
        "damage_per_death": damage_per_death,
        "taken_per_death": taken_per_death,
        "healing_per_death": healing_per_death,
        "heal_conversion": heal_conversion,
        "kill_ratio": ratio(kills, camp_totals["kills"]),
        "assist_ratio": ratio(assists, camp_totals["assists"]),
        "player_damage_ratio": ratio(player_damage, camp_totals["player_damage"]),
        "building_ratio": ratio(building_damage, camp_totals["building_damage"]),
        "taken_ratio": ratio(damage_taken, camp_totals["damage_taken"]),
        "death_ratio": ratio(deaths, camp_totals["deaths"]),
        "heal_ratio": ratio(healing, camp_totals["healing"]),
        "revive_rate": round(revives / MATCH_DURATION_SECONDS, 4),
        "fen_gu_rate": round(fen_gu / MATCH_DURATION_SECONDS, 4),
    }


def get_camp_totals(records: list) -> dict[str, dict]:
    """按阵营汇总数据（占比指标的分母为整个阵营）。"""
    totals: dict[str, dict] = {}
    for r in records:
        camp = r.camp
        t = totals.setdefault(camp, {
            "camp": camp, "player_count": 0, "kills": 0, "assists": 0,
            "player_damage": 0, "building_damage": 0, "healing": 0,
            "damage_taken": 0, "deaths": 0, "springs": 0, "revives": 0, "fen_gu": 0,
        })
        t["player_count"] += 1
        t["kills"] += r.kills
        t["assists"] += r.assists
        t["player_damage"] += r.player_damage
        t["building_damage"] += r.building_damage
        t["healing"] += r.healing
        t["damage_taken"] += r.damage_taken
        t["deaths"] += r.deaths
        t["springs"] += r.springs
        t["revives"] += r.revives
        t["fen_gu"] += r.fen_gu
    return totals


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
    camps = {}
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
    """获取排行榜数据（可按局过滤）。"""
    await get_schedule(session, guild_id, schedule_id)

    stmt = select(MatchData).where(MatchData.schedule_id == schedule_id)
    if round_no is not None:
        stmt = stmt.where(MatchData.round_no == round_no)
    if camp:
        stmt = stmt.where(MatchData.camp == camp)

    records = list((await session.execute(stmt)).scalars().all())

    # 按不同维度排序
    def get_ranking(field: str) -> list[dict]:
        sorted_records = sorted(records, key=lambda r: getattr(r, field), reverse=True)[:limit]
        return [
            {
                "player_name": r.player_name,
                "profession": r.profession,
                "camp": r.camp,
                "value": getattr(r, field),
            }
            for r in sorted_records
        ]

    return {
        "kills_ranking": get_ranking("kills"),
        "damage_ranking": get_ranking("player_damage"),
        "building_ranking": get_ranking("building_damage"),
        "healing_ranking": get_ranking("healing"),
        "taken_ranking": get_ranking("damage_taken"),
        "fen_gu_ranking": get_ranking("fen_gu"),
    }


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
    our_camp = max(camp_hits, key=camp_hits.get) if camp_hits else (records[0].camp if records else None)
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

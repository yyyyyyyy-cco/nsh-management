"""比赛数据分析业务：CSV 导入、排行榜、职业统计、报告导出。"""
import csv
import io
from datetime import datetime, timezone

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.match_data import MatchData
from app.models.schedule import Schedule
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
    """获取职业统计数据（可按局过滤）。"""
    await get_schedule(session, guild_id, schedule_id)

    stmt = select(MatchData).where(MatchData.schedule_id == schedule_id)
    if round_no is not None:
        stmt = stmt.where(MatchData.round_no == round_no)
    if camp:
        stmt = stmt.where(MatchData.camp == camp)

    records = list((await session.execute(stmt)).scalars().all())

    # 按职业分组统计
    professions = {}
    for r in records:
        prof = r.profession or "未知"
        if prof not in professions:
            professions[prof] = {
                "profession": prof,
                "count": 0,
                "total_kills": 0,
                "total_damage": 0,
                "total_healing": 0,
            }
        p = professions[prof]
        p["count"] += 1
        p["total_kills"] += r.kills
        p["total_damage"] += r.player_damage
        p["total_healing"] += r.healing

    # 计算平均值
    result = []
    for p in professions.values():
        result.append({
            "profession": p["profession"],
            "count": p["count"],
            "avg_kills": round(p["total_kills"] / p["count"], 1) if p["count"] > 0 else 0,
            "avg_damage": round(p["total_damage"] / p["count"], 0) if p["count"] > 0 else 0,
            "avg_healing": round(p["total_healing"] / p["count"], 0) if p["count"] > 0 else 0,
        })

    return sorted(result, key=lambda x: x["count"], reverse=True)


async def generate_html_report(
    session: AsyncSession, guild_id: int, schedule_id: int, round_no: int | None = None
) -> str:
    """生成 HTML 分析报告（可按局生成）。"""
    schedule = await get_schedule(session, guild_id, schedule_id)
    records, camps, _, _, _ = await list_match_data(session, guild_id, schedule_id, round_no)
    rankings = await get_rankings(session, guild_id, schedule_id, round_no, limit=10)
    prof_stats = await get_profession_stats(session, guild_id, schedule_id, round_no)

    round_label = f"第 {round_no} 局" if round_no is not None else "全部局"

    # 生成 HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>比赛数据分析报告（{round_label}） - {schedule.opponent}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 20px; background: #f9fafb; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ color: #1f2937; border-bottom: 2px solid #d4af37; padding-bottom: 10px; }}
        h2 {{ color: #374151; margin-top: 30px; }}
        .info-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; }}
        .stat-card {{ background: #fff8e7; padding: 16px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 24px; font-weight: 700; color: #b8960e; }}
        .stat-label {{ font-size: 12px; color: #6b7280; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        th {{ background: #f9fafb; padding: 12px; text-align: left; font-weight: 600; color: #374151; }}
        td {{ padding: 12px; border-top: 1px solid #f3f4f6; }}
        tr:hover {{ background: #f9fafb; }}
        .camp-section {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>比赛数据分析报告</h1>
        <div class="info-card">
            <p><strong>对手：</strong>{schedule.opponent}</p>
            <p><strong>比赛时间：</strong>{schedule.match_time.strftime('%Y-%m-%d %H:%M') if schedule.match_time else '-'}</p>
            <p><strong>局数：</strong>{schedule.rounds} 局（当前展示：{round_label}）</p>
        </div>

        <h2>阵营统计</h2>
        <div class="stats-grid">
"""

    for camp in camps:
        html += f"""
            <div class="stat-card">
                <div class="stat-label">{camp['camp']}</div>
                <div class="stat-value">{camp['player_count']} 人</div>
                <div class="stat-label">击杀 {camp['total_kills']} | 伤害 {camp['total_damage']:,}</div>
            </div>
"""

    html += """
        </div>

        <h2>排行榜</h2>
"""

    ranking_titles = {
        "kills_ranking": "击杀榜",
        "damage_ranking": "玩家伤害榜",
        "building_ranking": "建筑伤害榜",
        "healing_ranking": "治疗榜",
        "taken_ranking": "承伤榜",
        "fen_gu_ranking": "焚骨榜",
    }

    for key, title in ranking_titles.items():
        html += f"""
        <h3>{title}</h3>
        <table>
            <thead>
                <tr>
                    <th>排名</th>
                    <th>玩家</th>
                    <th>职业</th>
                    <th>阵营</th>
                    <th>数值</th>
                </tr>
            </thead>
            <tbody>
"""
        for i, item in enumerate(rankings[key], 1):
            html += f"""
                <tr>
                    <td>{i}</td>
                    <td>{item['player_name']}</td>
                    <td>{item['profession'] or '-'}</td>
                    <td>{item['camp']}</td>
                    <td>{item['value']:,}</td>
                </tr>
"""
        html += """
            </tbody>
        </table>
"""

    html += """
        <h2>职业统计</h2>
        <table>
            <thead>
                <tr>
                    <th>职业</th>
                    <th>人数</th>
                    <th>平均击杀</th>
                    <th>平均伤害</th>
                    <th>平均治疗</th>
                </tr>
            </thead>
            <tbody>
"""
    for p in prof_stats:
        html += f"""
                <tr>
                    <td>{p['profession']}</td>
                    <td>{p['count']}</td>
                    <td>{p['avg_kills']}</td>
                    <td>{p['avg_damage']:,.0f}</td>
                    <td>{p['avg_healing']:,.0f}</td>
                </tr>
"""
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    return html

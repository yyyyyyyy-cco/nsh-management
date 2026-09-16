"""比赛数据 CSV 解析：列名映射、文件限制、业务异常与解析函数。

由 match_data_service 拆出（纯解析逻辑，无 DB 依赖）。
"""
import csv
import io

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

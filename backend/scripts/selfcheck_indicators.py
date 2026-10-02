"""衍生指标自检脚本（无需 DB / 无需 pytest）。

运行（在 backend 目录下）：
    python scripts/selfcheck_indicators.py
"""
# ---- 前置依赖探测（缺依赖时模块级跳过；见合规化计划 W2-2 与本文件被 pytest 收集的约定）----
import unittest as _unittest

try:  # noqa: SIM105
    import fastapi  # noqa: F401
    import sqlalchemy  # noqa: F401
except ImportError as _exc:  # pragma: no cover - 无依赖环境（如 Python 3.14 装不上 pydantic-core）
    raise _unittest.SkipTest(f"缺少运行依赖（FastAPI/SQLAlchemy），跳过本模块：{_exc}") from _exc

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.schemas.match_data import IndicatorOut, ProfessionStats, SquadOut
from app.services.match_data_stats import (
    MATCH_DURATION_MINUTES,
    calculate_indicators,
    get_camp_totals,
)

# 文档示例玩家：击败/清泉=21（16 击败 + 5 清泉）、助攻 82、重伤 12、
# 人伤 3189843、拆塔 3289538、治疗 0、承伤 4196936、复活 0、焚骨 0
p = SimpleNamespace(
    profession="玄机", kills=21, assists=82, deaths=12, player_damage=3189843, building_damage=3289538,
    damage_taken=4196936, healing=0, revives=0, fen_gu=0,
)
# 阵营汇总（占比分母，文档示例值）
camp_totals = {
    "kills": 402, "assists": 5800, "player_damage": 280_000_000, "building_damage": 45_000_000,
    "damage_taken": 300_000_000, "deaths": 320, "healing": 95_000_000,
}

ind = calculate_indicators(p, camp_totals)
assert ind["kda"] == 8.58, f"kda={ind['kda']}"                       # (21+82)/12
assert ind["dps"] == 4695, f"dps={ind['dps']}"                       # 6479381/1380
assert ind["kpa_damage"] == 62907, f"kpa_damage={ind['kpa_damage']}"  # 6479381/103
assert ind["damage_per_death"] == 539948, f"damage_per_death={ind['damage_per_death']}"
assert ind["taken_per_death"] == 349745, f"taken_per_death={ind['taken_per_death']}"
assert ind["healing_per_death"] == 0, f"healing_per_death={ind['healing_per_death']}"
assert ind["heal_conversion"] == 0, f"heal_conversion={ind['heal_conversion']}"
assert ind["kill_ratio"] == round(21 / 402, 4), f"kill_ratio={ind['kill_ratio']}"
assert ind["assist_ratio"] == round(82 / 5800, 4), f"assist_ratio={ind['assist_ratio']}"
assert ind["revive_rate"] == 0 and ind["fen_gu_rate"] == 0

# 边界：死亡为 0 时用 max(死亡,1)
p0 = SimpleNamespace(
    profession="素问", kills=5, assists=10, deaths=0, player_damage=100, building_damage=50,
    damage_taken=30, healing=20, revives=1, fen_gu=2,
)
ind0 = calculate_indicators(p0, camp_totals)
assert ind0["kda"] == 15.0, f"kda0={ind0['kda']}"
assert ind0["damage_per_death"] == 150, f"damage_per_death0={ind0['damage_per_death']}"
assert ind0["revive_rate"] == round(1 / MATCH_DURATION_MINUTES, 4)
assert ind0["fen_gu_rate"] == round(2 / MATCH_DURATION_MINUTES, 4)

# 辅助型加权：铁衣与治疗职业同样适用（助攻 ×0.8、死亡 ×1.2，仅影响 KDA）
pt = SimpleNamespace(
    profession="铁衣", kills=10, assists=20, deaths=10, player_damage=1000, building_damage=500,
    damage_taken=800, healing=10, revives=0, fen_gu=0,
)
indt = calculate_indicators(pt, camp_totals)
assert indt["kda"] == 2.17, f"kda_tank={indt['kda']}"          # (10+20*0.8)/(10*1.2) = 26/12
assert indt["damage_per_death"] == 150, f"damage_per_death_tank={indt['damage_per_death']}"  # 其他指标用原始死亡数
ph = SimpleNamespace(
    profession="神相", kills=10, assists=20, deaths=10, player_damage=500, building_damage=100,
    damage_taken=800, healing=900, revives=0, fen_gu=0,
)
indh = calculate_indicators(ph, camp_totals)
assert indh["kda"] == 2.17, f"kda_healer={indh['kda']}"        # 治疗量 > 人伤 → 同样加权

# 阵营汇总
rows = [
    SimpleNamespace(camp="横戈", kills=21, assists=82, player_damage=100, building_damage=50,
                    healing=0, damage_taken=30, deaths=12, springs=5, revives=0, fen_gu=0),
    SimpleNamespace(camp="横戈", kills=9, assists=18, player_damage=200, building_damage=10,
                    healing=0, damage_taken=40, deaths=3, springs=2, revives=0, fen_gu=1),
]
totals = get_camp_totals(rows)
assert totals["横戈"]["player_count"] == 2
assert totals["横戈"]["kills"] == 30
assert totals["横戈"]["springs"] == 7
assert totals["横戈"]["fen_gu"] == 1

# Pydantic 响应模型可正常构建（嵌套 / 前向引用无碍）
squad_out = SquadOut(**{
    "squad_name": "进攻1 第1队", "category": "进攻1", "team_index": 0,
    "members": [{
        "player_name": "玩家1", "profession": "玄机", "camp": "横戈",
        "kills": 21, "springs": 5, "assists": 82, "player_damage": 3189843, "building_damage": 3289538,
        "healing": 0, "damage_taken": 4196936, "deaths": 12, "revives": 0, "fen_gu": 0,
        "kill_ratio": 1.0, "assist_ratio": 1.0, "player_damage_ratio": 1.0, "building_ratio": 1.0,
        "taken_ratio": 1.0, "death_ratio": 1.0, "heal_ratio": 1.0,
        "kda": 8.58, "dps": 4695, "kpa_damage": 62907, "damage_per_death": 539948,
        "taken_per_death": 349745, "healing_per_death": 0, "heal_conversion": 0,
        "revive_rate": 0, "fen_gu_rate": 0,
    }],
    "totals": {"player_count": 1, "kills": 21, "assists": 82, "player_damage": 3189843,
               "building_damage": 3289538, "healing": 0, "damage_taken": 4196936,
               "deaths": 12, "revives": 0, "fen_gu": 0},
    "indicators": {"kda": 8.58, "dps": 4695.0, "kpa_damage": 62907.0, "damage_per_death": 539948.0,
                   "taken_per_death": 349745.0, "healing_per_death": 0.0, "heal_conversion": 0.0,
                   "revive_rate": 0.0, "fen_gu_rate": 0.0},
})
assert squad_out.squad_name == "进攻1 第1队"

prof_out = ProfessionStats(**{
    "profession": "素问", "count": 3, "avg_kills": 5.0, "avg_damage": 1000.0, "avg_healing": 5000.0,
    "avg_kda": 8.0, "avg_dps": 10.0, "avg_kpa_damage": 20.0, "avg_damage_per_death": 30.0,
    "avg_taken_per_death": 40.0, "avg_healing_per_death": 50.0, "avg_heal_conversion": 0.8,
    "avg_kill_ratio": 0.1, "avg_assist_ratio": 0.2, "avg_player_damage_ratio": 0.3,
    "avg_building_ratio": 0.4, "avg_taken_ratio": 0.5, "avg_death_ratio": 0.6, "avg_heal_ratio": 0.7,
    "avg_revive_rate": 0.001, "avg_fen_gu_rate": 0.002,
    "camps": [{"camp": "横戈", "count": 2, "avg_kills": 5.0, "avg_player_damage": 1000.0,
               "avg_building_damage": 200.0, "avg_healing": 5000.0, "avg_damage_taken": 3000.0,
               "avg_kda": 8.0}],
    "comparison": [{"metric": "avg_kills", "camp1": "横戈", "camp2": "仗剑",
                    "value1": 5.0, "value2": 4.0, "diff": 1.0, "wave": 25.0}],
})
assert prof_out.count == 3
assert prof_out.comparison[0].wave == 25.0

indicator_out = IndicatorOut(**{
    "id": 1, "schedule_id": 1, "round_no": 1, "player_name": "玩家1",
    "profession": "玄机", "camp": "横戈", "kills": 21, "springs": 5, "assists": 82,
    "player_damage": 3189843, "armor_break_damage": 0, "building_damage": 3289538,
    "tower_break_damage": 0, "healing": 0, "damage_taken": 4196936, "deaths": 12, "revives": 0,
    "fen_gu": 0, "kda": 8.58, "dps": 4695, "kpa_damage": 62907, "damage_per_death": 539948,
    "taken_per_death": 349745, "healing_per_death": 0, "heal_conversion": 0,
    "kill_ratio": 0.0522, "assist_ratio": 0.0141, "player_damage_ratio": 0.0114,
    "building_ratio": 0.0731, "taken_ratio": 0.0140, "death_ratio": 0.0375, "heal_ratio": 0.0,
    "revive_rate": 0.0, "fen_gu_rate": 0.0,
})
assert indicator_out.kda == 8.58

print("[PASS] all assertions OK: 16 derived indicators, camp totals, Pydantic response models")

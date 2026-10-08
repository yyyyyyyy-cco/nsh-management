"""比赛数据统计计算：衍生指标与阵营汇总（纯函数，无 DB 依赖）。

由 match_data_service 拆出。
"""

# 比赛时长固定 23 分钟，用于秒伤/技能使用率等指标
MATCH_DURATION_SECONDS = 23 * 60
MATCH_DURATION_MINUTES = 23


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

    # 辅助型玩家（治疗职业：治疗量 > 玩家伤害；或坦克职业铁衣）
    # KDA 中助攻按 ×0.8 折算、死亡按 ×1.2 加重（仅影响 KDA，其他指标用原始值）
    is_support = healing > player_damage or record.profession == "铁衣"
    kda_assists = assists * 0.8 if is_support else assists
    kda_deaths = deaths * 1.2 if is_support else deaths
    kda = round((kills + kda_assists) / max(kda_deaths, 1), 2)
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
        "revive_rate": round(revives / MATCH_DURATION_MINUTES, 4),
        "fen_gu_rate": round(fen_gu / MATCH_DURATION_MINUTES, 4),
    }


def get_camp_totals(records: list) -> dict[str, dict]:
    """按阵营汇总数据（占比指标的分母为整个阵营）。"""
    totals: dict[str, dict] = {}
    for r in records:
        camp = r.camp
        t = totals.setdefault(
            camp,
            {
                "camp": camp,
                "player_count": 0,
                "kills": 0,
                "assists": 0,
                "player_damage": 0,
                "building_damage": 0,
                "healing": 0,
                "damage_taken": 0,
                "deaths": 0,
                "springs": 0,
                "revives": 0,
                "fen_gu": 0,
            },
        )
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

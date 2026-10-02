# -*- coding: utf-8 -*-
"""v4 权重精确推导（供 analysis.ts 转录）：
v3 规则 + 边际资格收紧：rs<1 且 rs>=0.5 且职业内非零占比>=50%（挡掉小均值噪声指标）
边际项倍数在运行时封顶 2.0（前端按 权重<0.06 判别边际项），本脚本不计 cap
"""
import os, sqlite3, sys, io
from collections import defaultdict
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 数据源：默认取 backend/data 下的服务器快照，可用环境变量 NSH_DB_PATH 覆盖（2026-10-02 移除硬编码绝对路径）
DB_PATH = Path(os.environ.get("NSH_DB_PATH") or Path(__file__).resolve().parents[1] / "data" / "nsh-server-20260907.db")
conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT * FROM match_data")
rows = [dict(r) for r in cur.fetchall()]
conn.close()

GET = {
    '击杀': lambda r: r['kills'], '助攻': lambda r: r['assists'],
    '人伤': lambda r: r['player_damage'] + r['armor_break_damage'],
    '建筑': lambda r: r['building_damage'] + r['tower_break_damage'] * 0.7,
    '治疗': lambda r: r['healing'], '承伤': lambda r: r['damage_taken'],
    '复活': lambda r: r['revives'], '焚骨': lambda r: r['fen_gu'],
}
SCARCE = {'复活', '焚骨'}

def archetype(r):
    p = r['profession']
    b = GET['建筑'](r); d = GET['人伤'](r)
    if p == '潮光': return '潮光·拆塔' if b >= d else '潮光·输出'
    if p == '鸿音': return '鸿音·治疗' if r['healing'] > b else '鸿音·拆塔'
    return p

overall = {m: sum(f(r) for r in rows)/len(rows) for m, f in GET.items()}
groups = defaultdict(list)
for r in rows: groups[archetype(r)].append(r)

for arch in sorted(groups):
    grp = groups[arch]
    means = {m: sum(f(r) for r in grp)/len(grp) for m, f in GET.items()}
    nonzero = {m: sum(1 for r in grp if f(r) > 0)/len(grp) for m, f in GET.items()}
    rs = {m: (means[m]/overall[m] if overall[m] else 0) for m in GET}
    core = {m: v for m, v in rs.items() if v >= 1.5 and m not in SCARCE}
    scarce_core = [m for m in SCARCE if rs[m] >= 1.5]
    minor = {m: v for m, v in rs.items() if 1.0 <= v < 1.5}
    marginal = [m for m, v in rs.items()
                if v < 1.0 and v >= 0.5 and means[m] > 0 and nonzero[m] >= 0.5]
    raw = {}
    core_sum = sum(core.values())
    if core_sum:
        for m, v in core.items(): raw[m] = 0.85 * v / core_sum
    for m in scarce_core: raw[m] = 0.30
    if minor:
        share = 0.15 if core_sum else 1.0
        for m in minor: raw[m] = share / len(minor)
    for m in marginal: raw[m] = raw.get(m, 0) + 0.05
    total = sum(raw.values()) or 1
    w = {m: raw.get(m, 0)/total for m in GET}
    items = '  '.join(f"{m}={w[m]:.4f}" for m in GET if w[m] > 0)
    print(f"  {arch:8s}: {items}   和={sum(w.values()):.4f}  边际={marginal}")

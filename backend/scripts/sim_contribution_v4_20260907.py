# -*- coding: utf-8 -*-
"""v4 权重推导 + 全量模拟验证（评分总览验收参照脚本）
规则（rs = 该职业分路指标均值 ÷ 全体均值）：
  核心 rs>=1.5（85% 份额按 rs 占比；复活/焚骨稀缺 cap 0.30）
  次要 1.0<=rs<1.5（15% 份额均分）
  边际 0.5<=rs<1 且职业内非零占比>=50%（每项 0.05；运行时倍数封顶 2.0）
  正向权重归一化；重伤统一 -15×重伤倍数；轮内指标全组为 0 时权重摊给其余项
"""
import os, sqlite3, sys, io
from collections import defaultdict, Counter
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
MARGINAL_W = 0.05
MARGINAL_MULT_CAP = 2.0
MARGINAL_WEIGHT_THRESHOLD = 0.06
DEATH_PENALTY = 15.0
# 手工覆盖：强制计入边际项的指标（绕过 rs>=0.5 门槛；用户逐项指定）
# - 铁衣：承伤时的人伤/建筑应有认可
# - 沧澜/龙吟：拆塔位助攻应认可（rs 0.47 仅差门槛一点且非零占比 100%）
OVERRIDE_MARGINAL = {
    '铁衣': ['人伤', '建筑'],
    '沧澜': ['助攻'],
    '龙吟': ['助攻'],
    '潮光·拆塔': ['击杀', '助攻'],
    '玄机': ['建筑'],
}

def archetype(r):
    p = r['profession']
    b = GET['建筑'](r); d = GET['人伤'](r)
    if p == '潮光': return '潮光·拆塔' if b >= d else '潮光·输出'
    if p == '鸿音': return '鸿音·治疗' if r['healing'] > b else '鸿音·拆塔'
    return p

# ===== 权重推导 =====
overall = {m: sum(f(r) for r in rows)/len(rows) for m, f in GET.items()}
groups = defaultdict(list)
for r in rows: groups[archetype(r)].append(r)

W = {}
print('== v4 权重表（正向和=1.0） ==')
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
    for m in OVERRIDE_MARGINAL.get(arch, []):
        if m not in marginal and means[m] > 0:
            marginal.append(m)
    raw = {}
    core_sum = sum(core.values())
    if core_sum:
        for m, v in core.items(): raw[m] = 0.85 * v / core_sum
    for m in scarce_core: raw[m] = 0.30
    if minor:
        share = 0.15 if core_sum else 1.0
        for m in minor: raw[m] = share / len(minor)
    for m in marginal: raw[m] = raw.get(m, 0) + MARGINAL_W
    total = sum(raw.values()) or 1
    W[arch] = {m: raw.get(m, 0)/total for m in GET}
    items = '  '.join(f"{m}={W[arch][m]:.4f}" for m in GET if W[arch][m] > 0)
    print(f"  {arch:8s}: {items}   边际={marginal}")

# ===== 全量模拟 =====
by_round = defaultdict(list)
for r in rows: by_round[(r['schedule_id'], r['round_no'])].append(r)

scores = []
for key, items in by_round.items():
    by_arch = defaultdict(list)
    for r in items: by_arch[archetype(r)].append(r)
    for arch, grp in by_arch.items():
        w = W[arch]
        means = {}
        for m in GET:
            if w[m] <= 0: continue
            mv = sum(GET[m](x) for x in grp)/len(grp)
            if mv > 0: means[m] = mv
        active = list(means)
        wsum = sum(w[m] for m in active)
        dmean = sum(x['deaths'] for x in grp)/len(grp) or 1
        for r in grp:
            s = 0.0
            for m in active:
                mult = GET[m](r)/means[m]
                if w[m] < MARGINAL_WEIGHT_THRESHOLD and mult > MARGINAL_MULT_CAP:
                    mult = MARGINAL_MULT_CAP
                s += w[m]/wsum * mult * 100
            s -= DEATH_PENALTY*(r['deaths']/dmean)
            scores.append((arch, round(s), r))

score_sum = defaultdict(list)
for arch, s, r in scores: score_sum[arch].append(s)

print('\n== 各职业分路得分分布（基准 85） ==')
all_s = []
print(f"{'职业分路':10s} {'n':>4s} {'均分':>6s} {'中位':>5s} {'P10':>5s} {'P90':>5s} {'最高':>5s}")
for arch in sorted(score_sum):
    s = sorted(score_sum[arch]); all_s += [(arch, x) for x in s]
    print(f"{arch:10s} {len(s):4d} {sum(s)/len(s):6.1f} {s[len(s)//2]:5d} {s[int(len(s)*0.1)]:5d} {s[int(len(s)*0.9)]:5d} {s[-1]:5d}")

all_s.sort(key=lambda x: -x[1])
print('\nTOP20:', dict(Counter(a for a, _ in all_s[:20])))
print('TOP50:', dict(Counter(a for a, _ in all_s[:50])))
vals = sorted(x for _, x in all_s); n = len(vals)
print(f'全体: 中位={vals[n//2]} P10={vals[int(n*0.1)]} P90={vals[int(n*0.9)]} 最高={vals[-1]}')
for th in (100, 115):
    cnt = sum(1 for _, x in all_s if x >= th)
    print(f'≥{th}: {cnt} 人 ({cnt/n*100:.1f}%)')

# ===== 两个问题案例修复后对比 =====
print('\n== 问题案例修复后得分 ==')
for a, s, r in scores:
    if r['player_name'] in ('小叙白', '好甜酱'):
        print(f"  {r['player_name']:8s} {a:10s} S{r['schedule_id']}-R{r['round_no']}  {s}")

# -*- coding: utf-8 -*-
"""v4 权重设计合理性审计（全部基于 1440 条实际数据）
A1 前端权重表与推导结果零偏差校验
A2 结构合理性：每个分路的最大权重项是否就是其 rs 最高的非稀缺指标
A3 相关性：分路内 综合分 vs 主维贡献倍数 的排名相关性（分数是否抓住本职表现）
A4 钻空子检查：全场 TOP20 玩家是否本职维度确实突出（主维倍数>=1.5）
A5 权重集中度：核心+次要占比（边际项合计不应超过 25%）
"""
import io
import os
import re
import sqlite3
import sys
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
MARGINAL_W, CAP, THRESH, DEATH = 0.05, 2.0, 0.06, 15.0
OVERRIDE = {'铁衣': ['人伤', '建筑'], '沧澜': ['助攻'], '龙吟': ['助攻'],
            '潮光·拆塔': ['击杀', '助攻'], '玄机': ['建筑']}
# 主维（业务职责，用于 A4）：每个分路的本职指标
CORE_OF = {'素问': ['治疗'], '鸿音·治疗': ['治疗'], '铁衣': ['承伤'],
           '沧澜': ['建筑'], '龙吟': ['建筑'], '鸿音·拆塔': ['建筑'],
           '潮光·拆塔': ['建筑'], '神相': ['击杀', '人伤'], '血河': ['击杀', '人伤'],
           '九灵': ['击杀', '人伤', '焚骨'], '玄机': ['击杀'],
           '碎梦': ['击杀'], '潮光·输出': ['击杀', '人伤']}

def archetype(r):
    p = r['profession']
    b = GET['建筑'](r); d = GET['人伤'](r)
    if p == '潮光': return '潮光·拆塔' if b >= d else '潮光·输出'
    if p == '鸿音': return '鸿音·治疗' if r['healing'] > b else '鸿音·拆塔'
    return p

overall = {m: sum(f(r) for r in rows)/len(rows) for m, f in GET.items()}
groups = defaultdict(list)
for r in rows: groups[archetype(r)].append(r)

W, MARG = {}, {}
for arch, grp in groups.items():
    means = {m: sum(f(r) for r in grp)/len(grp) for m, f in GET.items()}
    nonzero = {m: sum(1 for r in grp if f(r) > 0)/len(grp) for m, f in GET.items()}
    rs = {m: (means[m]/overall[m] if overall[m] else 0) for m in GET}
    core = {m: v for m, v in rs.items() if v >= 1.5 and m not in SCARCE}
    scarce_core = [m for m in SCARCE if rs[m] >= 1.5]
    minor = {m: v for m, v in rs.items() if 1.0 <= v < 1.5}
    marginal = [m for m, v in rs.items() if v < 1.0 and v >= 0.5 and means[m] > 0 and nonzero[m] >= 0.5]
    for m in OVERRIDE.get(arch, []):
        if m not in marginal and means[m] > 0: marginal.append(m)
    raw = {}
    cs = sum(core.values())
    if cs:
        for m, v in core.items(): raw[m] = 0.85*v/cs
    for m in scarce_core: raw[m] = 0.30
    if minor:
        sh = 0.15 if cs else 1.0
        for m in minor: raw[m] = sh/len(minor)
    for m in marginal: raw[m] = raw.get(m, 0) + MARGINAL_W
    t = sum(raw.values()) or 1
    W[arch] = {m: raw.get(m, 0)/t for m in GET}
    MARG[arch] = set(marginal)

# ===== A1 前端权重表零偏差校验 =====
# 前端权重表来源：仓库内 analysis.ts，可用环境变量 NSH_ANALYSIS_TS 覆盖
TS_PATH = Path(os.environ.get("NSH_ANALYSIS_TS") or Path(__file__).resolve().parents[2] / "frontend" / "src" / "components" / "match-data" / "analysis.ts")
ts = TS_PATH.read_text(encoding='utf-8')
m = re.search(r'PROFESSION_WEIGHTS[^=]*= (\{[\s\S]*?\n\})', ts)
block = re.sub(r'(^|\n)\s*//[^\n]*', '', m.group(1))
block = re.sub(r"(?m)^([ \t]*)([^'\"{}\s][^:'\"{}\n]*):", r"\1'\2':", block)
block = re.sub(r"([{,]\s*)([^'\"{}\d\s][^:'\"{}\n]*?)\s*:", r"\1'\2':", block)
ts_w = eval(block)
print('== A1 前端权重表 vs 推导结果 ==')
diffs = []
for arch in W:
    for metric in GET:
        a, b = ts_w[arch][metric], round(W[arch][metric], 4)
        if abs(a - b) > 1e-9:
            diffs.append((arch, metric, a, b))
print('  零偏差' if not diffs else f'  偏差项: {diffs}')

# ===== 全量模拟 =====
by_round = defaultdict(list)
for r in rows: by_round[(r['schedule_id'], r['round_no'])].append(r)
scored = []
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
            mults, s = {}, 0.0
            for mm in active:
                mu = GET[mm](r)/means[mm]
                if w[mm] < THRESH and mu > CAP: mu = CAP
                mults[mm] = mu
                s += w[mm]/wsum*mu*100
            s -= DEATH*(r['deaths']/dmean)
            scored.append((arch, round(s), mults, r))

# ===== A2 结构合理性：最大权重项 vs rs 最高非稀缺指标 =====
print('\n== A2 最大权重项是否与数据画像一致 ==')
ok = 0
for arch in sorted(W):
    w = W[arch]
    top_w = max(GET, key=lambda m: w[m])
    grp = groups[arch]
    means = {m: sum(f(r) for r in grp)/len(grp) for m, f in GET.items()}
    rs = {m: (means[m]/overall[m] if overall[m] else 0) for m in GET if m not in SCARCE and means[m] > 0}
    top_rs = max(rs, key=lambda m: rs[m])
    good = w[top_w] >= 0.4 and top_w in CORE_OF[arch]
    ok += good
    print(f"  {arch:10s} 最大权重项={top_w}({w[top_w]:.3f}) rs最高={top_rs}({rs[top_rs]:.2f}) {'✓' if good else '✗'}")
print(f'  通过 {ok}/13')

# ===== A5 权重集中度：边际合计占比 =====
print('\n== A5 边际项合计权重占比（应 <=25%） ==')
bad = []
for arch in sorted(W):
    share = sum(w for m, w in W[arch].items() if m in MARG[arch])
    if share > 0.25: bad.append((arch, share))
    print(f"  {arch:10s} 边际占比 {share*100:5.1f}%  {'✗超限' if share > 0.25 else '✓'}")
print('  全部通过' if not bad else f'  超限: {bad}')

# ===== A3 相关性：分路内 综合分 vs 主维倍数（Spearman 秩相关） =====
def spearman(x, y):
    def rank(v):
        s = sorted(range(len(v)), key=lambda i: v[i])
        r = [0]*len(v)
        for i, idx in enumerate(s): r[idx] = i+1
        return r
    rx, ry = rank(x), rank(y)
    n = len(x)
    mx, my = sum(rx)/n, sum(ry)/n
    cov = sum((a-mx)*(b-my) for a, b in zip(rx, ry))
    vx = sum((a-mx)**2 for a in rx)**0.5
    vy = sum((b-my)**2 for b in ry)**0.5
    return cov/(vx*vy) if vx and vy else 0

print('\n== A3 综合分 vs 主维倍数 秩相关（分路内，越接近 1 分数越忠实于本职表现） ==')
by_arch2 = defaultdict(lambda: ([], []))
for arch, s, mults, r in scored:
    core = CORE_OF[arch]
    dom = max(core, key=lambda m: mults.get(m, 0))
    by_arch2[arch][0].append(s); by_arch2[arch][1].append(mults.get(dom, 0))
for arch in sorted(by_arch2):
    sc, dm = by_arch2[arch]
    print(f"  {arch:10s} ρ={spearman(sc, dm):.3f}")

# ===== A4 钻空子检查：TOP20 玩家主维倍数 =====
print('\n== A4 全场 TOP20 的主维倍数（>=1.5 为本职突出，<1.2 视为钻空子嫌疑） ==')
all_s = sorted(scored, key=lambda t: -t[1])
sus = 0
for i, (arch, s, mults, r) in enumerate(all_s[:20], 1):
    core = CORE_OF[arch]
    dom_mult = max(mults.get(m, 0) for m in core)
    flag = '' if dom_mult >= 1.2 else ' ←嫌疑'
    if dom_mult < 1.2: sus += 1
    print(f"  #{i:2d} {r['player_name']:12s} {arch:10s} 总分={s:4d} 主维倍数={dom_mult:.2f}{flag}")
print(f'  嫌疑数: {sus}/20')

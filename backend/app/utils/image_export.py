"""成员常驻库图片导出：按主职业分区绘制长图（PNG），供群内分享。

中文字体解析顺序：Linux 容器（fonts-wqy-microhei）→ Windows 本地雅黑 → PIL 默认。
"""
import glob
import os
from datetime import datetime, timezone
from math import ceil

from PIL import Image, ImageDraw, ImageFont

from app.models.member import Member

# 画布与布局常量
WIDTH = 960
PADDING = 24
COLUMNS = 4
CELL_W = (WIDTH - PADDING * 2) // COLUMNS  # 228
CELL_H = 46
SECTION_TITLE_H = 40
SECTION_GAP = 14
HEADER_H = 78
FOOTER_H = 34

# 单张长图成员上限：画布高度随人数线性增长，800 人约 26MB 位图，
# 超过后内存与编码耗时不可控（5000 人约 165MB），提示分批导出
MAX_IMAGE_MEMBERS = 800

# 配色（呼应宣纸鎏金主题）
BG = (250, 247, 240)
GOLD = (166, 124, 26)
GOLD_SOFT = (217, 182, 74)
INK = (43, 38, 32)
INK_SOFT = (138, 131, 120)
WHITE = (255, 255, 255)
LINE = (230, 223, 206)

_FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",   # 容器：fonts-wqy-microhei
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    "C:/Windows/Fonts/msyh.ttc",                        # Windows 开发环境
    "C:/Windows/Fonts/simhei.ttf",
]


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in _FONT_CANDIDATES:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    # 兜底：Glob 搜索任意已装中文字体
    for pattern in ("/usr/share/fonts/**/*wqy*", "/usr/share/fonts/**/*noto*cjk*"):
        found = glob.glob(pattern, recursive=True)
        if found:
            return ImageFont.truetype(found[0], size)
    return ImageFont.load_default()


def draw_members_png(members: list[Member], guild_name: str | None = None) -> bytes:
    """按主职业分区绘制成员长图，返回 PNG 字节流。超过人数上限抛 ValueError。"""
    if len(members) > MAX_IMAGE_MEMBERS:
        raise ValueError(f"成员数超过 {MAX_IMAGE_MEMBERS} 人长图上限，请按职业筛选后分批导出")

    title_font = _load_font(26)
    sub_font = _load_font(13)
    section_font = _load_font(18)
    name_font = _load_font(16)
    note_font = _load_font(11)

    buckets: dict[str, list[Member]] = {}
    for member in members:
        buckets.setdefault(member.main_profession, []).append(member)
    # 组内正式在前、替补在后，同状态按姓名；区块按人数多的职业在前
    groups = sorted(
        ((p, sorted(g, key=lambda m: (m.status != "formal", m.name))) for p, g in buckets.items()),
        key=lambda kv: -len(kv[1]),
    )

    # 预计算总高度
    total_rows = sum(ceil(len(g) / COLUMNS) for _, g in groups)
    height = HEADER_H + len(groups) * SECTION_TITLE_H + total_rows * CELL_H \
        + (len(groups) - 1) * SECTION_GAP + FOOTER_H + PADDING

    img = Image.new("RGB", (WIDTH, height), BG)
    draw = ImageDraw.Draw(img)

    # ===== 头部 =====
    draw.rectangle([0, 0, WIDTH, 6], fill=GOLD_SOFT)
    title = guild_name or "常驻库成员表"
    draw.text((PADDING, 20), f"{title} · 常驻库", font=title_font, fill=INK)
    date_text = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d")
    stat_text = f"{len(members)} 人 · {len(groups)} 个职业 · {date_text}"
    stat_w = draw.textlength(stat_text, font=sub_font)
    draw.text((WIDTH - PADDING - stat_w, 30), stat_text, font=sub_font, fill=INK_SOFT)
    draw.line([PADDING, HEADER_H - 10, WIDTH - PADDING, HEADER_H - 10], fill=LINE, width=1)

    # ===== 职业分区 =====
    y = HEADER_H
    for profession, group in groups:
        formal = sum(1 for m in group if m.status == "formal")
        draw.text((PADDING, y + 6), profession, font=section_font, fill=GOLD)
        count_text = f"{len(group)} 人（正式 {formal} / 替补 {len(group) - formal}）"
        cw = draw.textlength(count_text, font=sub_font)
        draw.text((WIDTH - PADDING - cw, y + 12), count_text, font=sub_font, fill=INK_SOFT)
        y += SECTION_TITLE_H

        for index, member in enumerate(group):
            col = index % COLUMNS
            row = index // COLUMNS
            x = PADDING + col * CELL_W
            cy = y + row * CELL_H
            is_formal = member.status == "formal"
            draw.rectangle([x, cy, x + CELL_W - 8, cy + CELL_H - 8], fill=WHITE, outline=LINE)
            name_color = INK if is_formal else INK_SOFT
            name = member.name if is_formal else f"{member.name}（替）"
            draw.text((x + 10, cy + 6), name, font=name_font, fill=name_color)
            if member.sub_profession:
                sub_text = f"副：{member.sub_profession}"
                draw.text((x + 10, cy + 27), sub_text, font=note_font, fill=INK_SOFT)
        y += ceil(len(group) / COLUMNS) * CELL_H + SECTION_GAP

    # ===== 底部水印 =====
    footer = "轻衫都会用的帮会联赛管理系统 · 本地导出"
    fw = draw.textlength(footer, font=note_font)
    draw.text(((WIDTH - fw) // 2, height - FOOTER_H + 2), footer, font=note_font, fill=INK_SOFT)

    from io import BytesIO
    out = BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()

# -*- coding: utf-8 -*-
"""成员常驻库图片导出（PNG）的行为回归（合规化计划 W1-11 / 发现 F-56）。

**为什么补这个文件**：把 Pillow 由 `11.1.0` 升到 `12.3.0` 时（依据见 `security-review.md §14.7`）
才发现 `app/utils/image_export.py` 的导出路径**没有任何测试覆盖** —— 当时只能给出
"模块可导入 + 字体可加载"这种弱证据。本文件把导出的**行为契约**固定下来：

- 输出是**合法 PNG**，画布**宽度固定**，**高度**按实现公式随「职业区块数」与「行数」线性增长；
- **空列表不抛异常**（0 人时高度公式含 `(groups-1)*SECTION_GAP` 负项，属易错点）；
- 「正式 / 替补 / 副职业」三类文本分支都能跑通；
- **人数上限守卫**：超过 `MAX_IMAGE_MEMBERS` 抛 `ValueError` 且消息含上限数字。

**字体**：`_load_font` 有完整回退链（Linux `wqy` → Windows 雅黑 → glob → `ImageFont.load_default()`），
所以本文件**不断言字形**（无中文字体的 CI 也应通过），只断言结构与尺寸。

依赖 Pillow；缺失时模块级跳过（ai-checklist 第 32 条）。
"""
import unittest
from io import BytesIO
from math import ceil

try:
    from PIL import Image

    from app.utils import image_export
    from app.utils.image_export import draw_members_png
except ImportError as exc:  # pragma: no cover — 无依赖环境
    raise unittest.SkipTest(f"缺少运行依赖（Pillow），跳过本模块：{exc}") from exc


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class _Member:
    """导出函数只用到这几个属性（轻量替身，避免依赖 ORM，与 excel 导出用例同风格）。"""

    def __init__(
        self,
        name: str,
        main_profession: str = "铁衣",
        sub_profession: str | None = None,
        status: str = "formal",
    ) -> None:
        self.name = name
        self.main_profession = main_profession
        self.sub_profession = sub_profession
        self.status = status


def _expected_height(profession_counts: dict[str, int]) -> int:
    """按实现的高度公式**独立重算**（引用模块常量，常量若改这里自动跟随）。"""
    groups = len(profession_counts)
    total_rows = sum(ceil(n / image_export.COLUMNS) for n in profession_counts.values())
    return (
        image_export.HEADER_H
        + groups * image_export.SECTION_TITLE_H
        + total_rows * image_export.CELL_H
        + (groups - 1) * image_export.SECTION_GAP
        + image_export.FOOTER_H
        + image_export.PADDING
    )


def _size_of(members: list[_Member]) -> tuple[int, int]:
    with Image.open(BytesIO(draw_members_png(members))) as img:
        return img.size


class ImageExportTest(unittest.TestCase):
    def test_output_is_png_with_expected_canvas(self) -> None:
        data = draw_members_png([_Member("张三")], guild_name="测试帮会")
        self.assertIsInstance(data, bytes)
        self.assertTrue(data.startswith(PNG_MAGIC), "输出必须是 PNG 字节流")
        with Image.open(BytesIO(data)) as img:
            self.assertEqual(img.format, "PNG")
            self.assertEqual(img.width, image_export.WIDTH)
            self.assertEqual(img.height, _expected_height({"铁衣": 1}))

    def test_height_grows_one_row_per_four_members(self) -> None:
        one = _size_of([_Member("成员1")])
        five = _size_of([_Member(f"成员{i}") for i in range(1, 6)])
        # 同职业：1 人 = 1 行，5 人 = 2 行
        self.assertEqual(five[1] - one[1], image_export.CELL_H)
        self.assertEqual(five[0], one[0])  # 宽度不受人数影响

    def test_height_grows_with_profession_sections(self) -> None:
        one = _size_of([_Member("甲")])
        two = _size_of([_Member("甲"), _Member("乙", main_profession="素问")])
        expected_delta = (
            image_export.SECTION_TITLE_H + image_export.CELL_H + image_export.SECTION_GAP
        )
        self.assertEqual(two[1] - one[1], expected_delta)
        self.assertEqual(two[1], _expected_height({"铁衣": 1, "素问": 1}))

    def test_empty_list_does_not_raise(self) -> None:
        data = draw_members_png([])
        self.assertTrue(data.startswith(PNG_MAGIC), "0 人也应产出合法 PNG")
        self.assertEqual(_size_of([])[1], _expected_height({}))

    def test_formal_substitute_and_sub_profession_branches(self) -> None:
        members = [
            _Member("正式甲", status="formal", sub_profession="素问"),
            _Member("替补乙", status="substitute"),
            _Member("替补丙", status="substitute", main_profession="九灵"),
        ]
        data = draw_members_png(members, guild_name="帮会")
        self.assertTrue(data.startswith(PNG_MAGIC))
        self.assertEqual(_size_of(members)[1], _expected_height({"铁衣": 2, "九灵": 1}))

    def test_member_limit_guard(self) -> None:
        over = [_Member(f"m{i}") for i in range(image_export.MAX_IMAGE_MEMBERS + 1)]
        with self.assertRaises(ValueError) as ctx:
            draw_members_png(over)
        self.assertIn(str(image_export.MAX_IMAGE_MEMBERS), str(ctx.exception))
        # 覆盖边界（有意）：恰好 MAX_IMAGE_MEMBERS 人的**成功**路径未在此执行 ——
        # 要生成约 26MB 位图、耗时不可控，见计划 W1-11 的说明。
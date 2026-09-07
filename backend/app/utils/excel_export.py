"""Excel 成员导出：按主职业分 Sheet，组内正式在前、替补在后，与导入模板表头一致。"""
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from app.models.member import Member
from app.utils.constants import PROFESSIONS

# 表头与 excel_import 的表头识别一一对应，确保导出文件可直接回导
HEADERS = ["姓名", "主职业", "副职业", "状态", "备注"]
STATUS_LABELS = {"formal": "正式", "substitute": "替补"}
COL_WIDTHS = [14, 14, 14, 10, 30]

# Sheet 名中的 Excel 非法字符（职业名为固定中文，正常不会命中，兜底防御）
_SHEET_ILLEGAL = str.maketrans({c: "-" for c in r":\/?*[]"})


def _group_members(members: list[Member]) -> list[tuple[str, list[Member]]]:
    """按主职业分组：Sheet 顺序按 PROFESSIONS 常量，未知职业兜底到最后；
    组内正式在前、替补在后，同状态按姓名排序。"""
    buckets: dict[str, list[Member]] = {}
    for member in members:
        buckets.setdefault(member.main_profession, []).append(member)

    ordered: list[tuple[str, list[Member]]] = []
    for profession in PROFESSIONS:
        if profession in buckets:
            ordered.append((profession, buckets.pop(profession)))
    for profession in sorted(buckets):  # 兜底：非常规职业名
        ordered.append((profession, buckets[profession]))

    result = []
    for profession, group in ordered:
        group.sort(key=lambda m: (m.status != "formal", m.name))
        result.append((profession, group))
    return result


def _write_group(sheet, members: list[Member]) -> None:
    header_fill = PatternFill("solid", fgColor="F3E9D2")
    header_font = Font(bold=True)
    for col, title in enumerate(HEADERS, start=1):
        cell = sheet.cell(row=1, column=col, value=title)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
        sheet.column_dimensions[get_column_letter(col)].width = COL_WIDTHS[col - 1]

    for row, member in enumerate(members, start=2):
        sheet.cell(row=row, column=1, value=member.name)
        sheet.cell(row=row, column=2, value=member.main_profession)
        sheet.cell(row=row, column=3, value=member.sub_profession or "")
        sheet.cell(row=row, column=4, value=STATUS_LABELS.get(member.status, member.status))
        sheet.cell(row=row, column=5, value=member.remark or "")

    sheet.freeze_panes = "A2"  # 冻结表头行


def build_members_xlsx(members: list[Member]) -> bytes:
    """按主职业生成多 Sheet 的 xlsx 字节流，每个职业一个 Sheet。"""
    workbook = Workbook()
    workbook.remove(workbook.active)  # 移除默认空 Sheet

    for profession, group in _group_members(members):
        sheet = workbook.create_sheet(title=profession.translate(_SHEET_ILLEGAL)[:31])
        _write_group(sheet, group)

    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()

"""Excel 成员导入解析：自动识别表头，重名跳过，返回导入结果。"""
from io import BytesIO

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.utils.constants import PROFESSIONS


class ExcelImportError(Exception):
    """导入失败（格式问题），HTTP 400。"""


def _header_index(header: str) -> str:
    """表头归一化：去掉空白，返回字段名。"""
    text = (header or "").strip()
    if not text:
        return ""
    if "姓名" in text or "名字" in text:
        return "name"
    if "主职业" in text or text == "职业":
        return "main_profession"
    if "副职业" in text:
        return "sub_profession"
    if "状态" in text:
        return "status"
    if "备注" in text:
        return "remark"
    return ""


def _parse_status(value) -> str:
    text = str(value or "").strip()
    if text in ("正式", "formal", "1"):
        return "formal"
    if text in ("替补", "substitute", "0"):
        return "substitute"
    return "formal"


async def import_members(session: AsyncSession, guild_id: int, content: bytes) -> dict:
    """解析 Excel 成员数据并入库，返回 {imported, skipped, errors}。"""
    try:
        workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
        sheet = workbook.active
    except Exception:
        raise ExcelImportError("Excel 文件解析失败，请检查格式")

    rows = list(sheet.iter_rows(values_only=True))
    if len(rows) < 2:
        raise ExcelImportError("Excel 至少需要表头行和一条数据")

    header = [_header_index(cell) for cell in rows[0]]
    if "name" not in header or "main_profession" not in header:
        raise ExcelImportError("表头需包含「姓名」和「职业/主职业」列")

    existing = set(
        (await session.execute(select(Member.name).where(Member.guild_id == guild_id))).scalars()
    )

    imported = 0
    skipped = 0
    errors: list[str] = []
    new_members: list[Member] = []
    for row in rows[1:]:
        record = {field: (row[index] if index < len(row) else None) for index, field in enumerate(header) if field}
        name = str(record.get("name") or "").strip()
        if not name:
            continue
        if name in existing:
            skipped += 1
            continue
        profession = str(record.get("main_profession") or "").strip()
        if profession not in PROFESSIONS:
            errors.append(f"{name}：无效职业「{profession}」")
            skipped += 1
            continue
        new_members.append(
            Member(
                guild_id=guild_id,
                name=name,
                main_profession=profession,
                sub_profession=str(record.get("sub_profession") or "").strip() or None,
                status=_parse_status(record.get("status")),
                remark=str(record.get("remark") or "").strip() or None,
            )
        )
        existing.add(name)

    if new_members:
        session.add_all(new_members)
        await session.commit()
        imported = len(new_members)
    return {"imported": imported, "skipped": skipped, "errors": errors}

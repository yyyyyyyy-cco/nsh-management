"""成员 Excel 导入规则的回归测试（补充既有 selfcheck_member_exports.py 未覆盖的三条文档规则）。

已由 `backend/scripts/selfcheck_member_exports.py` 覆盖（不重复）：
来源行不决定归属、新旧模板回导、空导出有效工作表、文件名清理、未绑定帮会 403、出勤隔离；
公式注入防护由 `tests/test_excel_export_formula.py` 覆盖。

本文件补充：
- 重名跳过（`database-design §2.5 members` 业务约束、`design-document-v2 §3`「重名跳过」）；
- 数据行上限 5000（`security-review` 威胁核对表第 10 行）；
- `.xlsx` 扩展名限制与 5MB 大小双检（声明长度 + 读取后二次兜底，`api/v1/members.py`）。
"""

from __future__ import annotations

import unittest
from io import BytesIO
from types import SimpleNamespace

from openpyxl import Workbook
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from support import profession_seed_rows

from app.api.v1.members import import_excel
from app.core.database import Base
from app.models.guild import Guild
from app.models.member import Member
from app.utils.excel_export import build_members_xlsx
from app.utils.excel_import import MAX_FILE_SIZE, MAX_IMPORT_ROWS, ExcelImportError, import_members


def _xlsx_with_rows(rows: list[tuple]) -> bytes:
    """按导出格式（含来源行）生成工作簿字节。"""
    wb = Workbook()
    sheet = wb.active
    sheet.append(["所属帮会", "上限测试帮会", "帮会ID", 1, "仅作来源标识，非防伪凭证"])
    sheet.append(["姓名", "主职业", "副职业", "状态", "备注"])
    for row in rows:
        sheet.append(list(row))
    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        self.session.add(Guild(id=1, name="上限测试帮会"))
        self.session.add_all(profession_seed_rows())
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _count(self) -> int:
        return (await self.session.execute(select(func.count()).select_from(Member))).scalar()


class MemberImportRulesTest(_Base):
    async def test_duplicate_names_are_skipped(self) -> None:
        """同一帮会内重名跳过：第二次导入 imported=0、skipped=全部。"""
        rows = [("重名甲", "铁衣", None, "formal", None), ("重名乙", "素问", None, "formal", None)]
        first = await import_members(self.session, 1, _xlsx_with_rows(rows))
        self.assertEqual(first["imported"], 2)
        self.assertEqual(await self._count(), 2)
        second = await import_members(self.session, 1, _xlsx_with_rows(rows))
        self.assertEqual(second["imported"], 0, "重名不应重复入库")
        self.assertEqual(second["skipped"], 2)
        self.assertEqual(await self._count(), 2, "成员总数不得增长")

    async def test_existing_member_name_is_skipped_even_if_not_in_file(self) -> None:
        """与库中已有成员同名（但不在本次文件里）也跳过。"""
        self.session.add(Member(guild_id=1, name="库里已有", main_profession="铁衣"))
        await self.session.commit()
        result = await import_members(self.session, 1, _xlsx_with_rows([("库里已有", "铁衣", None, "formal", None)]))
        self.assertEqual(result["imported"], 0)
        self.assertEqual(result["skipped"], 1)
        self.assertEqual(await self._count(), 1)

    async def test_invalid_rows_are_reported_and_skipped(self) -> None:
        """无效职业与超长姓名计入 errors 且按跳过处理（实现语义，import_members 返回 errors）。"""
        rows = [
            ("正常甲", "铁衣", None, "formal", None),
            ("错职业", "不存在的职业", None, "formal", None),
            ("超长" * 20, "铁衣", None, "formal", None),
        ]
        result = await import_members(self.session, 1, _xlsx_with_rows(rows))
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["skipped"], 2)
        self.assertEqual(len(result["errors"]), 2)
        self.assertEqual(await self._count(), 1)

    async def test_row_cap_boundary(self) -> None:
        """边界：正好 5000 行可导入，第 5001 行被拒绝（security-review 威胁核对表第 10 行）。

        实现为准：`_parse_workbook` 在**追加之前**判 `len(data_rows) >= MAX_IMPORT_ROWS`，
        故额外一次导入到第 5001 行时报错——即上限为「最多 5000 行」。
        """
        exactly = [(f"成员{i}", "铁衣", None, "formal", None) for i in range(MAX_IMPORT_ROWS)]
        result = await import_members(self.session, 1, _xlsx_with_rows(exactly))
        self.assertEqual(result["imported"], MAX_IMPORT_ROWS, "5000 行应被接受")
        self.assertEqual(await self._count(), MAX_IMPORT_ROWS)

        overflow = [(f"溢出{i}", "铁衣", None, "formal", None) for i in range(MAX_IMPORT_ROWS + 1)]
        with self.assertRaises(ExcelImportError):
            await import_members(self.session, 1, _xlsx_with_rows(overflow))

    async def test_extension_must_be_xlsx(self) -> None:
        """端点只接受 .xlsx（扩展名校验先于解析）。"""
        from starlette.datastructures import UploadFile

        upload = UploadFile(file=BytesIO(b"not a workbook"), filename="members.csv")
        with self.assertRaises(ExcelImportError):
            await import_excel(file=upload, current_user=SimpleNamespace(guild_id=1), session=self.session)

    async def test_declared_size_over_limit_is_rejected(self) -> None:
        """.size > 5MB（声明长度）直接拒绝，不进入解析。"""
        from starlette.datastructures import UploadFile

        upload = UploadFile(file=BytesIO(b"x"), filename="members.xlsx", size=MAX_FILE_SIZE + 1)
        with self.assertRaises(ExcelImportError):
            await import_excel(file=upload, current_user=SimpleNamespace(guild_id=1), session=self.session)

    async def test_actual_size_over_limit_is_rejected(self) -> None:
        """声明缺失时，读取后二次兜底仍拒绝（Content-Length 可能缺失或伪造）。"""
        from starlette.datastructures import UploadFile

        payload = b"0" * (MAX_FILE_SIZE + 1)
        upload = UploadFile(file=BytesIO(payload), filename="members.xlsx")
        with self.assertRaises(ExcelImportError):
            await import_excel(file=upload, current_user=SimpleNamespace(guild_id=1), session=self.session)

    async def test_valid_file_imports_through_endpoint(self) -> None:
        """正向：合法文件经端点导入成功并返回统计。"""
        from starlette.datastructures import UploadFile

        blob = build_members_xlsx([Member(guild_id=1, name="端点甲", main_profession="铁衣")], "上限测试帮会", 1)
        upload = UploadFile(file=BytesIO(blob), filename="members.xlsx", size=len(blob))
        result = await import_excel(file=upload, current_user=SimpleNamespace(guild_id=1), session=self.session)
        self.assertEqual(result["imported"], 1)
        self.assertEqual(await self._count(), 1)


if __name__ == "__main__":
    unittest.main()

# -*- coding: utf-8 -*-
"""编外成员状态回归：统计口径、多状态导出、Excel 回环与出勤候选边界。"""

from __future__ import annotations

import unittest
from datetime import UTC, datetime
from io import BytesIO

from openpyxl import load_workbook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.guild import Guild
from app.models.member import Member
from app.models.schedule import Schedule
from app.services import member_service
from app.utils import attendance_import
from app.utils.excel_export import build_members_xlsx
from app.utils.excel_import import _parse_status, import_members


class _Member:
    """Excel 导出只读取这些属性（轻量替身，避免依赖 ORM）。"""

    def __init__(self, name: str, status: str = "formal", main_profession: str = "铁衣") -> None:
        self.name = name
        self.status = status
        self.main_profession = main_profession
        self.sub_profession = None
        self.remark = None


class ExcelExternalTests(unittest.TestCase):
    def test_status_labels_and_order(self) -> None:
        blob = build_members_xlsx(
            [_Member("编外甲", "external"), _Member("替补乙", "substitute"), _Member("正式丙", "formal")],
            "测试帮会",
            1,
        )
        workbook = load_workbook(BytesIO(blob))
        try:
            sheet = workbook[workbook.sheetnames[0]]
            self.assertEqual(
                [sheet.cell(row=row, column=1).value for row in (3, 4, 5)],
                ["正式丙", "替补乙", "编外甲"],
            )
            self.assertEqual(
                [sheet.cell(row=row, column=4).value for row in (3, 4, 5)],
                ["正式", "替补", "编外"],
            )
        finally:
            workbook.close()

    def test_parse_status_accepts_external(self) -> None:
        self.assertEqual(_parse_status("编外"), "external")
        self.assertEqual(_parse_status("external"), "external")
        self.assertEqual(_parse_status("2"), "external")


class MemberExternalServiceTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)()
        self.guild = Guild(name="编外测试帮会")
        self.session.add(self.guild)
        await self.session.flush()
        self.gid = self.guild.id
        schedule = Schedule(guild_id=self.gid, opponent="对手", match_time=datetime.now(UTC), rounds=1)
        self.session.add(schedule)
        await self.session.flush()
        self.sid = schedule.id
        self.formal = Member(guild_id=self.gid, name="正式甲", main_profession="铁衣", status="formal")
        self.substitute = Member(guild_id=self.gid, name="替补乙", main_profession="素问", status="substitute")
        self.external = Member(guild_id=self.gid, name="编外丙", main_profession="九灵", status="external")
        self.session.add_all([self.formal, self.substitute, self.external])
        await self.session.commit()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def test_list_stats_include_external(self) -> None:
        _, total, stats = await member_service.list_members(self.session, self.gid, 1, 20)
        self.assertEqual(total, 3)
        self.assertEqual(stats, {"formal_count": 1, "substitute_count": 1, "external_count": 1})

    async def test_profession_filter_counts_by_actual_status(self) -> None:
        self.formal.sub_profession = "素问"
        await self.session.commit()
        _, total, stats = await member_service.list_members(self.session, self.gid, 1, 20, profession="素问")
        self.assertEqual(total, 2)
        self.assertEqual(stats, {"formal_count": 1, "substitute_count": 1, "external_count": 0})

    async def test_export_filters_by_multiple_statuses(self) -> None:
        only_external = await member_service.export_members(self.session, self.gid, statuses=["external"])
        self.assertEqual([m.name for m in only_external], ["编外丙"])
        two_types = await member_service.export_members(self.session, self.gid, statuses=["formal", "external"])
        self.assertEqual({m.name for m in two_types}, {"正式甲", "编外丙"})
        with self.assertRaises(member_service.MemberServiceError):
            await member_service.export_members(self.session, self.gid, statuses=["not-a-status"])

    async def test_attendance_import_respects_external_rules(self) -> None:
        formal_result = await attendance_import.import_formal(self.session, self.gid, self.sid)
        self.assertEqual(formal_result["imported"], 1, "一键导入正式不应包含编外")
        candidates = await attendance_import.substitute_candidates(self.session, self.gid, self.sid)
        self.assertEqual({m.name for m in candidates}, {"替补乙"}, "替补候选不应包含编外")
        all_candidates = await attendance_import.all_member_candidates(self.session, self.gid, self.sid)
        self.assertEqual({m.name for m in all_candidates}, {"替补乙", "编外丙"}, "全量导入候选应包含编外")
        external_result = await attendance_import.import_members(self.session, self.gid, self.sid, [self.external.id])
        self.assertEqual(external_result["imported"], 1, "编外应可通过全量导入进入出勤库")
        rates = await member_service.attendance_rate(self.session, self.gid)
        self.assertIn(self.external.id, {item["member_id"] for item in rates}, "编外出勤率应照常统计")
        substitute_result = await attendance_import.import_substitutes(
            self.session, self.gid, self.sid, [self.external.id]
        )
        self.assertEqual(substitute_result["imported"], 0, "导入替补接口不应接收编外")

    async def test_excel_roundtrip_keeps_external(self) -> None:
        blob = build_members_xlsx([_Member("导出编外", status="external")], "测试帮会", self.gid)
        result = await import_members(self.session, self.gid, blob)
        self.assertEqual(result["imported"], 1)
        imported = (
            await self.session.execute(select(Member).where(Member.guild_id == self.gid, Member.name == "导出编外"))
        ).scalar_one()
        self.assertEqual(imported.status, "external")

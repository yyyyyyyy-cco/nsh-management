"""成员删除后历史排表保留与候选池标记的回归测试（2026-10-14）。

背景：删除成员时 detach_member 会置空其出勤记录的 member_id（F-78 防主键复用），
姓名快照仍留在出勤库。此前排表读取的惰性清理按 member_id 匹配，会把该成员从历史排表清空、
候选池又将其标记为「补」。本组用例锁定修复后的语义：
- 删除成员 → 读取排表：槽位转为补人形态保留（姓名与备注不丢，member_id 置空防主键复用）；
- 删除成员 → 候选池：member_status 标记 deleted（真补人 is_filler=True 仍为 filler）；
- 出勤库记录被移除（无姓名快照）→ 槽位仍照旧清空（原语义不回退）；
- 删除后读取的排表可直接重新保存（补人形态通过 save_lineup 校验）；
- 补人/快照槽位的出勤记录被删除（姓名在本场出勤库完全不存在）→ 槽位同步清空（与正式成员口径统一）。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from support import DbTestCase

from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.member import Member
from app.models.schedule import Schedule
from app.services import attendance_service, lineup_service, member_service
from app.services.lineup_attendance import candidate_pool
from app.utils.lineup_structure import empty_lineup_data


class LineupMemberDeleteTest(DbTestCase):
    """公共场景：帮会 + 成员「张三」已排入 s1 第 0 队第 0 槽并出勤 normal。"""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.guild = Guild(name="排表删除测试帮会")
        self.session.add(self.guild)
        await self.session.flush()
        self.gid = self.guild.id
        self.member = Member(guild_id=self.gid, name="张三", main_profession="铁衣", status="formal")
        self.session.add(self.member)
        await self.session.flush()
        self.mid = self.member.id
        self.schedule = Schedule(
            guild_id=self.gid, opponent="对手甲", match_time=datetime(2026, 10, 1, 20, 0), rounds=1
        )
        self.session.add(self.schedule)
        await self.session.flush()
        self.session.add(
            AttendanceRecord(
                schedule_id=self.schedule.id, member_id=self.mid, member_name="张三", profession="铁衣", status="normal"
            )
        )
        data = empty_lineup_data()
        data[0]["slots"][0] = {"slot_index": 0, "member_id": self.mid, "member_name": "张三", "remark": "主T"}
        self.session.add(Lineup(schedule_id=self.schedule.id, data=data, title_remark="", groups_remark={}))
        await self.session.commit()

    async def _stored_slot(self) -> dict:
        data = (
            await self.session.execute(select(Lineup.data).where(Lineup.schedule_id == self.schedule.id))
        ).scalar_one()
        return data[0]["slots"][0]

    async def test_deleted_member_slot_kept_as_filler_snapshot(self) -> None:
        """删除成员后读取排表：槽位保留姓名与备注（补人形态），不再整槽清空。"""
        await member_service.delete_member(self.session, self.gid, self.mid)
        lineup = await lineup_service.get_lineup(self.session, self.gid, self.schedule.id)
        slot = lineup.data[0]["slots"][0]
        self.assertIsNone(slot["member_id"], "悬空 member_id 应置空（防主键复用）")
        self.assertEqual(slot["member_name"], "张三", "历史排表应保留姓名快照")
        self.assertEqual(slot["remark"], "主T", "槽位备注应保留")
        stored = await self._stored_slot()
        self.assertEqual((stored["member_id"], stored["member_name"]), (None, "张三"), "清理结果应已落库")

    async def test_candidate_pool_marks_deleted_member(self) -> None:
        """删除成员后:候选池标记 deleted；真补人仍为 filler；正常成员仍为 formal。"""
        other = Member(guild_id=self.gid, name="李四", main_profession="素问", status="substitute")
        self.session.add(other)
        await self.session.flush()
        self.session.add_all(
            [
                AttendanceRecord(
                    schedule_id=self.schedule.id,
                    member_id=other.id,
                    member_name="李四",
                    profession="素问",
                    status="normal",
                ),
                AttendanceRecord(
                    schedule_id=self.schedule.id,
                    member_id=None,
                    member_name="散人甲",
                    profession="素问",
                    status="normal",
                    is_filler=True,
                ),
            ]
        )
        await self.session.commit()
        await member_service.delete_member(self.session, self.gid, self.mid)

        pool = await candidate_pool(self.session, self.gid, self.schedule.id)
        by_name = {p["member_name"]: p for p in pool}
        self.assertEqual(by_name["张三"]["member_status"], "deleted", "已删除成员的历史快照应标记 deleted")
        self.assertIsNone(by_name["张三"]["member_id"])
        self.assertEqual(by_name["散人甲"]["member_status"], "filler", "真补人（is_filler=True）仍为 filler")
        self.assertEqual(by_name["李四"]["member_status"], "substitute", "在库成员仍取常驻库状态")

    async def test_purge_still_clears_without_name_snapshot(self) -> None:
        """出勤库记录被移除（无姓名快照残留）时，槽位仍照旧清空（原语义不回退）。"""
        record = (await self.session.execute(select(AttendanceRecord))).scalars().one()
        await self.session.delete(record)
        await self.session.commit()

        lineup = await lineup_service.get_lineup(self.session, self.gid, self.schedule.id)
        slot = lineup.data[0]["slots"][0]
        self.assertIsNone(slot["member_id"])
        self.assertEqual(slot["member_name"], "", "无姓名快照的失效槽位应清空")

    async def test_save_after_delete_accepts_snapshot_slot(self) -> None:
        """删除后读取的排表（槽位已是补人形态）可直接重新保存，不触发成员归属校验报错。"""
        await member_service.delete_member(self.session, self.gid, self.mid)
        lineup = await lineup_service.get_lineup(self.session, self.gid, self.schedule.id)
        saved = await lineup_service.save_lineup(self.session, self.gid, self.schedule.id, lineup.data)
        slot = saved.data[0]["slots"][0]
        self.assertEqual((slot["member_id"], slot["member_name"]), (None, "张三"))

    async def test_snapshot_slot_cleared_after_attendance_deleted(self) -> None:
        """用户报告场景：删常驻库 → 打开排表（转补人形态）→ 删出勤记录 → 排表同步清空（不再残留无职业槽位）。"""
        await member_service.delete_member(self.session, self.gid, self.mid)
        lineup = await lineup_service.get_lineup(self.session, self.gid, self.schedule.id)
        self.assertEqual(lineup.data[0]["slots"][0]["member_name"], "张三", "前置：转补人形态保留姓名")

        record = (await self.session.execute(select(AttendanceRecord))).scalars().one()
        await attendance_service.delete_record(self.session, self.gid, self.schedule.id, record.id)

        lineup = await lineup_service.get_lineup(self.session, self.gid, self.schedule.id)
        slot = lineup.data[0]["slots"][0]
        self.assertEqual(slot["member_name"], "", "出勤记录被删除后，补人/快照槽位应同步清空")
        stored = await self._stored_slot()
        self.assertEqual(stored["member_name"], "", "清理结果应已落库")

    async def test_filler_slot_cleared_after_attendance_deleted(self) -> None:
        """真补人槽位的出勤记录被删除（姓名在本场出勤库不存在）→ 槽位同步清空（与正式成员口径统一）。"""
        other = Schedule(guild_id=self.gid, opponent="对手乙", match_time=datetime(2026, 9, 20, 20, 0), rounds=1)
        self.session.add(other)
        await self.session.flush()
        filler = AttendanceRecord(
            schedule_id=other.id,
            member_id=None,
            member_name="补人乙",
            profession="素问",
            status="normal",
            is_filler=True,
        )
        data = empty_lineup_data()
        data[0]["slots"][0] = {"slot_index": 0, "member_id": None, "member_name": "补人乙", "remark": "临时"}
        self.session.add_all([filler, Lineup(schedule_id=other.id, data=data, title_remark="", groups_remark={})])
        await self.session.commit()

        await attendance_service.delete_record(self.session, self.gid, other.id, filler.id)
        lineup = await lineup_service.get_lineup(self.session, self.gid, other.id)
        slot = lineup.data[0]["slots"][0]
        self.assertEqual(slot["member_name"], "", "补人出勤记录被删除后，槽位应同步清空")
        self.assertEqual(slot["remark"], "临时", "清空仅移除姓名，槽位备注保留")

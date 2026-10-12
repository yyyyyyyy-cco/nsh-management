"""成员档案查询回归测试（design-member-archive.md §8.1）。

覆盖：三档案的排序与过滤语义、改名后按 member_id 仍可见（历史原文不变）、
删除成员的陈旧排表引用双条件过滤（防主键复用误关联，见 database-design §1.3）、
跨帮会 404、帮众 403、端点接线（require_admin）与空数据。
"""

from __future__ import annotations

import inspect
from datetime import datetime, timedelta
from types import SimpleNamespace

from fastapi import HTTPException
from sqlalchemy import select
from support import DbTestCase

from app.api.deps import require_admin
from app.api.v1 import member_archive as member_archive_api
from app.models.attendance import AttendanceRecord
from app.models.guild import Guild
from app.models.lineup import Lineup
from app.models.member import Member
from app.models.recording import Recording
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.member import MemberUpdate
from app.schemas.member_archive import AttendanceHistoryOut, LineupHistoryOut, RecordingHistoryOut
from app.services import member_archive_service, member_service
from app.services.member_service import MemberServiceError
from app.utils.lineup_structure import empty_lineup_data

CALLS = (
    member_archive_service.attendance_history,
    member_archive_service.recording_history,
    member_archive_service.lineup_history,
)


class ArchiveFixture(DbTestCase):
    """公共场景：1 个帮会 + 成员「甲」+ 2 场赛程（s2 较新）。"""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.guild = Guild(name="档案测试帮会")
        self.session.add(self.guild)
        await self.session.flush()
        self.gid = self.guild.id
        self.member = Member(guild_id=self.gid, name="甲", main_profession="铁衣", status="formal")
        self.session.add(self.member)
        await self.session.flush()
        self.mid = self.member.id
        base = datetime(2026, 10, 1, 20, 0)
        self.s1 = Schedule(guild_id=self.gid, opponent="战队一", match_time=base, rounds=1, result="win")
        self.s2 = Schedule(
            guild_id=self.gid, opponent="战队二", match_time=base + timedelta(days=2), rounds=2, result="lose"
        )
        self.session.add_all([self.s1, self.s2])
        await self.session.flush()

    def _lineup_with_member(self, category: str, team_index: int, slot_index: int, remark: str = "") -> list[dict]:
        """构造含成员「甲」的标准排表结构。"""
        data = empty_lineup_data()
        for team in data:
            if team["category"] == category and team["team_index"] == team_index:
                team["slots"][slot_index] = {
                    "slot_index": slot_index,
                    "member_id": self.mid,
                    "member_name": self.member.name,
                    "remark": remark,
                }
        return data

    async def _admin(self) -> User:
        user = User(
            guild_id=self.gid, username="op_admin", role="admin", password_hash="x", status="active", token_version=0
        )
        self.session.add(user)
        await self.session.flush()
        return user


class AttendanceHistoryTest(ArchiveFixture):
    async def test_rows_filter_and_order(self) -> None:
        other = Member(guild_id=self.gid, name="乙", main_profession="素问", status="formal")
        self.session.add(other)
        await self.session.flush()
        self.session.add_all(
            [
                AttendanceRecord(
                    schedule_id=self.s1.id,
                    member_id=self.mid,
                    member_name="甲",
                    profession="铁衣",
                    status="normal",
                    remark="主力",
                ),
                AttendanceRecord(
                    schedule_id=self.s2.id, member_id=self.mid, member_name="甲", profession="铁衣", status="leave"
                ),
                AttendanceRecord(
                    schedule_id=self.s1.id, member_id=other.id, member_name="乙", profession="素问", status="normal"
                ),
                # 补人行（同名但 member_id 为空）不得出现
                AttendanceRecord(
                    schedule_id=self.s1.id,
                    member_id=None,
                    member_name="甲",
                    profession="铁衣",
                    status="normal",
                    is_filler=True,
                ),
            ]
        )
        await self.session.commit()

        rows = await member_archive_service.attendance_history(self.session, self.gid, self.mid)
        self.assertEqual([r["schedule_id"] for r in rows], [self.s2.id, self.s1.id], "应按比赛时间倒序且只含本人")
        self.assertEqual((rows[1]["status"], rows[1]["remark"], rows[1]["schedule_result"]), ("normal", "主力", "win"))
        self.assertEqual(rows[0]["status"], "leave")

    async def test_cross_guild_member_returns_404(self) -> None:
        guild2 = Guild(name="别的帮会")
        self.session.add(guild2)
        await self.session.flush()
        stranger = Member(guild_id=guild2.id, name="丙", main_profession="铁衣", status="formal")
        self.session.add(stranger)
        await self.session.commit()
        for call in CALLS:
            with self.assertRaises(MemberServiceError) as ctx:
                await call(self.session, self.gid, stranger.id)
            self.assertEqual(ctx.exception.status_code, 404, f"{call.__name__} 跨帮会成员应 404")


class RecordingHistoryTest(ArchiveFixture):
    async def test_includes_unsubmitted_and_round_order(self) -> None:
        self.session.add_all(
            [
                Recording(
                    schedule_id=self.s1.id,
                    member_id=self.mid,
                    member_name="甲",
                    round_number=1,
                    url=None,
                    status="pending",
                ),
                Recording(
                    schedule_id=self.s2.id,
                    member_id=self.mid,
                    member_name="甲",
                    round_number=1,
                    url="https://b23.tv/x",
                    status="approved",
                    review_remark="通过",
                ),
                Recording(
                    schedule_id=self.s2.id,
                    member_id=self.mid,
                    member_name="甲",
                    round_number=2,
                    url=None,
                    status="pending",
                ),
            ]
        )
        await self.session.commit()

        rows = await member_archive_service.recording_history(self.session, self.gid, self.mid)
        self.assertEqual(
            [(r["schedule_id"], r["round_number"]) for r in rows],
            [(self.s2.id, 1), (self.s2.id, 2), (self.s1.id, 1)],
            "比赛时间倒序、同场局号升序",
        )
        self.assertIsNone(rows[1]["url"], "未提交行（url 为空）应返回")
        self.assertEqual((rows[0]["status"], rows[0]["review_remark"]), ("approved", "通过"))


class LineupHistoryTest(ArchiveFixture):
    async def test_positions_and_order(self) -> None:
        self.session.add_all(
            [
                Lineup(schedule_id=self.s1.id, data=self._lineup_with_member("进攻1", 0, 0, remark="主T")),
                Lineup(schedule_id=self.s2.id, data=self._lineup_with_member("防守1", 0, 5)),
                # 双条件过滤依赖「该场出勤库存在同 member_id」→ 补足出勤行
                AttendanceRecord(
                    schedule_id=self.s1.id, member_id=self.mid, member_name="甲", profession="铁衣", status="normal"
                ),
                AttendanceRecord(
                    schedule_id=self.s2.id, member_id=self.mid, member_name="甲", profession="铁衣", status="normal"
                ),
            ]
        )
        await self.session.commit()

        rows = await member_archive_service.lineup_history(self.session, self.gid, self.mid)
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["schedule_id"], self.s2.id, "应按比赛时间倒序")
        self.assertEqual((rows[0]["category"], rows[0]["team_index"], rows[0]["slot_index"]), ("防守1", 0, 5))
        self.assertIsNone(rows[0]["slot_remark"], "空备注应归一为 None")
        self.assertEqual((rows[1]["category"], rows[1]["slot_index"], rows[1]["slot_remark"]), ("进攻1", 0, "主T"))


class StaleReferenceTest(ArchiveFixture):
    async def test_stale_slot_filtered_after_delete_and_id_reuse(self) -> None:
        """删除成员后新成员复用同一 id：档案不得继承旧排表（双条件过滤兜底）。"""
        self.session.add_all(
            [
                Lineup(schedule_id=self.s1.id, data=self._lineup_with_member("进攻2", 1, 2)),
                AttendanceRecord(
                    schedule_id=self.s1.id, member_id=self.mid, member_name="甲", profession="铁衣", status="normal"
                ),
            ]
        )
        await self.session.commit()
        self.assertEqual(
            len(await member_archive_service.lineup_history(self.session, self.gid, self.mid)), 1, "删除前应可见"
        )

        await member_service.delete_member(self.session, self.gid, self.mid)  # detach 置空出勤/录屏引用
        newbie = Member(guild_id=self.gid, name="乙", main_profession="铁衣", status="formal")
        self.session.add(newbie)
        await self.session.commit()
        self.assertEqual(newbie.id, self.mid, "前置：删除最大 id 后新成员复用同一 id（SQLite 未启用 AUTOINCREMENT）")

        # 陈旧槽位仍在 JSON 中（D4 裁决：历史原文不主动清理）
        data_after = (
            await self.session.execute(select(Lineup.data).where(Lineup.schedule_id == self.s1.id))
        ).scalar_one()
        stale = [slot for team in data_after for slot in team["slots"] if slot.get("member_id") == self.mid]
        self.assertEqual(len(stale), 1, "排表 JSON 应保留陈旧 member_id（未主动清理）")

        rows = await member_archive_service.lineup_history(self.session, self.gid, newbie.id)
        self.assertEqual(rows, [], "新成员不得继承旧成员的排表历史（双条件过滤）")


class RenameTest(ArchiveFixture):
    async def test_histories_visible_by_member_id_after_rename(self) -> None:
        self.session.add_all(
            [
                AttendanceRecord(
                    schedule_id=self.s1.id, member_id=self.mid, member_name="甲", profession="铁衣", status="normal"
                ),
                Recording(
                    schedule_id=self.s1.id,
                    member_id=self.mid,
                    member_name="甲",
                    round_number=1,
                    url=None,
                    status="pending",
                ),
                Lineup(schedule_id=self.s1.id, data=self._lineup_with_member("进攻1", 0, 0)),
            ]
        )
        await self.session.commit()

        operator = await self._admin()
        await member_service.update_member(self.session, self.gid, self.mid, MemberUpdate(name="甲改名"), operator)

        results = [await call(self.session, self.gid, self.mid) for call in CALLS]
        self.assertEqual([len(r) for r in results], [1, 1, 1], "改名后按 member_id 仍应可见")
        snapshot = (
            await self.session.execute(
                select(AttendanceRecord.member_name).where(AttendanceRecord.schedule_id == self.s1.id)
            )
        ).scalar_one()
        self.assertEqual(snapshot, "甲", "历史姓名快照不随改名更新（原文不变）")


class PermissionAndWiringTest(ArchiveFixture):
    async def test_require_admin_denies_member_allows_admin(self) -> None:
        member_user = User(
            guild_id=self.gid, username="m1", role="member", password_hash="x", status="active", token_version=0
        )
        admin_user = await self._admin()
        with self.assertRaises(HTTPException) as ctx:
            await require_admin(member_user)
        self.assertEqual(ctx.exception.status_code, 403)
        self.assertEqual((await require_admin(admin_user)).username, "op_admin")

    async def test_endpoint_wiring_uses_require_admin(self) -> None:
        for fn in (
            member_archive_api.get_attendance_history,
            member_archive_api.get_recording_history,
            member_archive_api.get_lineup_history,
        ):
            dep = inspect.signature(fn).parameters["current_user"].default
            self.assertIs(dep.dependency, require_admin, f"{fn.__name__} 应挂 require_admin 依赖")

    async def test_endpoint_functions_typed_rows_and_empty(self) -> None:
        user = SimpleNamespace(guild_id=self.gid)  # 端点只读取 guild_id（参照既有自检风格）
        # 空数据：三个端点均返回空列表
        for fn in (
            member_archive_api.get_attendance_history,
            member_archive_api.get_recording_history,
            member_archive_api.get_lineup_history,
        ):
            self.assertEqual(await fn(self.mid, current_user=user, session=self.session), [])
        # 成员不存在（非本帮会 / 幽灵 id）→ 404 业务错误
        with self.assertRaises(MemberServiceError):
            await member_archive_api.get_attendance_history(9999, current_user=user, session=self.session)

        # 有数据：返回 Pydantic 模型实例
        self.session.add_all(
            [
                AttendanceRecord(
                    schedule_id=self.s1.id, member_id=self.mid, member_name="甲", profession="铁衣", status="normal"
                ),
                Recording(
                    schedule_id=self.s1.id,
                    member_id=self.mid,
                    member_name="甲",
                    round_number=1,
                    url=None,
                    status="pending",
                ),
                Lineup(schedule_id=self.s1.id, data=self._lineup_with_member("进攻1", 0, 0)),
            ]
        )
        await self.session.commit()
        att = await member_archive_api.get_attendance_history(self.mid, current_user=user, session=self.session)
        rec = await member_archive_api.get_recording_history(self.mid, current_user=user, session=self.session)
        lin = await member_archive_api.get_lineup_history(self.mid, current_user=user, session=self.session)
        self.assertIsInstance(att[0], AttendanceHistoryOut)
        self.assertIsInstance(rec[0], RecordingHistoryOut)
        self.assertIsInstance(lin[0], LineupHistoryOut)

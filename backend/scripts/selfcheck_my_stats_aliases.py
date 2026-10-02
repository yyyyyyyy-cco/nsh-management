"""个人战绩新旧 ID 关联回归：真实 JWT + ASGI 路由，仅用内存库。

运行：backend/.venv/Scripts/python.exe backend/scripts/selfcheck_my_stats_aliases.py
覆盖：合并/精确模式、连续改名与改回、新名无数据、可检测冲突（当前重名 / 他人批准记录 /
失效引用 / 同局双名）、冲突在最近 10 场之外仍被发现、跨帮会隔离、候选补全、最近 10 场截取。
"""
# ---- 前置依赖探测（缺依赖时模块级跳过；见合规化计划 W2-2 与本文件被 pytest 收集的约定）----
import unittest as _unittest

try:  # noqa: SIM105
    import fastapi  # noqa: F401
    import sqlalchemy  # noqa: F401
except ImportError as _exc:  # pragma: no cover - 无依赖环境（如 Python 3.14 装不上 pydantic-core）
    raise _unittest.SkipTest(f"缺少运行依赖（FastAPI/SQLAlchemy），跳过本模块：{_exc}") from _exc

import json
import sys
import unittest
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.parse import urlencode

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.api.v1 import my_stats
from app.core.database import Base, get_db
from app.core.security import create_access_token
from app.models.game_id_request import MemberGameIdRequest
from app.models.guild import Guild
from app.models.match_data import MatchData
from app.models.member import Member
from app.models.schedule import Schedule
from app.models.user import User
from app.schemas.member import MemberUpdate
from app.services.member_service import update_member
from app.services.player_identity_service import PlayerIdentityError

BASE_TIME = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


class MyStatsAliasTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.session = async_sessionmaker(self.engine, expire_on_commit=False)()
        self.session.add_all([Guild(id=1, name="帮会甲"), Guild(id=2, name="帮会乙")])
        await self.session.flush()
        self.tokens = {}
        for uid, role, gid in [(1, "admin", 1), (2, "developer", None), (3, "member", 1)]:
            user = User(id=uid, username=f"actor{uid}", role=role, guild_id=gid, password_hash="unused")
            self.session.add(user)
            self.tokens[uid] = None
        await self.session.commit()
        for uid in self.tokens:
            user = await self.session.get(User, uid)
            self.tokens[uid] = create_access_token(user.id, user.role, user.token_version)

        self.app = FastAPI()
        self.app.include_router(my_stats.router)

        async def session_override():
            yield self.session

        async def conflict_error(request, exc):
            return JSONResponse({"message": exc.message}, status_code=exc.status_code)

        self.app.dependency_overrides[get_db] = session_override
        self.app.add_exception_handler(PlayerIdentityError, conflict_error)
        self._member_seq = 100
        self._request_seq = 100

    async def asyncTearDown(self):
        await self.session.close()
        await self.engine.dispose()

    # ---- 造数工具 ----

    async def add_member(self, name: str, guild_id: int = 1, profession: str = "神相") -> Member:
        self._member_seq += 1
        member = Member(id=self._member_seq, guild_id=guild_id, name=name, main_profession=profession, status="formal")
        self.session.add(member)
        await self.session.flush()
        return member

    async def add_approved(self, member_id: int | None, old_game_id: str, new_game_id: str, guild_id: int = 1) -> None:
        """直接写入已通过申请（模拟审核完成后的关联依据）。"""
        self._request_seq += 1
        self.session.add(
            MemberGameIdRequest(
                id=self._request_seq,
                guild_id=guild_id,
                member_id=member_id,
                old_game_id=old_game_id,
                new_game_id=new_game_id,
                requester_username="setup",
                status="approved",
                reviewer_username="setup",
                reviewed_at=BASE_TIME,
            )
        )
        await self.session.flush()

    async def add_schedule(self, days: int, guild_id: int = 1, rounds: int = 1) -> Schedule:
        schedule = Schedule(
            guild_id=guild_id,
            opponent=f"对手{days}",
            match_time=BASE_TIME + timedelta(days=days),
            rounds=rounds,
            result="win",
        )
        self.session.add(schedule)
        await self.session.flush()
        return schedule

    async def add_record(self, schedule_id: int, name: str, round_no: int = 1, camp: str = "我方", **overrides) -> None:
        data = dict(
            schedule_id=schedule_id, round_no=round_no, player_name=name, profession="神相", camp=camp,
            kills=10, springs=1, assists=5, resource=0, player_damage=1000, armor_break_damage=0,
            building_damage=100, tower_break_damage=0, healing=0, damage_taken=500, deaths=1,
            revives=0, fen_gu=0,
        )
        data.update(overrides)
        self.session.add(MatchData(**data))
        await self.session.flush()

    async def get_stats(self, name: str, merge: bool = True, actor: int = 3):
        query = urlencode({"player_name": name, "merge_aliases": str(merge).lower()})
        return await self.request("GET", f"/my-stats?{query}", actor=actor)

    async def request(self, method, path, actor=3):
        pure_path, _, query = path.partition("?")
        headers = [(b"content-type", b"application/json")]
        if actor is not None:
            headers.append((b"authorization", f"Bearer {self.tokens[actor]}".encode()))
        scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1",
                 "method": method, "scheme": "http", "path": pure_path, "raw_path": pure_path.encode(),
                 "query_string": query.encode(), "root_path": "", "headers": headers,
                 "server": ("test", 80), "client": ("127.0.0.1", 1)}
        events = []

        async def receive():
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message):
            events.append(message)

        await self.app(scope, receive, send)
        status = next(e["status"] for e in events if e["type"] == "http.response.start")
        content = b"".join(e.get("body", b"") for e in events if e["type"] == "http.response.body")
        return status, json.loads(content) if content else {}

    # ---- 合并与精确 ----

    async def test_merge_basic_and_exact(self):
        member = await self.add_member("乙")
        await self.add_approved(member.id, "甲", "乙")
        await self.add_member("甲", guild_id=2)  # 外帮会同名不得触发冲突
        s1 = await self.add_schedule(1, rounds=2)
        s2 = await self.add_schedule(2)
        await self.add_record(s1.id, "甲", 1)
        await self.add_record(s1.id, "甲", 2)
        await self.add_record(s1.id, "队友", 1)
        await self.add_record(s2.id, "乙", 1)
        await self.session.commit()

        status, old_view = await self.get_stats("甲")
        self.assertEqual(status, 200)
        self.assertEqual(old_view["identity"]["mode"], "merged")
        self.assertEqual(old_view["identity"]["member_id"], member.id)
        self.assertEqual(old_view["identity"]["current_game_id"], "乙")
        self.assertEqual(old_view["identity"]["aliases"], ["乙", "甲"])
        self.assertEqual(old_view["summary"]["player_name"], "乙")
        self.assertEqual(len(old_view["records"]), 3)
        self.assertEqual({r["player_name"] for r in old_view["records"]}, {"甲", "乙"})
        # 该局排名分母仍为该局全部记录（甲 + 队友）
        first_round = [r for r in old_view["records"] if r["round_no"] == 1 and r["player_name"] == "甲"][0]
        self.assertEqual(first_round["rankings"][0]["total"], 2)

        status, new_view = await self.get_stats("乙")
        self.assertEqual(status, 200)
        self.assertEqual(
            [r["player_name"] for r in new_view["records"]],
            [r["player_name"] for r in old_view["records"]],
        )

        status, exact = await self.get_stats("甲", merge=False)
        self.assertEqual(status, 200)
        self.assertEqual(exact["identity"]["mode"], "exact")
        self.assertIsNone(exact["identity"]["member_id"])
        self.assertEqual(exact["identity"]["aliases"], ["甲"])
        self.assertEqual(len(exact["records"]), 2)
        self.assertEqual(exact["summary"]["player_name"], "甲")

    async def test_chain_and_rename_back(self):
        member = await self.add_member("戊")
        await self.add_approved(member.id, "丙", "丁")
        await self.add_approved(member.id, "丁", "戊")
        await self.add_approved(member.id, "戊", "丙")
        member.name = "丙"  # 改回旧名后仍应保留全部关联
        s = await self.add_schedule(1)
        await self.add_record(s.id, "丁", 1)
        await self.session.commit()

        for name in ("丙", "丁", "戊"):
            status, data = await self.get_stats(name)
            self.assertEqual(status, 200, name)
            self.assertEqual(sorted(data["identity"]["aliases"]), sorted(["丙", "丁", "戊"]), name)
            self.assertEqual(len(data["records"]), 1, name)

    async def test_identity_for_new_name_without_data(self):
        member = await self.add_member("庚")
        await self.add_approved(member.id, "己", "庚")
        s = await self.add_schedule(1)
        await self.add_record(s.id, "己", 1)
        await self.session.commit()

        status, data = await self.get_stats("庚")
        self.assertEqual(status, 200)
        self.assertEqual(data["identity"]["mode"], "merged")
        self.assertEqual(len(data["records"]), 1)
        # 新名本身无比赛数据也能作为候选出现
        status, names = await self.request("GET", "/my-stats/player-names?q=%E5%BA%9A")
        self.assertIn("庚", names["names"])
        self.assertIn("己", names["names"])

    async def test_admin_direct_rename_records_alias(self):
        """管理员直接在常驻库改名：自动记录一条已确认关联，旧名与新名均可查询合并战绩。"""
        member = await self.add_member("子")
        s = await self.add_schedule(1)
        await self.add_record(s.id, "子", 1)
        await self.session.commit()

        operator = await self.session.get(User, 1)
        await update_member(self.session, 1, member.id, MemberUpdate(name="丑"), operator)

        for name in ("子", "丑"):
            status, data = await self.get_stats(name)
            self.assertEqual(status, 200, name)
            self.assertEqual(data["identity"]["mode"], "merged", name)
            self.assertEqual(sorted(data["identity"]["aliases"]), sorted(["子", "丑"]), name)
            self.assertEqual(len(data["records"]), 1, name)

        # 自动记录：approved + 操作管理员快照 + 备注标注来源
        record = (
            await self.session.execute(
                select(MemberGameIdRequest).where(MemberGameIdRequest.new_game_id == "丑")
            )
        ).scalar_one()
        self.assertEqual((record.status, record.old_game_id), ("approved", "子"))
        self.assertEqual((record.requester_username, record.reviewer_username), ("actor1", "actor1"))
        self.assertIsNotNone(record.reviewed_at)
        self.assertTrue(record.review_remark)

    async def test_recent_ten_across_aliases(self):
        member = await self.add_member("未")
        await self.add_approved(member.id, "午", "未")
        for days in range(1, 13):
            schedule = await self.add_schedule(days)
            await self.add_record(schedule.id, "午" if days % 2 else "未", 1)
        await self.session.commit()

        status, data = await self.get_stats("未")
        self.assertEqual(status, 200)
        self.assertEqual(len(data["records"]), 10)  # 整体取最近 10 场，而非每个名称各 10 场
        opponents = {r["opponent"] for r in data["records"]}
        self.assertNotIn("对手1", opponents)
        self.assertNotIn("对手2", opponents)

    async def test_unknown_player_and_developer_denied(self):
        status, data = await self.get_stats("无名氏")
        self.assertEqual(status, 200)
        self.assertEqual((data["identity"]["mode"], data["records"]), ("exact", []))
        status, _ = await self.get_stats("甲", actor=2)
        self.assertEqual(status, 403)
        status, _ = await self.request("GET", "/my-stats/player-names?q=%E7%94%B2", actor=2)
        self.assertEqual(status, 403)

    # ---- 冲突（一律 409，精确模式仍可用） ----

    async def _assert_conflict(self, name: str):
        status, data = await self.get_stats(name)
        self.assertEqual(status, 409, name)
        self.assertIn("仅查此 ID", data["message"])
        status, exact = await self.get_stats(name, merge=False)
        self.assertEqual((status, exact["identity"]["mode"]), (200, "exact"))

    async def test_conflict_current_member_occupies_alias(self):
        member = await self.add_member("壬")
        await self.add_approved(member.id, "辛", "壬")
        await self.add_member("辛")  # 另一成员占用了历史名
        await self.session.commit()
        await self._assert_conflict("壬")
        await self._assert_conflict("辛")

    async def test_conflict_other_member_approved_record(self):
        member = await self.add_member("子")
        await self.add_approved(member.id, "癸", "子")
        other = await self.add_member("丑")
        await self.add_approved(other.id, "癸", "丑")  # 他人批准记录与集合重叠
        await self.session.commit()
        await self._assert_conflict("子")
        await self._assert_conflict("癸")

    async def test_conflict_detached_member_evidence(self):
        member = await self.add_member("卯")
        await self.add_approved(member.id, "寅", "卯")
        await self.add_approved(None, "寅", "寅旧")  # 成员已删除后留下的失效引用
        await self.session.commit()
        await self._assert_conflict("卯")
        await self._assert_conflict("寅")

    async def test_conflict_same_round_two_names_beyond_recent_ten(self):
        member = await self.add_member("巳")
        await self.add_approved(member.id, "辰", "巳")
        oldest = await self.add_schedule(1)
        await self.add_record(oldest.id, "辰", 1)
        await self.add_record(oldest.id, "巳", 1)  # 同一场同一局出现两个关联名称
        for days in range(2, 13):
            schedule = await self.add_schedule(days)
            await self.add_record(schedule.id, "巳", 1)
        await self.session.commit()
        await self._assert_conflict("巳")


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""职业目录（professions）规则测试：创建/停用/改名级联/旧值豁免/导入与路由守卫。

背景：职业清单自 2026-10 起由数据库维护（`.agent/plans/profession-catalog-plan.md` §2/§3）。
本文件锁定以下语义：
- 创建：名称含停用职业全局唯一；排序缺省追加末位；颜色缺省主色；
- 停用：不提供物理删除；「至少保留一个启用职业」由服务层守卫；
- 改名级联仅活跃数据（成员/职业配置/单场覆盖），历史快照（出勤/比赛数据）保持原名；
- 旧值豁免：与现值相同的职业允许为停用（成员更新/出勤记录/单场覆盖均可继续编辑）；
- Excel 导入拒绝停用职业；`/professions` 写操作仅开发者（路由守卫）。
"""

from __future__ import annotations

from datetime import UTC, datetime
from io import BytesIO

from openpyxl import Workbook
from sqlalchemy import select
from support import PROFESSION_SEED, DbTestCase

from app.api import deps
from app.models.attendance import AttendanceRecord
from app.models.match_data import MatchData
from app.models.member import Member
from app.models.profession import Profession, ProfessionConfig
from app.models.schedule import Schedule
from app.schemas.member import MemberCreate, MemberUpdate
from app.schemas.profession import ProfessionCreate, ProfessionUpdate
from app.services import attendance_service, member_service, profession_service, schedule_service
from app.services.profession_service import ProfessionServiceError
from app.utils.excel_import import import_members


def _xlsx_with_rows(rows: list[tuple]) -> bytes:
    """按导出格式（含来源行）生成工作簿字节。"""
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["所属帮会", "测试帮会", "帮会ID", 1, "仅作来源标识，非防伪凭证"])
    sheet.append(["姓名", "主职业", "副职业", "状态", "备注"])
    for row in rows:
        sheet.append(list(row))
    buffer = BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


class ProfessionCatalogServiceTest(DbTestCase):
    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.users = await self.seed_users()  # 帮会 id=1 + 角色矩阵账号
        self.operator = self.users[1]

    async def _create(self, name: str, **kwargs) -> Profession:
        return await profession_service.create_profession(self.session, ProfessionCreate(name=name, **kwargs))

    async def _deactivate(self, name: str) -> Profession:
        profession = (await self.session.execute(select(Profession).where(Profession.name == name))).scalar_one()
        return await profession_service.update_profession(
            self.session, profession.id, ProfessionUpdate(is_active=False)
        )

    async def _create_member(self, name: str, main: str, sub: str | None = None) -> Member:
        return await member_service.create_member(
            self.session, 1, MemberCreate(name=name, main_profession=main, sub_profession=sub)
        )

    async def test_list_orders_by_sort_order(self) -> None:
        """目录列表按 (sort_order, id) 升序，与种子顺序一致。"""
        items = await profession_service.list_professions(self.session)
        self.assertEqual([p.name for p in items], [name for name, _, _ in PROFESSION_SEED])

    async def test_create_defaults_and_uniqueness(self) -> None:
        """排序缺省追加末位、颜色缺省主色；名称含停用职业全局唯一。"""
        created = await self._create("新职业甲")
        self.assertEqual(created.sort_order, len(PROFESSION_SEED) + 1)
        self.assertEqual(created.color, "#c9a13b")
        self.assertTrue(created.is_active)
        with self.assertRaises(ProfessionServiceError):
            await self._create("新职业甲")
        await self.session.rollback()
        await self._deactivate("新职业甲")
        with self.assertRaises(ProfessionServiceError):
            await self._create("新职业甲")  # 停用后仍不可重名
        await self.session.rollback()

    async def test_last_active_profession_guard(self) -> None:
        """至少保留一个启用职业：逐个停用后，最后一个被拒绝。"""
        names = [name for name, _, _ in PROFESSION_SEED]
        for name in names[:-1]:
            await self._deactivate(name)
        with self.assertRaises(ProfessionServiceError):
            await self._deactivate(names[-1])
        await self.session.rollback()

    async def test_rename_cascades_active_data_only(self) -> None:
        """改名级联：成员/职业配置/单场覆盖更新；出勤与比赛数据快照保持原名。"""
        member = await self._create_member("甲", "铁衣", "素问")
        self.session.add(ProfessionConfig(guild_id=1, profession="铁衣", target_count=3))
        schedule = Schedule(
            guild_id=1,
            opponent="对手",
            match_time=datetime.now(UTC),
            rounds=1,
            profession_config={"铁衣": 5, "素问": 2},
        )
        self.session.add(schedule)
        await self.session.flush()
        attendance = AttendanceRecord(
            schedule_id=schedule.id, member_id=member.id, member_name="甲", profession="铁衣", status="normal"
        )
        match_row = MatchData(schedule_id=schedule.id, player_name="甲", profession="铁衣", camp="我方")
        self.session.add_all([attendance, match_row])
        await self.session.commit()

        profession = (await self.session.execute(select(Profession).where(Profession.name == "铁衣"))).scalar_one()
        await profession_service.update_profession(self.session, profession.id, ProfessionUpdate(name="铁衣·改"))

        await self.session.refresh(member)
        self.assertEqual(member.main_profession, "铁衣·改")
        config = (
            (await self.session.execute(select(ProfessionConfig).where(ProfessionConfig.guild_id == 1))).scalars().one()
        )
        self.assertEqual(config.profession, "铁衣·改")
        await self.session.refresh(schedule)
        self.assertEqual(schedule.profession_config, {"铁衣·改": 5, "素问": 2})
        await self.session.refresh(attendance)
        self.assertEqual(attendance.profession, "铁衣", "出勤快照保持原名")
        await self.session.refresh(match_row)
        self.assertEqual(match_row.profession, "铁衣", "比赛数据快照保持原名")

    async def test_rename_conflicts_rejected(self) -> None:
        """目标名与既有职业（含停用）或职业配置行冲突时拒绝。"""
        created = await self._create("待改名甲")
        created_id = created.id  # rollback 会过期 ORM 实例：ID 提前取出
        with self.assertRaises(ProfessionServiceError):
            await profession_service.update_profession(self.session, created_id, ProfessionUpdate(name="铁衣"))
        await self.session.rollback()
        # 孤儿配置行（模拟历史残留）：目标名已被职业配置使用
        self.session.add(ProfessionConfig(guild_id=1, profession="待改名乙", target_count=1))
        await self.session.commit()
        with self.assertRaises(ProfessionServiceError):
            await profession_service.update_profession(self.session, created_id, ProfessionUpdate(name="待改名乙"))
        await self.session.rollback()

    async def test_member_edit_grandfathers_inactive_value(self) -> None:
        """旧值豁免：成员职业未变更时允许停用职业；改换必须为启用职业。"""
        await self._create("旧职业甲")
        await self._create("旧职业乙")
        member = await self._create_member("乙", "旧职业甲", "铁衣")
        member_id = member.id  # rollback 会过期 ORM 实例：ID 提前取出
        await self._deactivate("旧职业甲")
        await self._deactivate("旧职业乙")
        # 未变更主职业（停用）→ 可保存其他字段
        updated = await member_service.update_member(
            self.session, 1, member_id, MemberUpdate(main_profession="旧职业甲", status="substitute"), self.operator
        )
        self.assertEqual(updated.status, "substitute")
        # 换到另一个停用职业 → 拒绝；换到启用职业 → 允许
        with self.assertRaises(member_service.MemberServiceError):
            await member_service.update_member(
                self.session, 1, member_id, MemberUpdate(main_profession="旧职业乙"), self.operator
            )
        await self.session.rollback()
        ok = await member_service.update_member(
            self.session, 1, member_id, MemberUpdate(main_profession="素问"), self.operator
        )
        self.assertEqual(ok.main_profession, "素问")

    async def test_attendance_profession_grandfather(self) -> None:
        """出勤记录：与记录现值相同豁免；换成停用职业拒绝；换成启用职业允许。"""
        await self._create("旧职业甲")
        await self._create("旧职业乙")
        member = await self._create_member("丙", "旧职业甲", "铁衣")
        schedule = Schedule(guild_id=1, opponent="对手", match_time=datetime.now(UTC), rounds=1)
        self.session.add(schedule)
        await self.session.flush()
        record = AttendanceRecord(
            schedule_id=schedule.id, member_id=member.id, member_name="丙", profession="旧职业甲", status="normal"
        )
        self.session.add(record)
        await self.session.commit()
        schedule_id = schedule.id  # rollback 会过期 ORM 实例：ID 提前取出
        record_id = record.id
        await self._deactivate("旧职业甲")
        await self._deactivate("旧职业乙")

        same = await attendance_service.update_record_profession(self.session, 1, schedule_id, record_id, "旧职业甲")
        self.assertEqual(same.profession, "旧职业甲")
        with self.assertRaises(attendance_service.AttendanceServiceError):
            await attendance_service.update_record_profession(self.session, 1, schedule_id, record_id, "旧职业乙")
        await self.session.rollback()
        changed = await attendance_service.update_record_profession(self.session, 1, schedule_id, record_id, "铁衣")
        self.assertEqual(changed.profession, "铁衣")

    async def test_schedule_override_grandfather(self) -> None:
        """单场覆盖：既有键豁免；新键必须为启用职业。"""
        await self._create("旧职业甲")
        schedule = Schedule(
            guild_id=1,
            opponent="对手",
            match_time=datetime.now(UTC),
            rounds=1,
            profession_config={"旧职业甲": 3},
        )
        self.session.add(schedule)
        await self.session.commit()
        await self._deactivate("旧职业甲")

        updated = await schedule_service.update_profession_config(self.session, 1, schedule.id, {"旧职业甲": 4})
        self.assertEqual(updated.profession_config, {"旧职业甲": 4})
        with_new_key = {"旧职业甲": 4, "旧职业乙": 1}
        with self.assertRaises(schedule_service.ScheduleServiceError):
            await schedule_service.update_profession_config(self.session, 1, schedule.id, with_new_key)
        await self.session.rollback()

    async def test_excel_import_rejects_inactive_profession(self) -> None:
        """Excel 导入：停用职业行计入 errors 并跳过，启用职业行正常导入。"""
        await self._create("旧职业甲")
        await self._deactivate("旧职业甲")
        content = _xlsx_with_rows(
            [
                ("新丁", "旧职业甲", None, "formal", None),
                ("新戊", "铁衣", None, "formal", None),
            ]
        )
        result = await import_members(self.session, 1, content)
        self.assertEqual(result["imported"], 1)
        self.assertEqual(result["skipped"], 1)
        self.assertTrue(any("不存在或已停用" in err for err in result["errors"]))


class ProfessionRouteGuardTest(DbTestCase):
    async def test_route_guards(self) -> None:
        """路由守卫：GET 任意登录用户（get_current_user）；POST/PUT 仅开发者（require_developer）。

        说明：本版 FastAPI 的 include_router 为延迟物化（`app.routes` 中是 `_IncludedRouter` 占位），
        故「全链路可达」以 openapi 路径断言、「守卫依赖」以叶子路由（api/v1/professions.py）断言。
        """
        from app.api.v1 import professions as professions_api
        from app.main import app as fastapi_app

        spec_paths = fastapi_app.openapi()["paths"]
        self.assertIn("/api/v1/professions", spec_paths, "GET/POST /professions 应经全链路注册")
        self.assertIn("/api/v1/professions/{profession_id}", spec_paths, "PUT /professions/{id} 应经全链路注册")

        leaf = {(route.path, method): route for route in professions_api.router.routes for method in route.methods}
        get_calls = {dependency.call for dependency in leaf[("/professions", "GET")].dependant.dependencies}
        self.assertIn(deps.get_current_user, get_calls)
        self.assertNotIn(deps.require_developer, get_calls)
        for key in (("/professions", "POST"), ("/professions/{profession_id}", "PUT")):
            write_calls = {dependency.call for dependency in leaf[key].dependant.dependencies}
            self.assertIn(deps.require_developer, write_calls)

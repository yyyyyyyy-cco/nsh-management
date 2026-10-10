"""职业目录业务：全局职业清单（名称/排序/颜色/启停）的查询与维护。

权威源说明：职业清单自本次迭代起以数据库为准（`models/profession.py` 的 `Profession` 表），
不再使用代码常量。改名级联仅作用于活跃数据（成员/职业配置/单场覆盖）；
出勤/录屏/比赛数据的历史快照保持原名（database-design §2.13）。
"""

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.member import Member
from app.models.profession import Profession, ProfessionConfig
from app.models.schedule import Schedule
from app.schemas.profession import ProfessionCreate, ProfessionUpdate


class ProfessionServiceError(Exception):
    """职业目录业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def list_professions(session: AsyncSession, include_inactive: bool = True) -> list[Profession]:
    """职业目录列表（按 sort_order, id 升序）；默认含停用（前端需为历史数据着色）。"""
    stmt = select(Profession).order_by(Profession.sort_order, Profession.id)
    if not include_inactive:
        stmt = stmt.where(Profession.is_active.is_(True))
    return list((await session.execute(stmt)).scalars().all())


async def active_names(session: AsyncSession) -> set[str]:
    """启用职业名集合（各消费点校验的公共入口；「旧值豁免」由调用方自行放行）。"""
    rows = (await session.execute(select(Profession.name).where(Profession.is_active.is_(True)))).scalars().all()
    return set(rows)


async def create_profession(session: AsyncSession, data: ProfessionCreate) -> Profession:
    """新增职业：名称（含停用职业）全局唯一；排序缺省为当前最大值 +1。"""
    name = data.name.strip()
    if not name:
        raise ProfessionServiceError("职业名不能为空")
    existing = (await session.execute(select(Profession).where(Profession.name == name))).scalar_one_or_none()
    if existing is not None:
        raise ProfessionServiceError(f"职业「{name}」已存在（含停用职业不可重名）")
    sort_order = data.sort_order
    if sort_order is None:
        max_order = (await session.execute(select(func.max(Profession.sort_order)))).scalar()
        sort_order = (max_order or 0) + 1
    profession = Profession(name=name, sort_order=sort_order, color=data.color)
    session.add(profession)
    await session.commit()
    await session.refresh(profession)
    return profession


async def update_profession(session: AsyncSession, profession_id: int, data: ProfessionUpdate) -> Profession:
    """局部更新：改名级联（活跃数据）与停用守卫（至少保留一个启用职业）。"""
    profession = await session.get(Profession, profession_id)
    if profession is None:
        raise ProfessionServiceError("职业不存在", 404)
    changes = data.model_dump(exclude_unset=True)

    new_name = changes.get("name")
    if new_name is not None:
        new_name = new_name.strip()
        if not new_name:
            raise ProfessionServiceError("职业名不能为空")
        if new_name != profession.name:
            await _cascade_rename(session, profession, new_name)

    if changes.get("is_active") is False and profession.is_active:
        active_count = (
            await session.execute(select(func.count(Profession.id)).where(Profession.is_active.is_(True)))
        ).scalar_one()
        if active_count <= 1:
            raise ProfessionServiceError("至少保留一个启用职业")

    if new_name is not None:
        profession.name = new_name
    for field in ("sort_order", "color", "is_active"):
        if field in changes and changes[field] is not None:
            setattr(profession, field, changes[field])
    await session.commit()
    await session.refresh(profession)
    return profession


async def _cascade_rename(session: AsyncSession, profession: Profession, new_name: str) -> None:
    """改名校验与级联（活跃数据）；与调用方同一次 commit（本函数不自行提交）。

    历史快照（attendance_records / recordings / match_data）不更新——保持写入时原名。
    """
    old_name = profession.name
    dup = (
        await session.execute(
            select(Profession.id).where(Profession.name == new_name, Profession.id != profession.id).limit(1)
        )
    ).scalar_one_or_none()
    if dup is not None:
        raise ProfessionServiceError(f"职业「{new_name}」已存在（含停用职业不可重名）")
    config_conflict = (
        await session.execute(select(ProfessionConfig.id).where(ProfessionConfig.profession == new_name).limit(1))
    ).scalar_one_or_none()
    if config_conflict is not None:
        raise ProfessionServiceError(f"目标职业名「{new_name}」已被职业配置使用")

    await session.execute(update(Member).where(Member.main_profession == old_name).values(main_profession=new_name))
    await session.execute(update(Member).where(Member.sub_profession == old_name).values(sub_profession=new_name))
    await session.execute(
        update(ProfessionConfig).where(ProfessionConfig.profession == old_name).values(profession=new_name)
    )
    schedules = (await session.execute(select(Schedule).where(Schedule.profession_config.is_not(None)))).scalars().all()
    for schedule in schedules:
        config = schedule.profession_config or {}
        if old_name in config:
            schedule.profession_config = {new_name if key == old_name else key: value for key, value in config.items()}

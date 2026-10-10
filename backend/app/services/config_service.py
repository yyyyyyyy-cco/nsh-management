"""系统配置业务：职业配置（账号管理见 account_service，帮会管理见 guild_service）。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession import ProfessionConfig
from app.services import profession_service
from app.utils.constants import MAX_PROFESSION_TARGET


class ConfigServiceError(Exception):
    """系统配置业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_profession_configs(session: AsyncSession, guild_id: int | None) -> list[ProfessionConfig]:
    """获取帮会的职业配置列表（仅启用职业，按职业目录顺序）。开发者账号无帮会时返回空列表。

    缺失的职业在内存中补齐默认值（GET 不写库，避免读请求占用写锁；首次保存时落库）。
    停用职业的既有配置行不返回（重新启用后自动恢复展示）；职业目录权威源见 database-design §2.13。
    """
    if guild_id is None:
        return []

    rows = list(
        (await session.execute(select(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id))).scalars().all()
    )
    existing = {c.profession: c for c in rows}

    configs: list[ProfessionConfig] = []
    for profession in await profession_service.list_professions(session, include_inactive=False):
        config = existing.get(profession.name)
        if config is None:
            config = ProfessionConfig(guild_id=guild_id, profession=profession.name, target_count=0)
        configs.append(config)
    return configs


async def update_profession_config(
    session: AsyncSession, guild_id: int | None, profession: str, target_count: int, remark: str | None = None
) -> ProfessionConfig:
    """更新单个职业的目标人数与说明。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")
    if profession not in await profession_service.active_names(session):
        raise ConfigServiceError(f"无效的职业：{profession}")
    if not isinstance(target_count, int) or not 0 <= target_count <= MAX_PROFESSION_TARGET:
        raise ConfigServiceError(f"目标人数无效（0～{MAX_PROFESSION_TARGET}）")

    config = (
        await session.execute(
            select(ProfessionConfig).where(
                ProfessionConfig.guild_id == guild_id,
                ProfessionConfig.profession == profession,
            )
        )
    ).scalar_one_or_none()

    if config is None:
        config = ProfessionConfig(
            guild_id=guild_id,
            profession=profession,
            target_count=target_count,
            remark=remark,
        )
        session.add(config)
    else:
        config.target_count = target_count
        config.remark = remark

    await session.commit()
    await session.refresh(config)
    return config


async def batch_update_profession_configs(session: AsyncSession, guild_id: int | None, configs_data: list[dict]) -> int:
    """批量更新职业配置（一次载入、内存 diff、单次 commit）。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")

    existing = {
        c.profession: c
        for c in (await session.execute(select(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id)))
        .scalars()
        .all()
    }

    active = await profession_service.active_names(session)
    count = 0
    for item in configs_data:
        profession = item.get("profession")
        target_count = item.get("target_count", 0)
        remark = item.get("remark")

        if profession not in active:
            continue
        if not isinstance(target_count, int) or not 0 <= target_count <= MAX_PROFESSION_TARGET:
            raise ConfigServiceError(f"职业「{profession}」的目标人数无效（0～{MAX_PROFESSION_TARGET}）")

        config = existing.get(profession)
        if config is None:
            config = ProfessionConfig(
                guild_id=guild_id,
                profession=profession,
                target_count=target_count,
                remark=remark,
            )
            session.add(config)
            existing[profession] = config
        else:
            config.target_count = target_count
            config.remark = remark
        count += 1

    await session.commit()
    return count

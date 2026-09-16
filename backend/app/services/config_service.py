"""系统配置业务：职业配置（账号管理见 account_service，帮会管理见 guild_service）。"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession import ProfessionConfig
from app.utils.constants import PROFESSIONS


class ConfigServiceError(Exception):
    """系统配置业务异常。"""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


async def get_profession_configs(session: AsyncSession, guild_id: int | None) -> list[ProfessionConfig]:
    """获取帮会的职业配置列表。开发者账号无帮会时返回空列表。

    缺失的职业在内存中补齐默认值（GET 不写库，避免读请求占用写锁；首次保存时落库）。
    """
    if guild_id is None:
        return []

    configs = list(
        (
            await session.execute(
                select(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id)
            )
        )
        .scalars()
        .all()
    )

    # 缺少某些职业的配置，内存补齐默认配置（不落库）
    existing_professions = {c.profession for c in configs}
    for profession in PROFESSIONS:
        if profession not in existing_professions:
            configs.append(
                ProfessionConfig(
                    guild_id=guild_id,
                    profession=profession,
                    target_count=0,
                )
            )

    configs.sort(key=lambda c: c.profession)
    return configs


async def update_profession_config(
    session: AsyncSession, guild_id: int | None, profession: str, target_count: int, remark: str | None = None
) -> ProfessionConfig:
    """更新单个职业的目标人数与说明。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")
    if profession not in PROFESSIONS:
        raise ConfigServiceError(f"无效的职业：{profession}")

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


async def batch_update_profession_configs(
    session: AsyncSession, guild_id: int | None, configs_data: list[dict]
) -> int:
    """批量更新职业配置（一次载入、内存 diff、单次 commit）。"""
    if guild_id is None:
        raise ConfigServiceError("开发者账号无法修改职业配置，请先创建帮会")

    existing = {
        c.profession: c
        for c in (
            await session.execute(
                select(ProfessionConfig).where(ProfessionConfig.guild_id == guild_id)
            )
        )
        .scalars()
        .all()
    }

    count = 0
    for item in configs_data:
        profession = item.get("profession")
        target_count = item.get("target_count", 0)
        remark = item.get("remark")

        if profession not in PROFESSIONS:
            continue

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

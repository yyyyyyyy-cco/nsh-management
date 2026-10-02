"""联赛日程请求/响应模型。"""
from datetime import datetime, timedelta, timezone

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import UtcDatetime

# 业务约定：match_time 为 naive，语义 = 用户本地（UTC+8）墙上时间，
# 与前端日历/今日赛程/按月查询口径一致；勿改为带时区或 UTC 存储。
USER_TZ = timezone(timedelta(hours=8))


def _normalize_match_time(value: datetime | None) -> datetime | None:
    """防御外部调用者传带时区的 ISO（如 Z 结尾）：转北京墙上时间后去 tz 再存。"""
    if value is None or value.tzinfo is None:
        return value
    return value.astimezone(USER_TZ).replace(tzinfo=None)


class ScheduleCreate(BaseModel):
    opponent: str = Field(..., min_length=1, max_length=64)
    match_time: datetime
    location: str | None = Field(None, max_length=128)
    rounds: int = Field(..., ge=1, le=3)  # 创建后不可修改

    _naive_match_time = field_validator("match_time")(_normalize_match_time)


class ScheduleUpdate(BaseModel):
    opponent: str | None = Field(None, min_length=1, max_length=64)
    match_time: datetime | None = None
    location: str | None = Field(None, max_length=128)
    result: str | None = None  # win / lose / draw / pending
    round_results: list[str] | None = None  # 每局结果，长度须与局数一致

    _naive_match_time = field_validator("match_time")(_normalize_match_time)


class ScheduleOut(BaseModel):
    id: int
    guild_id: int
    opponent: str
    match_time: datetime
    location: str | None
    rounds: int
    result: str
    round_results: list | None
    profession_config: dict[str, int] | None = None  # 单场职业配置覆盖，NULL 沿用系统配置
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class ScheduleProfessionConfigUpdate(BaseModel):
    """单场职业配置覆盖：configs 为 {职业: 目标人数}，None 表示恢复默认（沿用系统配置）。"""

    configs: dict[str, int] | None = None

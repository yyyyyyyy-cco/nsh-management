"""联赛日程请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field


class ScheduleCreate(BaseModel):
    opponent: str = Field(..., min_length=1, max_length=64)
    match_time: datetime
    location: str | None = Field(None, max_length=128)
    rounds: int = Field(..., ge=1, le=3)  # 创建后不可修改


class ScheduleUpdate(BaseModel):
    opponent: str | None = Field(None, min_length=1, max_length=64)
    match_time: datetime | None = None
    location: str | None = Field(None, max_length=128)
    result: str | None = None  # win / lose / draw / pending
    round_results: list[str] | None = None  # 每局结果，长度须与局数一致


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
    created_at: datetime

    model_config = {"from_attributes": True}


class ScheduleProfessionConfigUpdate(BaseModel):
    """单场职业配置覆盖：configs 为 {职业: 目标人数}，None 表示恢复默认（沿用系统配置）。"""

    configs: dict[str, int] | None = None

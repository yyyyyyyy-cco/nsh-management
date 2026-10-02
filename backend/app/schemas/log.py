"""日志模块 Pydantic Schema。"""

from pydantic import BaseModel, Field

from app.schemas.common import UtcDatetime


class OperationLogOut(BaseModel):
    """审计日志输出。"""

    id: int
    user_id: int | None = None
    username: str | None = None
    role: str | None = None
    guild_id: int | None = None
    module: str
    action: str
    method: str
    path: str
    status_code: int | None = None
    level: str
    detail: str | None = None
    ip: str | None = None
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class LogListOut(BaseModel):
    """日志分页列表。"""

    total: int
    items: list[OperationLogOut]


class WeeklyErrorItem(BaseModel):
    date: str
    count: int


class LogStatsOut(BaseModel):
    """日志概览统计。"""

    today_requests: int
    today_errors: int
    weekly_errors: list[WeeklyErrorItem]


class LogClearRequest(BaseModel):
    """清理日志请求：删除 days 天前的日志。"""

    days: int = Field(90, ge=1, le=3650, description="清理多少天前的日志")

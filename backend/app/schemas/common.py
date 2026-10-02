"""Schema 共享类型：时间戳序列化与批量 ID 校验约定。

全站时间语义分两类（勿混用）：
- 系统生成时间戳（created_at / updated_at / reviewed_at）：存储为 UTC（naive），
  输出经 UtcDatetime 补 +00:00 标记，前端 dayjs 自动转浏览器本地时区显示；
- 业务输入时间（schedule.match_time）：naive 直存，语义 = 用户本地（UTC+8）墙上时间，
  不做任何标记，保持与前端日历/按天分组/按月查询口径一致。
"""
from datetime import datetime, timezone
from typing import Annotated

from pydantic import Field, PlainSerializer


def _mark_utc(dt: datetime) -> datetime:
    """SQLite 读回 naive；系统时间戳一律为 UTC，补时区标记（已是 aware 则原样）。"""
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


UtcDatetime = Annotated[datetime, PlainSerializer(_mark_utc, return_type=datetime)]

# 批量写操作共用边界：非空、最多 500 个正整数 ID，拒绝布尔值与隐式类型转换。
BatchIds = Annotated[
    list[Annotated[int, Field(gt=0, strict=True)]],
    Field(min_length=1, max_length=500),
]

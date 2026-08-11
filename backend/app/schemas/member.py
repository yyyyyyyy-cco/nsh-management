"""常驻库成员请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field


class MemberBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    main_profession: str = Field(..., max_length=16)
    sub_profession: str | None = Field(None, max_length=16)
    status: str = "formal"  # formal / substitute
    remark: str | None = Field(None, max_length=255)


class MemberCreate(MemberBase):
    pass


class MemberUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=32)
    main_profession: str | None = Field(None, max_length=16)
    sub_profession: str | None = Field(None, max_length=16)
    status: str | None = None
    remark: str | None = Field(None, max_length=255)


class MemberOut(MemberBase):
    id: int
    guild_id: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemberPage(BaseModel):
    items: list[MemberOut]
    total: int
    page: int
    page_size: int


class BatchDeleteRequest(BaseModel):
    ids: list[int]


class AttendanceRateItem(BaseModel):
    member_id: int
    name: str
    main_profession: str
    status: str
    normal_count: int
    leave_count: int
    attendance_rate: float | None  # 无出勤记录时为 None

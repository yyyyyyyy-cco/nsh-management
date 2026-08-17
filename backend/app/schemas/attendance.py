"""出勤库请求/响应模型。"""
from pydantic import BaseModel, Field


class AttendanceRecordOut(BaseModel):
    id: int
    schedule_id: int
    member_id: int | None
    member_name: str
    profession: str
    status: str  # normal / leave
    is_filler: bool  # 补人（非帮会成员）
    member_status: str | None = None  # 常驻库成员状态 formal/substitute，补人为 None

    model_config = {"from_attributes": True}


class AttendanceStats(BaseModel):
    total: int
    normal_count: int
    leave_count: int
    gap: int  # 缺口 = max(0, 60 - 正常人数)


class AttendanceListResponse(BaseModel):
    items: list[AttendanceRecordOut]
    stats: AttendanceStats


class SubstituteCandidateOut(BaseModel):
    id: int
    name: str
    main_profession: str
    sub_profession: str | None
    remark: str | None

    model_config = {"from_attributes": True}


class ImportSubstitutesRequest(BaseModel):
    member_ids: list[int]


class FillerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=32)
    profession: str = Field(..., max_length=16)


class StatusUpdate(BaseModel):
    status: str  # normal / leave


class BatchStatusUpdate(BaseModel):
    ids: list[int]
    status: str  # normal / leave


class AttendanceStatsResponse(BaseModel):
    message: str
    stats: AttendanceStats

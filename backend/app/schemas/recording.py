"""录屏模块 Pydantic Schema。"""
from datetime import datetime

from pydantic import BaseModel, Field


class RecordingOut(BaseModel):
    """录屏记录输出。"""
    id: int
    schedule_id: int
    member_id: int | None
    member_name: str
    round_number: int
    url: str | None
    status: str
    review_remark: str | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class RecordingSubmit(BaseModel):
    """提交录屏链接。"""
    url: str = Field(..., min_length=1, max_length=512, description="录屏链接")


class RecordingReview(BaseModel):
    """审核录屏。"""
    remark: str | None = Field(None, max_length=255, description="审核备注")


class BatchApproveRequest(BaseModel):
    """批量审核通过。"""
    ids: list[int] = Field(..., min_length=1, description="录屏记录 ID 列表")


class RoundProgress(BaseModel):
    """单局审核进度。"""
    round_number: int
    total: int
    approved: int
    rejected: int
    pending: int


class RecordingListResponse(BaseModel):
    """录屏列表响应。"""
    items: list[RecordingOut]
    progress: list[RoundProgress]

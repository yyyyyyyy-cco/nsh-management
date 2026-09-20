"""录屏模块 Pydantic Schema。"""
from pydantic import BaseModel, Field

from app.schemas.common import BatchIds, UtcDatetime


class RecordingOut(BaseModel):
    """录屏记录输出。"""
    id: int
    schedule_id: int
    member_id: int | None
    member_name: str
    profession: str | None = None  # 职业快照（取自出勤库，便于按职业排序）
    round_number: int
    url: str | None
    note: str | None = None  # 帮众备注（前端展示层对帮众脱敏，仅管理员可见）
    status: str
    review_remark: str | None
    reviewed_at: UtcDatetime | None
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class RecordingSubmit(BaseModel):
    """提交录屏链接（须以 http:// 或 https:// 开头，防任意字符串/伪协议注入）。"""
    url: str = Field(
        ..., min_length=1, max_length=512, pattern=r"^https?://",
        description="录屏链接（须以 http:// 或 https:// 开头）",
    )


class RecordingNoteSubmit(BaseModel):
    """提交备注（自由内容，仅管理员可见，不影响审核状态）。"""
    note: str = Field(
        ..., min_length=1, max_length=500,
        description="备注内容（可填写任何内容）",
    )


class RecordingReview(BaseModel):
    """审核录屏。"""
    remark: str | None = Field(None, max_length=255, description="审核备注")


class BatchApproveRequest(BaseModel):
    """批量审核通过。"""
    ids: BatchIds = Field(..., description="录屏记录 ID 列表")


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

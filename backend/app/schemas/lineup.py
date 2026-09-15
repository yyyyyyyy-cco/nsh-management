"""排表请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import UtcDatetime


class LineupSlot(BaseModel):
    slot_index: int = Field(..., ge=0, le=5)
    member_id: int | None = None
    member_name: str = ""
    remark: str = Field("", max_length=255, description="槽位备注")
    profession: str | None = None  # 职业快照（读取时填充，保存时忽略）


class LineupTeam(BaseModel):
    category: str  # 进攻1 / 进攻2 / 防守1 / 防守2
    team_index: int
    slots: list[LineupSlot]


class LineupOut(BaseModel):
    id: int
    schedule_id: int
    data: list[LineupTeam]
    title_remark: str = ""
    groups_remark: dict = {}
    updated_at: UtcDatetime

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj):
        # 兼容性处理：DB 新列可能为 NULL
        if hasattr(obj, 'title_remark') and obj.title_remark is None:
            obj.title_remark = ""
        if hasattr(obj, 'groups_remark') and obj.groups_remark is None:
            obj.groups_remark = {}
        return super().model_validate(obj)


class LineupUpdate(BaseModel):
    data: list[LineupTeam]
    title_remark: str = ""
    groups_remark: dict = {}


class LineupCandidateOut(BaseModel):
    member_id: int | None  # 补人为 None
    member_name: str
    profession: str
    member_status: str  # formal / substitute / filler
    attendance_remark: str | None = None  # 出勤库备注（导入时从常驻库带入，可修改；补人无）


class LineupHistoryOut(BaseModel):
    """历史排表条目：赛程摘要 + 完整排表数据（供导入预览）。"""

    schedule_id: int
    opponent: str
    match_time: datetime
    teams: list[LineupTeam]


class LineupImportRequest(BaseModel):
    """导入历史排表请求：来源赛程 + 选中要导入的小队（如 "进攻1:0"）。"""

    source_schedule_id: int
    team_keys: list[str] = []

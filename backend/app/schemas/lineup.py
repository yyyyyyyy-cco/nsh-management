"""排表请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field


class LineupSlot(BaseModel):
    slot_index: int = Field(..., ge=0, le=5)
    member_id: int | None = None
    member_name: str = ""
    remark: str = ""


class LineupTeam(BaseModel):
    category: str  # 进攻1 / 进攻2 / 防守1 / 防守2
    team_index: int
    slots: list[LineupSlot]


class LineupOut(BaseModel):
    id: int
    schedule_id: int
    data: list[LineupTeam]
    updated_at: datetime

    model_config = {"from_attributes": True}


class LineupUpdate(BaseModel):
    data: list[LineupTeam]


class LineupCandidateOut(BaseModel):
    member_id: int | None  # 补人为 None
    member_name: str
    profession: str
    member_status: str  # formal / substitute / filler

"""分析调整副本请求/响应模型。"""
from datetime import datetime

from pydantic import BaseModel, Field


class SquadAdjustmentUpdate(BaseModel):
    data: dict[str, str] = Field(default_factory=dict, description="player_name → category:team_index")


class SquadAdjustmentOut(BaseModel):
    schedule_id: int
    data: dict[str, str]
    updated_at: datetime

    model_config = {"from_attributes": True}

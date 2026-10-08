"""分析调整副本请求/响应模型。"""

from pydantic import BaseModel, Field

from app.schemas.common import UtcDatetime


class SquadAdjustmentUpdate(BaseModel):
    data: dict[str, str] = Field(default_factory=dict, description="player_name → category:team_index")


class SquadAdjustmentOut(BaseModel):
    schedule_id: int
    data: dict[str, str]
    updated_at: UtcDatetime

    model_config = {"from_attributes": True}

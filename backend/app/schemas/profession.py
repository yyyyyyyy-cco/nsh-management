"""职业目录 Pydantic Schema。"""

from pydantic import BaseModel, Field

from app.schemas.common import UtcDatetime


class ProfessionOut(BaseModel):
    """职业目录输出。"""

    id: int
    name: str
    sort_order: int
    color: str
    is_active: bool
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class ProfessionCreate(BaseModel):
    """新增职业。"""

    name: str = Field(..., min_length=1, max_length=16, description="职业名（去首尾空白后不可为空）")
    color: str = Field("#c9a13b", pattern=r"^#[0-9a-fA-F]{6}$", description="职业色（#RRGGBB）")
    sort_order: int | None = Field(None, ge=0, description="展示排序（缺省追加到末位）")


class ProfessionUpdate(BaseModel):
    """更新职业（局部）：name 变更触发改名级联；is_active=false 即停用（至少保留一个启用职业）。"""

    name: str | None = Field(None, min_length=1, max_length=16, description="新职业名（触发改名级联）")
    color: str | None = Field(None, pattern=r"^#[0-9a-fA-F]{6}$", description="职业色（#RRGGBB）")
    sort_order: int | None = Field(None, ge=0, description="展示排序")
    is_active: bool | None = Field(None, description="启用状态（false=停用）")

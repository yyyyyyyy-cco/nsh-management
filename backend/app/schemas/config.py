"""系统配置 Pydantic Schema。"""
from datetime import datetime

from pydantic import BaseModel, Field


# ========== 职业配置 ==========

class ProfessionConfigOut(BaseModel):
    """职业配置输出。"""
    id: int
    guild_id: int
    profession: str
    target_count: int

    model_config = {"from_attributes": True}


class ProfessionConfigUpdate(BaseModel):
    """职业配置更新。"""
    target_count: int = Field(..., ge=0, description="目标人数")


class ProfessionConfigBatchUpdate(BaseModel):
    """职业配置批量更新。"""
    configs: list[dict] = Field(..., description="配置列表，每项包含 profession 和 target_count")


# ========== 账号管理 ==========

class AccountOut(BaseModel):
    """账号输出。"""
    id: int
    guild_id: int
    username: str
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    """创建账号。"""
    username: str = Field(..., min_length=3, max_length=64, description="登录名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    role: str = Field("member", description="角色：admin/member")


class AccountUpdate(BaseModel):
    """更新账号。"""
    username: str | None = Field(None, min_length=3, max_length=64, description="登录名")
    password: str | None = Field(None, min_length=6, max_length=128, description="密码")


class AccountStatusUpdate(BaseModel):
    """更新账号状态。"""
    status: str = Field(..., description="状态：active/disabled")


class GuildOut(BaseModel):
    """帮会输出。"""
    id: int
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}


class GuildCreate(BaseModel):
    """创建帮会。"""
    name: str = Field(..., min_length=2, max_length=64, description="帮会名称")

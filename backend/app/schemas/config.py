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
    remark: str | None = None  # 职业说明（可编辑，默认空）

    model_config = {"from_attributes": True}


class ProfessionConfigUpdate(BaseModel):
    """职业配置更新。"""
    target_count: int = Field(..., ge=0, description="目标人数")
    remark: str | None = Field(None, max_length=255, description="职业说明")


class ProfessionConfigBatchUpdate(BaseModel):
    """职业配置批量更新。"""
    configs: list[dict] = Field(..., description="配置列表，每项包含 profession 和 target_count")


# ========== 账号管理 ==========

class AccountOut(BaseModel):
    """账号输出。"""
    id: int
    guild_id: int | None
    guild_name: str | None = None
    username: str
    plain_password: str | None = None
    role: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    """创建账号。"""
    username: str = Field(..., min_length=3, max_length=64, description="登录名")
    password: str = Field(..., min_length=6, max_length=128, description="密码")
    role: str = Field("member", description="角色：admin/member")
    guild_id: int | None = Field(None, description="目标帮会ID（开发者创建时必传，管理员默认本帮会）")


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

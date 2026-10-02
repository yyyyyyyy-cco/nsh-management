"""系统配置 Pydantic Schema。"""
from pydantic import BaseModel, Field, field_validator

from app.core.password_policy import validate_password
from app.schemas.common import UtcDatetime


def _validate_password_complexity(value: str) -> str:
    """口令策略校验（实现见 `app/core/password_policy.py`）。

    2026-10-02（合规化计划 W4-10 / ASVS 5.0.0）：**删除了原「必须同时含字母和数字」的规则**——
    该规则违反 6.2.5（不得限制字符组成）；改为「长度 8–128 + 弱口令/上下文词表 + 不含登录名 + 非单一重复字符」，
    纯字母/纯数字/纯符号口令都允许。函数名保留以免改动调用点。
    """
    validate_password(value)
    return value


def _validate_password_optional(value: str | None) -> str | None:
    """可选口令字段的策略校验（None 直接放行）。"""
    if value is None:
        return value
    return _validate_password_complexity(value)


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
    target_count: int = Field(..., ge=0, le=999, description="目标人数（0～999）")
    remark: str | None = Field(None, max_length=255, description="职业说明")


class ProfessionConfigItem(BaseModel):
    """批量配置中的单项：值域与单职业端点一致（0～999，与前端输入上限一致）。"""

    profession: str = Field(..., min_length=1, max_length=16, description="职业名")
    target_count: int = Field(..., ge=0, le=999, description="目标人数（0～999）")
    remark: str | None = Field(None, max_length=255, description="职业说明")


class ProfessionConfigBatchUpdate(BaseModel):
    """职业配置批量更新。"""
    configs: list[ProfessionConfigItem] = Field(..., description="配置列表：profession + target_count + 可选 remark")


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
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class AccountCreate(BaseModel):
    """创建账号。"""
    username: str = Field(..., min_length=3, max_length=64, description="登录名")
    password: str = Field(
        ..., min_length=8, max_length=128,
        description="密码（8-128 位；不得为常见弱口令、不得含登录名；不限制字符组成）",
    )
    role: str = Field("member", description="角色：admin/member")
    guild_id: int | None = Field(None, ge=1, description="目标帮会ID（开发者创建时必传，管理员仅限本帮会）")

    _password_complexity = field_validator("password")(_validate_password_complexity)


class AccountUpdate(BaseModel):
    """更新账号。"""
    username: str | None = Field(None, min_length=3, max_length=64, description="登录名")
    password: str | None = Field(
        None, min_length=8, max_length=128,
        description="密码（8-128 位；不得为常见弱口令、不得含登录名；不限制字符组成）",
    )

    _password_complexity = field_validator("password")(_validate_password_optional)


class AccountStatusUpdate(BaseModel):
    """更新账号状态。"""
    status: str = Field(..., description="状态：active/disabled")


class GuildOut(BaseModel):
    """帮会输出。"""
    id: int
    name: str
    icon_char: str | None = None
    created_at: UtcDatetime

    model_config = {"from_attributes": True}


class GuildCreate(BaseModel):
    """创建帮会（管理员/帮众初始密码由创建者指定，按密码策略校验）。"""
    name: str = Field(..., min_length=2, max_length=64, description="帮会名称")
    admin_password: str = Field(
        ..., min_length=8, max_length=128,
        description="管理员初始密码（8-128 位；不得为常见弱口令、不得含登录名；不限制字符组成）",
    )
    member_password: str = Field(
        ..., min_length=8, max_length=128,
        description="帮众初始密码（8-128 位；不得为常见弱口令、不得含登录名；不限制字符组成）",
    )

    _validate_admin_password = field_validator("admin_password")(_validate_password_complexity)
    _validate_member_password = field_validator("member_password")(_validate_password_complexity)


class GuildRename(BaseModel):
    """帮会更名。"""
    name: str = Field(..., min_length=2, max_length=64, description="新帮会名称")


class GuildIconUpdate(BaseModel):
    """帮会图标字设置（空串表示清除）。"""
    icon_char: str = Field("", max_length=4, description="显示的首字，空串清除")

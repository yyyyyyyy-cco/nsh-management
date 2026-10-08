"""认证相关请求/响应模型。"""

from pydantic import BaseModel, Field, field_validator

from app.core.password_policy import validate_password


def _validate_new_password(value: str) -> str:
    """新口令策略（不含登录名的判断在服务层做，那里拿得到用户名）。"""
    validate_password(value)
    return value


class PasswordChangeRequest(BaseModel):
    """自助修改口令（ASVS 5.0.0 6.2.2 / 6.2.3：用户可改口令，且须提供当前口令）。"""

    current_password: str = Field(..., min_length=1, max_length=128, description="当前密码")
    new_password: str = Field(..., min_length=8, max_length=128, description="新密码（8-128 位）")

    _new_password_policy = field_validator("new_password")(_validate_new_password)


class LoginRequest(BaseModel):
    # 长度上限防超大请求体消耗服务器资源（bcrypt/解析 DoS 向量）
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class UserOut(BaseModel):
    id: int
    guild_id: int | None
    guild_name: str | None = None
    guild_icon: str | None = None
    username: str
    role: str
    status: str

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

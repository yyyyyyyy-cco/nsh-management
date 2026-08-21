"""认证相关请求/响应模型。"""
from pydantic import BaseModel, Field


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

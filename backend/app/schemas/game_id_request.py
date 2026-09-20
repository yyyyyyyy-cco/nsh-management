"""游戏 ID 修改申请请求/响应模型。

状态机与字段语义见 memory-bank/design-game-id-change.md；表结构见 database-design.md §2.12。
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.common import UtcDatetime

MAX_GAME_ID_LENGTH = 32


def normalize_new_game_id(value: str) -> str:
    """去首尾空白并校验游戏 ID：1～32 字符，不允许换行/控制字符（不做大小写或全半角归并）。"""
    text = (value or "").strip()
    if not text:
        raise ValueError("游戏 ID 不能为空")
    if len(text) > MAX_GAME_ID_LENGTH:
        raise ValueError(f"游戏 ID 长度不能超过 {MAX_GAME_ID_LENGTH} 个字符")
    if any(ch in "\r\n\t" or ord(ch) < 32 or ord(ch) == 127 for ch in text):
        raise ValueError("游戏 ID 不能包含换行或控制字符")
    return text


class MemberMinimal(BaseModel):
    """候选/历史页使用的最小成员信息（不暴露备注与账号资料）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    main_profession: str
    status: str


class GameIdRequestCreate(BaseModel):
    """提交申请：旧值仅用于防页面过期，真正存储的旧值取自数据库。"""

    model_config = ConfigDict(extra="forbid")

    expected_old_game_id: str = Field(..., min_length=1, max_length=32)
    new_game_id: str

    @field_validator("expected_old_game_id")
    @classmethod
    def _clean_expected(cls, value: str) -> str:
        text = (value or "").strip()
        if not text:
            raise ValueError("原 ID 不能为空")
        return text

    @field_validator("new_game_id")
    @classmethod
    def _clean_new(cls, value: str) -> str:
        return normalize_new_game_id(value)


class GameIdRequestAudit(BaseModel):
    """审核申请：通过需显式确认身份，驳回需填写原因。"""

    model_config = ConfigDict(extra="forbid")

    action: Literal["approve", "reject"]
    identity_confirmed: bool = False
    review_remark: str | None = Field(None, max_length=255)

    @field_validator("review_remark")
    @classmethod
    def _clean_remark(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None

    @model_validator(mode="after")
    def _check_by_action(self) -> "GameIdRequestAudit":
        if self.action == "approve":
            if not self.identity_confirmed:
                raise ValueError("请先确认已核实申请人身份")
        elif not self.review_remark:
            raise ValueError("驳回时必须填写原因")
        return self


class GameIdRequestMemberOut(BaseModel):
    """帮众可见的申请记录（不含账号快照）。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int | None
    old_game_id: str
    new_game_id: str
    status: str
    review_remark: str | None
    invalidated_reason: str | None
    created_at: UtcDatetime
    reviewed_at: UtcDatetime | None
    updated_at: UtcDatetime


class GameIdRequestAdminOut(GameIdRequestMemberOut):
    """管理员可见的申请记录（含提交/审核账号快照与当前成员名称）。"""

    requester_username: str
    reviewer_username: str | None
    current_game_id: str | None = None


class GameIdOptionPage(BaseModel):
    items: list[MemberMinimal]
    total: int
    page: int
    page_size: int


class GameIdRequestMemberPage(BaseModel):
    member: MemberMinimal
    items: list[GameIdRequestMemberOut]
    total: int
    page: int
    page_size: int


class GameIdRequestAdminPage(BaseModel):
    items: list[GameIdRequestAdminOut]
    total: int
    page: int
    page_size: int


class GameIdRequestAdminHistoryPage(BaseModel):
    """管理员查看某成员历史时额外返回账号快照与当前成员名（帮众走 MemberPage）。"""

    member: MemberMinimal
    items: list[GameIdRequestAdminOut]
    total: int
    page: int
    page_size: int

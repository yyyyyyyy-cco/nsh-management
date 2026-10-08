# -*- coding: utf-8 -*-
"""口令策略（纯逻辑，仅标准库——便于无依赖环境直接测试）。

**背景与沿革（重要）**：本模块 2026-10-02 由 `app/schemas/config.py` 里的内联校验
（`_validate_password_complexity`：强制「字母 + 数字」）重构而来，并按 ASVS 5.0.0 校正：

- 6.2.1（L1）口令至少 8 位 → `MIN_LENGTH = 8`（文档建议 15，见 `memory-bank/security-review.md`）；
- 6.2.9（L2）必须允许 ≥64 位 → `MAX_LENGTH = 128`；
- **6.2.5（L1）不得限制字符组成** → 因此**删除了原来的「必须含字母和数字」规则**：
  纯字母、纯数字、纯符号口令都应被允许，改用「长度 + 弱口令/上下文词表」拦截；
- 6.1.2 / 6.2.11 维护上下文相关词表（项目名、角色名、通用弱口令）并在设置口令时拒绝；
- 6.2.4 / 6.2.12 泄露口令集比对**未实现**（需离线字典或外部服务），见整改计划 F-52。

设计：抛 `PasswordPolicyError(ValueError)`，Pydantic 会把它转成校验错误（422），
服务层也可直接调用以形成第二道防线。
"""

from __future__ import annotations

MIN_LENGTH = 8
MAX_LENGTH = 128

# 上下文相关词与常见弱口令（小写比对）。**只做拦截，不做组成要求**（ASVS 6.2.5）。
CONTEXT_WORDS = frozenset(
    {
        # 通用弱口令
        "password",
        "passw0rd",
        "12345678",
        "123456789",
        "1234567890",
        "87654321",
        "qwertyui",
        "qwerty123",
        "abc12345",
        "11111111",
        "00000000",
        "iloveyou",
        "admin123",
        "root1234",
        "letmein1",
        "welcome1",
        "monkey123",
        "dragon123",
        # 项目/业务上下文
        "nsh",
        "nsh12345",
        "jianshan",
        "qingshan",
        "guild",
        "league",
        "member",
        "developer",
        "admin",
        "nishuihan",
        "逆水寒",
        "轻衫",
        "帮会",
        "联赛",
    }
)


class PasswordPolicyError(ValueError):
    """口令不符合策略（消息面向使用者，直接透出到 422 响应）。"""


def validate_password(password: str, *, username: str | None = None) -> None:
    """校验口令；不合规抛 `PasswordPolicyError`。

    规则（与 ASVS 5.0.0 对应）：
    1. 长度 8–128（6.2.1 / 6.2.9）；
    2. 不得是上下文词或常见弱口令（6.1.2 / 6.2.11）——**不以字符组成为条件**（6.2.5）；
    3. 不得包含登录名（或反过来被登录名包含）；
    4. 不得是单一字符的重复（如 `aaaaaaaa`）。
    """
    if len(password) < MIN_LENGTH:
        raise PasswordPolicyError(f"密码长度至少 {MIN_LENGTH} 位")
    if len(password) > MAX_LENGTH:
        raise PasswordPolicyError(f"密码长度不得超过 {MAX_LENGTH} 位")
    if password.lower() in CONTEXT_WORDS:
        raise PasswordPolicyError("密码过于常见，请更换")
    if len(set(password)) == 1:
        raise PasswordPolicyError("密码不能是单一字符的重复")
    if username:
        lowered_password, lowered_username = password.lower(), username.lower()
        if lowered_username in lowered_password or lowered_password in lowered_username:
            raise PasswordPolicyError("密码不得包含登录名")

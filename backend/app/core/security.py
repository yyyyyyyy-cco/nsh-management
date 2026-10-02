"""安全工具：密码哈希（bcrypt）与 JWT 令牌。"""
import re
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    """bcrypt 哈希（`$2b$`，默认 cost 12）。

    **2026-10-03（W1-10）**：由**未维护的 `passlib`**（上游 2020 年后无发布，且被 bcrypt ≥4.1 破坏
    `__about__` 属性）改为**直接使用 `bcrypt`**。既有库内哈希**无需迁移**，已用真实哈希验证：
    passlib 产出 `$2b$12$…`（60 字符）可被 `bcrypt.checkpw` 校验通过，且 `bcrypt.gensalt()` 默认同样产出 `$2b$12$`；
    向后兼容由 `tests/test_password_hash_compat.py` 用 passlib 生成的固定哈希长期看护。

    **已知边界（登记 F-57 / W1-12）**：bcrypt 原生只使用口令的**前 72 字节**且**静默截断**——
    实测"前 72 字节相同、后缀不同"的两个口令互相通过校验。当前策略上限是 **128 字符**（中文可达 384 字节），
    故该边界可达；修法（收紧为 72 字节上限，或先 SHA-256 预哈希并给哈希加版本前缀）与 bcrypt 5.0 的行为变化
    一并放在 W1-12 处理，避免"升级即改变长口令行为"。
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


# bcrypt 哈希格式：$2a/$2b/$2y + cost(2 位) + 22 字符盐 + 31 字符摘要 = 60 字符
_BCRYPT_HASH_RE = re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")


def _is_bcrypt_hash(value: object) -> bool:
    return isinstance(value, str) and bool(_BCRYPT_HASH_RE.match(value))


def verify_password(plain: str, hashed: str) -> bool:
    """校验口令；哈希缺失/损坏/格式非法时返回 **False**，不向调用方抛异常。

    **为什么要做格式预校验（2026-10-03，W1-10 过程中发现）**：`bcrypt` 的 Rust 实现（4.x）
    在收到**截断/非法**哈希时会 **Rust panic**（`pyo3_runtime.PanicException: range end index 22 out of range …`），
    既不是 `ValueError` 也不是 `TypeError`——若直接交给它，**库中任一损坏哈希都会让登录接口 500**。
    而 passlib 时代对这类输入是**返回 False**（passlib 先自行解析哈希），故这里必须保持同一容错语义。
    预校验把非法格式挡在库外（同时避免 Rust panic 直接打到 stderr/日志），宽捕获作为兜底，
    并显式重抛 `KeyboardInterrupt`/`SystemExit`（不吞掉进程级信号）。
    """
    if not _is_bcrypt_hash(hashed):
        return False
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("ascii"))
    except BaseException as exc:  # noqa: BLE001 — 底层 panic 非 Exception 子类，见上方说明
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        return False


def create_access_token(user_id: int, role: str, token_version: int = 0) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    # ver：令牌吊销版本号，与 users.token_version 比对，登出/改密后旧 Token 立即失效
    payload = {"sub": str(user_id), "role": role, "ver": token_version, "exp": expire}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict | None:
    """解码 JWT，失败返回 None。"""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

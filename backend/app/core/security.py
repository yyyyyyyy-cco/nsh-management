"""安全工具：密码哈希（bcrypt）与 JWT 令牌。"""
import re
from datetime import datetime, timedelta, timezone

import base64
import hashlib

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings

def hash_password(password: str) -> str:
    """bcrypt 哈希（`$2b$`，默认 cost 12）。

    **2026-10-03（W1-10）**：由**未维护的 `passlib`**（上游 2020 年后无发布，且被 bcrypt ≥4.1 破坏
    `__about__` 属性）改为**直接使用 `bcrypt`**。既有库内哈希**无需迁移**，已用真实哈希验证：
    passlib 产出 `$2b$12$…`（60 字符）可被 `bcrypt.checkpw` 校验通过，且 `bcrypt.gensalt()` 默认同样产出 `$2b$12$`；
    向后兼容由 `tests/test_password_hash_compat.py` 用 passlib 生成的固定哈希长期看护。

    **F-57 已修（W1-12）**：新哈希先做 `base64(SHA-256(口令))` 预哈希（见 `_prehash`），任意长度口令都被完整使用；历史哈希（无前缀）仍走直连 bcrypt，故既有用户登录不受影响。
    """
    return _SCHEME_PREFIX + bcrypt.hashpw(
        _prehash(password).encode("ascii"), bcrypt.gensalt()
    ).decode("ascii")


# 哈希方案前缀（2026-10-03，W1-12）：新哈希形如 `sha256$<bcrypt>`；**旧哈希无前缀**，仍按直连 bcrypt 校验。
_SCHEME_PREFIX = "sha256$"

# bcrypt 哈希格式：$2a/$2b/$2y + cost(2 位) + 22 字符盐 + 31 字符摘要 = 60 字符
_BCRYPT_HASH_RE = re.compile(r"^\$2[aby]\$\d{2}\$[./A-Za-z0-9]{53}$")


def _prehash(password: str) -> str:
    """口令预哈希：`base64(SHA-256(口令))`，输出 44 字符（< bcrypt 的 72 字节上限）。

    **为什么要它（W1-12 / F-57）**：bcrypt 只使用输入的**前 72 字节**且在 4.x 下**静默截断**——
    实测「前 72 字节相同、后缀不同」的两个口令会互相通过校验；而 bcrypt **5.0.0** 改为直接报错
    （`password cannot be longer than 72 bytes`，连 `checkpw` 也报），若不预哈希就升级会**锁死**既有超长口令用户。
    采用 OWASP《Password Storage Cheat Sheet》对 bcrypt 的标准做法：先 SHA-256 再 base64（base64 避免 NUL 字节），
    这样任意长度口令都被**完整**参与哈希，同时保持 72 字节以内的库输入。

    **为什么不改策略上限**：把策略收紧到 72 字节会让中文口令最多只剩 24 个字符，
    反而**违反 ASVS 6.2.9**（必须允许 ≥64 字符）——故策略保持 128 字符，改用预哈希解决。
    """
    digest = hashlib.sha256(password.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


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
    if not isinstance(hashed, str):
        return False
    if hashed.startswith(_SCHEME_PREFIX):
        # 新方案：口令先 SHA-256 + base64（44 字符 < 72 字节），故任意长度都被**完整**使用
        candidate = _prehash(plain)
        stored = hashed[len(_SCHEME_PREFIX):]
    else:
        # 旧方案（直连 bcrypt，含 passlib 时代）：行为保持不变 → 既有用户不受影响
        candidate, stored = plain, hashed
    if not _is_bcrypt_hash(stored):
        return False
    try:
        return bcrypt.checkpw(candidate.encode("utf-8"), stored.encode("ascii"))
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

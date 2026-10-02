"""权限依赖矩阵回归（W2-2）。

覆盖 `backend/app/api/deps.py` 的令牌链路与 6 个角色依赖，
权威源：`design-document-v2.md` §3（角色权限矩阵）、`memory-bank/security-review.md`（越权修复记录）。

说明：直连依赖函数（不经 HTTP），用真实 JWT + 内存库，故无需启动服务。
"""
import unittest

from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from starlette.requests import Request

from app.api.deps import (
    get_current_user,
    require_admin,
    require_admin_strict,
    require_developer,
    require_member,
    require_member_or_admin,
)
from app.core.security import create_access_token
from support import DbTestCase


def make_request(token: str | None = None) -> Request:
    headers = []
    if token:
        headers.append((b"authorization", f"Bearer {token}".encode()))
    return Request({"type": "http", "method": "GET", "path": "/", "headers": headers})


class TokenChainTests(DbTestCase):
    """get_current_user：无凭据/坏令牌/版本不符/账号停用 一律 401；正常令牌写入 request.state。"""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.users = await self.seed_users()

    async def _resolve(self, credentials: HTTPAuthorizationCredentials | None):
        request = make_request(credentials.credentials if credentials else None)
        return await get_current_user(request, credentials, self.session)

    async def test_missing_credentials_returns_401(self):
        with self.assertRaises(HTTPException) as ctx:
            await self._resolve(None)
        self.assertEqual(ctx.exception.status_code, 401)

    async def test_invalid_token_returns_401(self):
        for bad in ("not-a-token", "a.b.c", ""):
            credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=bad)
            with self.subTest(token=bad), self.assertRaises(HTTPException) as ctx:
                await self._resolve(credentials)
            self.assertEqual(ctx.exception.status_code, 401)

    async def test_stale_token_version_returns_401(self):
        user = self.users[1]
        stale = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=create_access_token(user.id, user.role, user.token_version + 1)
        )
        with self.assertRaises(HTTPException) as ctx:
            await self._resolve(stale)
        self.assertEqual(ctx.exception.status_code, 401)

    async def test_unknown_user_id_returns_401(self):
        ghost = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=create_access_token(9999, "admin", 0)
        )
        with self.assertRaises(HTTPException) as ctx:
            await self._resolve(ghost)
        self.assertEqual(ctx.exception.status_code, 401)

    async def test_disabled_user_returns_401(self):
        disabled = self.users[5]
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token_for(disabled))
        with self.assertRaises(HTTPException) as ctx:
            await self._resolve(credentials)
        self.assertEqual(ctx.exception.status_code, 401)

    async def test_valid_token_returns_user_and_sets_request_state(self):
        user = self.users[3]
        request = make_request(self.token_for(user))
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token_for(user))
        resolved = await get_current_user(request, credentials, self.session)
        self.assertEqual(resolved.id, user.id)
        self.assertEqual(resolved.role, "member")
        self.assertIs(request.state.user, resolved, "应写入 request.state.user 供审计中间件复用")


class RoleMatrixTests(DbTestCase):
    """角色依赖：按 design-document-v2 §3 的角色定义逐项断言允许/拒绝。"""

    async def asyncSetUp(self) -> None:
        await super().asyncSetUp()
        self.users = await self.seed_users()

    async def _load(self, user_id: int):
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=self.token_for(self.users[user_id]))
        return await get_current_user(make_request(credentials.credentials), credentials, self.session)

    async def _assert_allowed(self, dependency, user_id: int):
        user = await self._load(user_id)
        resolved = await dependency(user)
        self.assertEqual(resolved.id, user.id)

    async def _assert_denied(self, dependency, user_id: int, status: int = 403):
        user = await self._load(user_id)
        with self.assertRaises(HTTPException) as ctx:
            await dependency(user)
        self.assertEqual(ctx.exception.status_code, status)

    async def test_require_admin_allows_admin_and_developer(self):
        await self._assert_allowed(require_admin, 1)   # admin（已绑定帮会）
        await self._assert_allowed(require_admin, 4)   # admin（未绑定帮会）——本依赖不校验帮会绑定
        await self._assert_allowed(require_admin, 2)   # developer 视同管理员
        await self._assert_denied(require_admin, 3)    # member 拒绝

    async def test_require_developer_only_developer(self):
        await self._assert_allowed(require_developer, 2)
        await self._assert_denied(require_developer, 1)
        await self._assert_denied(require_developer, 3)

    async def test_require_member_only_member_with_guild(self):
        await self._assert_allowed(require_member, 3)
        await self._assert_denied(require_member, 1)
        await self._assert_denied(require_member, 2)

    async def test_require_admin_strict_excludes_developer_and_unbound(self):
        await self._assert_allowed(require_admin_strict, 1)
        await self._assert_denied(require_admin_strict, 2)   # developer 不属于帮会管理
        await self._assert_denied(require_admin_strict, 3)   # member
        await self._assert_denied(require_admin_strict, 4)   # 未绑定帮会 → 403

    async def test_require_member_or_admin(self):
        await self._assert_allowed(require_member_or_admin, 3)
        await self._assert_allowed(require_member_or_admin, 1)
        await self._assert_denied(require_member_or_admin, 2)
        await self._assert_denied(require_member_or_admin, 4)  # 未绑定帮会 → 403
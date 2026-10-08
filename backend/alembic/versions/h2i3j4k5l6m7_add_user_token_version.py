"""users 表添加 token_version 令牌吊销版本号。

登出/修改密码时自增，旧 Token 的 ver 声明与数据库不一致即判 401，实现 JWT 吊销。

Revision ID: h2i3j4k5l6m7
Revises: g1h2i3j4k5l6
Create Date: 2026-08-20 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'h2i3j4k5l6m7'
down_revision: Union[str, None] = 'g1h2i3j4k5l6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 token_version 列（SQLite 加 NOT NULL 列需带 server_default）。"""
    op.add_column(
        "users",
        sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """回滚：删除 token_version 列。"""
    op.drop_column("users", "token_version")

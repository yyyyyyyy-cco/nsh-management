"""添加开发者角色，guild_id 改为可空。

Revision ID: e5f6a7b8c9d0
Revises: c284e8a7e534
Create Date: 2026-08-17 10:50:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'c284e8a7e534'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """SQLite 不支持 ALTER COLUMN，需要重建表。"""
    # 创建临时表
    op.execute("""
        CREATE TABLE users_new (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            username VARCHAR(64) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            plain_password VARCHAR(128),
            role VARCHAR(16) NOT NULL DEFAULT 'member',
            status VARCHAR(16) NOT NULL DEFAULT 'active',
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(guild_id) REFERENCES guilds(id)
        )
    """)

    # 复制数据
    op.execute("""
        INSERT INTO users_new (id, guild_id, username, password_hash, plain_password, role, status, failed_attempts, locked_until, created_at)
        SELECT id, guild_id, username, password_hash, plain_password, role, status, failed_attempts, locked_until, created_at
        FROM users
    """)

    # 删除旧表
    op.execute("DROP TABLE users")

    # 重命名新表
    op.execute("ALTER TABLE users_new RENAME TO users")

    # 创建索引
    op.execute("CREATE INDEX ix_users_guild_id ON users(guild_id)")


def downgrade() -> None:
    """回滚：guild_id 改回 NOT NULL。"""
    # 删除没有 guild_id 的记录（开发者账号）
    op.execute("DELETE FROM users WHERE guild_id IS NULL")

    # 重建表，guild_id 设为 NOT NULL
    op.execute("""
        CREATE TABLE users_old (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER NOT NULL,
            username VARCHAR(64) NOT NULL UNIQUE,
            password_hash VARCHAR(128) NOT NULL,
            plain_password VARCHAR(128),
            role VARCHAR(16) NOT NULL DEFAULT 'member',
            status VARCHAR(16) NOT NULL DEFAULT 'active',
            failed_attempts INTEGER NOT NULL DEFAULT 0,
            locked_until DATETIME,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(guild_id) REFERENCES guilds(id)
        )
    """)

    op.execute("""
        INSERT INTO users_old (id, guild_id, username, password_hash, plain_password, role, status, failed_attempts, locked_until, created_at)
        SELECT id, guild_id, username, password_hash, plain_password, role, status, failed_attempts, locked_until, created_at
        FROM users
    """)

    op.execute("DROP TABLE users")
    op.execute("ALTER TABLE users_old RENAME TO users")
    op.execute("CREATE INDEX ix_users_guild_id ON users(guild_id)")

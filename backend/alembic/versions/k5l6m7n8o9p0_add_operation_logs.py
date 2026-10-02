"""新增 operation_logs 操作日志表。

Revision ID: k5l6m7n8o9p0
Revises: j4k5l6m7n8o9
Create Date: 2026-09-07 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'k5l6m7n8o9p0'
down_revision: Union[str, None] = 'j4k5l6m7n8o9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 operation_logs 表及常用查询索引。"""
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=64), nullable=True),
        sa.Column('role', sa.String(length=16), nullable=True),
        sa.Column('guild_id', sa.Integer(), nullable=True),
        sa.Column('module', sa.String(length=32), nullable=False),
        sa.Column('action', sa.String(length=32), nullable=False),
        sa.Column('method', sa.String(length=8), nullable=False),
        sa.Column('path', sa.String(length=255), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('level', sa.String(length=16), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('ip', sa.String(length=64), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_operation_logs_username', 'operation_logs', ['username'])
    op.create_index('ix_operation_logs_guild_id', 'operation_logs', ['guild_id'])
    op.create_index('ix_operation_logs_module', 'operation_logs', ['module'])
    op.create_index('ix_operation_logs_level', 'operation_logs', ['level'])
    op.create_index('ix_operation_logs_created_at', 'operation_logs', ['created_at'])


def downgrade() -> None:
    """回滚：删除 operation_logs 表。"""
    op.drop_table('operation_logs')

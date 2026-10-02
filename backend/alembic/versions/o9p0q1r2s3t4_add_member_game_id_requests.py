"""member_game_id_requests 表：游戏 ID 修改申请（帮众提交、管理员审核）。

Revision ID: o9p0q1r2s3t4
Revises: n8o9p0q1r2s3
Create Date: 2026-09-20 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'o9p0q1r2s3t4'
down_revision: Union[str, None] = 'n8o9p0q1r2s3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """新建申请表（SQLite 需在建表时一次定义 CHECK/唯一约束），随后创建查询与部分索引。"""
    op.create_table(
        'member_game_id_requests',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('guild_id', sa.Integer(), sa.ForeignKey('guilds.id'), nullable=False),
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('members.id'), nullable=True),
        sa.Column('old_game_id', sa.String(length=32), nullable=False),
        sa.Column('new_game_id', sa.String(length=32), nullable=False),
        sa.Column('requester_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('requester_username', sa.String(length=64), nullable=False),
        sa.Column('status', sa.String(length=16), nullable=False, server_default='pending'),
        sa.Column('reviewer_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewer_username', sa.String(length=64), nullable=True),
        sa.Column('review_remark', sa.String(length=255), nullable=True),
        sa.Column('invalidated_reason', sa.String(length=32), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending','approved','rejected','invalidated')",
            name='ck_game_id_requests_status',
        ),
        sa.CheckConstraint('length(old_game_id) BETWEEN 1 AND 32', name='ck_game_id_requests_old_len'),
        sa.CheckConstraint('length(new_game_id) BETWEEN 1 AND 32', name='ck_game_id_requests_new_len'),
    )
    op.create_index('ix_member_game_id_requests_guild_id', 'member_game_id_requests', ['guild_id'])
    op.create_index(
        'ix_game_id_requests_guild_status_created',
        'member_game_id_requests',
        ['guild_id', 'status', 'created_at', 'id'],
    )
    op.create_index(
        'ix_game_id_requests_guild_member_created',
        'member_game_id_requests',
        ['guild_id', 'member_id', 'created_at', 'id'],
    )
    op.create_index('ix_game_id_requests_requester', 'member_game_id_requests', ['requester_id'])
    op.create_index('ix_game_id_requests_reviewer', 'member_game_id_requests', ['reviewer_id'])
    op.create_index(
        'uq_game_id_requests_pending_member',
        'member_game_id_requests',
        ['guild_id', 'member_id'],
        unique=True,
        sqlite_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        'ix_game_id_requests_old_approved',
        'member_game_id_requests',
        ['guild_id', 'old_game_id'],
        sqlite_where=sa.text("status = 'approved'"),
    )
    op.create_index(
        'ix_game_id_requests_new_approved',
        'member_game_id_requests',
        ['guild_id', 'new_game_id'],
        sqlite_where=sa.text("status = 'approved'"),
    )


def downgrade() -> None:
    """回滚：撤销索引与申请表；已生效的成员改名不回滚（须另行处理）。"""
    op.drop_index('ix_game_id_requests_new_approved', table_name='member_game_id_requests')
    op.drop_index('ix_game_id_requests_old_approved', table_name='member_game_id_requests')
    op.drop_index('uq_game_id_requests_pending_member', table_name='member_game_id_requests')
    op.drop_index('ix_game_id_requests_reviewer', table_name='member_game_id_requests')
    op.drop_index('ix_game_id_requests_requester', table_name='member_game_id_requests')
    op.drop_index('ix_game_id_requests_guild_member_created', table_name='member_game_id_requests')
    op.drop_index('ix_game_id_requests_guild_status_created', table_name='member_game_id_requests')
    op.drop_index('ix_member_game_id_requests_guild_id', table_name='member_game_id_requests')
    op.drop_table('member_game_id_requests')

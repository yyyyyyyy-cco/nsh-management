"""新增 squad_adjustments 分析调整副本表。

存储小队分析内「未排表成员 → 目标队伍」的手动分配映射，与正式排表完全独立。

Revision ID: i3j4k5l6m7n8
Revises: h2i3j4k5l6m7
Create Date: 2026-08-26 16:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'i3j4k5l6m7n8'
down_revision: Union[str, None] = 'h2i3j4k5l6m7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建 squad_adjustments 表。"""
    op.create_table(
        'squad_adjustments',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('schedule_id', sa.Integer(), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['schedule_id'], ['schedules.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('schedule_id'),
    )


def downgrade() -> None:
    """回滚：删除 squad_adjustments 表。"""
    op.drop_table('squad_adjustments')

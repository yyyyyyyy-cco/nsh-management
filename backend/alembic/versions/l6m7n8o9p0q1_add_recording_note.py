"""recordings 表新增 note 备注列（帮众提交，展示层对帮众脱敏）。

Revision ID: l6m7n8o9p0q1
Revises: k5l6m7n8o9p0
Create Date: 2026-09-11 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'l6m7n8o9p0q1'
down_revision: Union[str, None] = 'k5l6m7n8o9p0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """新增 note 列（SQLite 支持 ALTER TABLE ADD COLUMN，无需约束变更）。"""
    op.add_column('recordings', sa.Column('note', sa.Text(), nullable=True))


def downgrade() -> None:
    """回滚：删除 note 列。"""
    op.drop_column('recordings', 'note')

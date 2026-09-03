"""新增 schedules.profession_config 单场职业配置覆盖列。

JSON 字典 {职业: 目标人数}，NULL 表示未覆盖、沿用系统配置。

Revision ID: j4k5l6m7n8o9
Revises: i3j4k5l6m7n8
Create Date: 2026-09-01 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'j4k5l6m7n8o9'
down_revision: Union[str, None] = 'i3j4k5l6m7n8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """schedules 表新增 profession_config JSON 可空列。"""
    op.add_column('schedules', sa.Column('profession_config', sa.JSON(), nullable=True))


def downgrade() -> None:
    """回滚：删除 profession_config 列。"""
    op.drop_column('schedules', 'profession_config')

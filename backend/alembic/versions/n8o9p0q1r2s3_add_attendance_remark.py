"""attendance_records 表新增 remark 备注列（导入时常驻库带入，出勤库内可修改）。

Revision ID: n8o9p0q1r2s3
Revises: m7n8o9p0q1r2
Create Date: 2026-09-11 16:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'n8o9p0q1r2s3'
down_revision: Union[str, None] = 'm7n8o9p0q1r2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """新增 remark 列（SQLite 支持 ALTER TABLE ADD COLUMN，无需约束变更）。"""
    op.add_column('attendance_records', sa.Column('remark', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """回滚：删除 remark 列。"""
    op.drop_column('attendance_records', 'remark')

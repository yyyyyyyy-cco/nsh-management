"""match_data 表添加局号字段 round_no，旧数据默认归为第 1 局。

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-08-19 10:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'dbb752d924fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 round_no 列（默认 1，历史数据归为第 1 局）并创建索引。"""
    op.add_column(
        "match_data",
        sa.Column("round_no", sa.Integer(), nullable=False, server_default="1"),
    )
    op.create_index("ix_match_data_round_no", "match_data", ["round_no"])


def downgrade() -> None:
    """回滚：删除索引与 round_no 列。"""
    op.drop_index("ix_match_data_round_no", table_name="match_data")
    op.drop_column("match_data", "round_no")

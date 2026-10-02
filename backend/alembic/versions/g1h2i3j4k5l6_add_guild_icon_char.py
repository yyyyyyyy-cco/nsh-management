"""guilds 表添加图标字 icon_char，用于侧边栏折叠按钮显示首字。

Revision ID: g1h2i3j4k5l6
Revises: f6a7b8c9d0e1
Create Date: 2026-08-20 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'g1h2i3j4k5l6'
down_revision: Union[str, None] = 'f6a7b8c9d0e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """添加 icon_char 列（可空，存储单个显示字符）。"""
    op.add_column(
        "guilds",
        sa.Column("icon_char", sa.String(length=4), nullable=True),
    )


def downgrade() -> None:
    """回滚：删除 icon_char 列。"""
    op.drop_column("guilds", "icon_char")

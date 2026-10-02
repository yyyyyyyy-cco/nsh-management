"""为 profession_configs 增加 remark 列（职业说明，可编辑）。

Revision ID: a1b2c3d4e5f6
Revises: e5f6a7b8c9d0
Create Date: 2026-08-17 20:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """SQLite 支持 ALTER TABLE ADD COLUMN。"""
    op.add_column("profession_configs", sa.Column("remark", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("profession_configs", "remark")

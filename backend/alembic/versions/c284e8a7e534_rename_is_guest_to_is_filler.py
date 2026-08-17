"""rename_is_guest_to_is_filler

Revision ID: c284e8a7e534
Revises: 7b834378524f
Create Date: 2026-08-11 16:13:12.207679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c284e8a7e534'
down_revision: Union[str, None] = '7b834378524f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """术语变更：客人(guest) → 补人(filler)。"""
    op.alter_column("attendance_records", "is_guest", new_column_name="is_filler")


def downgrade() -> None:
    op.alter_column("attendance_records", "is_filler", new_column_name="is_guest")

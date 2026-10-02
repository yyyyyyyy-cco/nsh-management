"""2026-10-03：为「补人」补上文档（database-design §2.6/§2.8 唯一约束行）声称的部分唯一索引。

背景（F-79）：文档写明
  - attendance_records：`(schedule_id, member_id)`（常驻成员每场一条）；`(schedule_id, member_name, is_filler=1)`
    （补人按姓名每场一条，**SQLite 通过部分唯一索引实现**）
  - recordings：`(schedule_id, member_id, round_number)`；补人按 `(schedule_id, member_name, round_number)`
但迁移后的真实库里**只有**含 `member_id` 的那一条唯一约束（NULL 在 SQLite 中互不冲突），
补人维度**没有**任何数据库级约束——仅靠 `attendance_service.add_filler` 的应用层名称查重（存在竞态）。
本迁移补上两条部分唯一索引，使约束与文档一致。

注意：若既有库中已存在重复补人行，`CREATE UNIQUE INDEX` 会失败——届时需先人工去重（本项目自托管，
数据量小，且历史上补人由应用层查重写入，重复概率低）。

Revision ID: p0q1r2s3t4u5
Revises: o9p0q1r2s3t4
"""
from alembic import op
from sqlalchemy import text as sa_text

revision = "p0q1r2s3t4u5"
down_revision = "o9p0q1r2s3t4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "uq_attendance_filler_schedule_name",
        "attendance_records",
        ["schedule_id", "member_name"],
        unique=True,
        sqlite_where=sa_text("is_filler = 1"),
    )
    op.create_index(
        "uq_recording_filler_schedule_name_round",
        "recordings",
        ["schedule_id", "member_name", "round_number"],
        unique=True,
        sqlite_where=sa_text("member_id IS NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_recording_filler_schedule_name_round", table_name="recordings")
    op.drop_index("uq_attendance_filler_schedule_name", table_name="attendance_records")

"""游戏 ID 修改申请表：帮众提交、管理员审核；approved 记录兼作战绩新旧 ID 关联来源。

设计依据：memory-bank/design-game-id-change.md；表结构见 database-design.md §2.12。
"""

from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base

# 申请状态：待审核 / 已通过 / 已驳回 / 自动失效（成员被直接改名或删除）
REQUEST_STATUSES = ("pending", "approved", "rejected", "invalidated")
# 自动失效原因
INVALIDATED_REASONS = ("member_renamed", "member_deleted")


class MemberGameIdRequest(Base):
    __tablename__ = "member_game_id_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"), nullable=False, index=True)
    # 目标常驻成员；成员删除后置空，避免主键复用导致误关联
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True)
    old_game_id: Mapped[str] = mapped_column(String(32), nullable=False)  # 提交时从成员表读取的快照
    new_game_id: Mapped[str] = mapped_column(String(32), nullable=False)
    requester_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    requester_username: Mapped[str] = mapped_column(String(64), nullable=False)  # 账号名快照
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)
    reviewer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewer_username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    review_remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    invalidated_reason: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','approved','rejected','invalidated')",
            name="ck_game_id_requests_status",
        ),
        CheckConstraint("length(old_game_id) BETWEEN 1 AND 32", name="ck_game_id_requests_old_len"),
        CheckConstraint("length(new_game_id) BETWEEN 1 AND 32", name="ck_game_id_requests_new_len"),
        Index("ix_game_id_requests_guild_status_created", "guild_id", "status", "created_at", "id"),
        Index("ix_game_id_requests_guild_member_created", "guild_id", "member_id", "created_at", "id"),
        Index("ix_game_id_requests_requester", "requester_id"),
        Index("ix_game_id_requests_reviewer", "reviewer_id"),
        # 数据库层兜底：同一成员同时最多一条待审核申请
        Index(
            "uq_game_id_requests_pending_member",
            "guild_id",
            "member_id",
            unique=True,
            sqlite_where=text("status = 'pending'"),
        ),
        # approved 记录的战绩关联定位与冲突检测
        Index(
            "ix_game_id_requests_old_approved",
            "guild_id",
            "old_game_id",
            sqlite_where=text("status = 'approved'"),
        ),
        Index(
            "ix_game_id_requests_new_approved",
            "guild_id",
            "new_game_id",
            sqlite_where=text("status = 'approved'"),
        ),
    )

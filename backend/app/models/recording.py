"""录屏表：按局数提交链接，审核状态流转。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Recording(Base):
    __tablename__ = "recordings"
    __table_args__ = (
        UniqueConstraint("schedule_id", "member_id", "round_number", name="uq_recording_schedule_member_round"),
        # 补人按 (schedule_id, member_name, round_number) 唯一（部分唯一索引；与迁移一致，见 F-79）
        Index("uq_recording_filler_schedule_name_round", "schedule_id", "member_name",
              "round_number", unique=True, sqlite_where=text("member_id IS NULL")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False, index=True)
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True, index=True)
    member_name: Mapped[str] = mapped_column(String(32), nullable=False)
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)  # 第几局
    url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)  # 帮众备注（展示层对帮众脱敏，仅管理员可见）
    status: Mapped[str] = mapped_column(String(16), default="pending", nullable=False, index=True)  # pending / approved / rejected
    review_remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

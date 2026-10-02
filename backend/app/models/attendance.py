"""出勤记录表：补人以姓名快照存储，不关联常驻库。"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AttendanceRecord(Base):
    __tablename__ = "attendance_records"
    __table_args__ = (
        UniqueConstraint("schedule_id", "member_id", name="uq_attendance_schedule_member"),
        # 补人按姓名每场一条（部分唯一索引；与迁移 p0q1r2s3t4u5 一致，见 database-design §2.6 / F-79）
        Index("uq_attendance_filler_schedule_name", "schedule_id", "member_name", unique=True,
              sqlite_where=text("is_filler = 1")),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False, index=True)
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id"), nullable=True, index=True)
    member_name: Mapped[str] = mapped_column(String(32), nullable=False)  # 姓名快照
    profession: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), default="normal", nullable=False)  # normal / leave
    is_filler: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # 补人（非帮会成员）
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 备注（导入时带出常驻库备注，出勤库内可改）
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

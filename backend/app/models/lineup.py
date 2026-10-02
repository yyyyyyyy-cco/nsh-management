"""排表表：与赛程 1:1，60 槽位数据以 JSON 存储。"""
from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lineup(Base):
    __tablename__ = "lineups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), unique=True, nullable=False)
    data: Mapped[list] = mapped_column(JSON, nullable=False)  # 10 队 × 6 槽位
    title_remark: Mapped[str | None] = mapped_column(String(255), nullable=True, default="")
    groups_remark: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )

"""常驻库成员表。"""
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    main_profession: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
    sub_profession: Mapped[str | None] = mapped_column(String(16), nullable=True)
    status: Mapped[str] = mapped_column(String(16), default="formal", nullable=False, index=True)  # formal / substitute
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

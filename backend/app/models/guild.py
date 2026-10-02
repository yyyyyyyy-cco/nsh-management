"""帮会表。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Guild(Base):
    __tablename__ = "guilds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    icon_char: Mapped[str | None] = mapped_column(String(4), nullable=True)  # 侧边栏折叠按钮显示的首字
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

"""账号表：每个帮会一个管理员账号 + 一个帮众共享账号。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int | None] = mapped_column(ForeignKey("guilds.id"), nullable=True, index=True)  # developer 角色可为空
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    plain_password: Mapped[str | None] = mapped_column(String(128), nullable=True)  # 仅限本地管理工具查看
    role: Mapped[str] = mapped_column(String(16), default="member", nullable=False)  # developer / admin / member
    status: Mapped[str] = mapped_column(String(16), default="active", nullable=False)  # active / disabled
    failed_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    locked_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

    guild: Mapped["Guild | None"] = relationship("Guild", foreign_keys=[guild_id], lazy="joined")

    @property
    def guild_name(self) -> str | None:
        """所属帮会名称（开发者无帮会时为 None）。"""
        return self.guild.name if self.guild else None

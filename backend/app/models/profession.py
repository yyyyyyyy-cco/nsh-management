"""职业配置表：各职业目标人数，按帮会隔离。"""
from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ProfessionConfig(Base):
    __tablename__ = "profession_configs"
    __table_args__ = (UniqueConstraint("guild_id", "profession", name="uq_profession_guild"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"), nullable=False)
    profession: Mapped[str] = mapped_column(String(16), nullable=False)
    target_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    remark: Mapped[str | None] = mapped_column(String(255), nullable=True)  # 职业说明（可编辑）

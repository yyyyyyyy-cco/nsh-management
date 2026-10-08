"""赛程表：局数创建后不可修改，每局结果以 JSON 存储。"""

from datetime import UTC, datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Schedule(Base):
    __tablename__ = "schedules"
    __table_args__ = (CheckConstraint("rounds BETWEEN 1 AND 3", name="ck_schedule_rounds"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(ForeignKey("guilds.id"), nullable=False, index=True)
    opponent: Mapped[str] = mapped_column(String(64), nullable=False)
    match_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)
    rounds: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-3，创建后不可修改
    result: Mapped[str] = mapped_column(String(16), default="pending", nullable=False)  # win / lose / draw / pending
    round_results: Mapped[list | None] = mapped_column(JSON, nullable=True)  # 每局结果，如 ["win","lose","pending"]
    profession_config: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )  # 单场职业配置覆盖 {职业: 目标人数}，NULL 沿用系统配置
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False
    )

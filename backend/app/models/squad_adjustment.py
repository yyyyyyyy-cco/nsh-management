"""分析调整副本表：小队分析内「未排表成员 → 目标队伍」的临时分配。

与正式排表（lineups）完全独立，修改仅作用于小队分析视图，不改变最终排表。
"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SquadAdjustment(Base):
    __tablename__ = "squad_adjustments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), unique=True, nullable=False)
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # {player_name: "category:team_index"}
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

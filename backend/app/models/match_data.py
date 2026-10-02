"""比赛数据表：CSV 导入，字段与真实导出列一一对应。"""
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MatchData(Base):
    __tablename__ = "match_data"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False, index=True)
    round_no: Mapped[int] = mapped_column(Integer, default=1, nullable=False, index=True)  # 第几局（1~rounds）
    player_name: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # 个人战绩按名查询
    profession: Mapped[str | None] = mapped_column(String(16), nullable=True)
    camp: Mapped[str] = mapped_column(String(32), nullable=False)  # CSV 区块标题，第一块为己方
    kills: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 击败+清泉合计
    springs: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 清泉原始分量
    assists: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    resource: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    player_damage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    armor_break_damage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    building_damage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tower_break_damage: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    healing: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    damage_taken: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deaths: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 重伤=死亡数
    revives: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 复活/清泉（单值）
    fen_gu: Mapped[int] = mapped_column(Integer, default=0, nullable=False)  # 独立焚骨榜
    extra_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 预留 CSV 新增列
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )

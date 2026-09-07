"""操作日志表：写操作审计与错误落库，供开发者查看。"""
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 匿名请求为空
    username: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    role: Mapped[str | None] = mapped_column(String(16), nullable=True)
    guild_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    module: Mapped[str] = mapped_column(String(32), nullable=False, index=True)  # member/schedule/.../other
    action: Mapped[str] = mapped_column(String(32), nullable=False)  # create/update/delete/login/.../other
    method: Mapped[str] = mapped_column(String(8), nullable=False)
    path: Mapped[str] = mapped_column(String(255), nullable=False)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)  # 异常中断时为空
    level: Mapped[str] = mapped_column(String(16), nullable=False, index=True)  # info / warning / error
    detail: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON 文本，敏感字段已脱敏
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True
    )

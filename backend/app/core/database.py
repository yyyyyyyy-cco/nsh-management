"""数据库连接：异步引擎、Session 工厂、ORM 基类。"""
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # SQLite 写事务等待锁的超时（秒），避免并发写入直接报 "database is locked"
    connect_args={"timeout": 30} if _is_sqlite(settings.DATABASE_URL) else {},
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


if _is_sqlite(settings.DATABASE_URL):
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:  # noqa: ANN001
        """每条连接生效的 SQLite PRAGMA：
        - WAL：读写不互斥（默认 delete 模式下写事务阻塞全部读）
        - synchronous=NORMAL：WAL 下的推荐档位，兼顾安全与写入性能
        - busy_timeout：锁等待重试，配合 connect timeout 进一步降低锁冲突
        """
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA busy_timeout=30000")
        cursor.close()


async def get_db() -> AsyncSession:
    """FastAPI 依赖：每个请求一个独立 Session。"""
    async with async_session_factory() as session:
        yield session

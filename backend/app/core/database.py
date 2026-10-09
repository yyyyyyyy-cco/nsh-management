"""数据库连接：异步引擎、Session 工厂、ORM 基类。"""

from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import AsyncAdaptedQueuePool

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _is_sqlite(url: str) -> bool:
    return url.startswith("sqlite")


_is_sqlite_db = _is_sqlite(settings.DATABASE_URL)
# 连接池仅用于文件型 SQLite：内存库（:memory:）每个连接是独立空库，多连接池语义错误
_sqlite_file_db = _is_sqlite_db and ":memory:" not in settings.DATABASE_URL

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    # SQLite 写事务等待锁的超时（秒），避免并发写入直接报 "database is locked"
    connect_args={"timeout": 30} if _is_sqlite_db else {},
    # 连接池（2026-10-09 性能优化）：文件型 SQLite 的异步方言默认 NullPool——每个请求新建连接
    # + 重跑三条 PRAGMA + aiosqlite 线程启停；实测单请求周期 ~6ms，而查询本身仅亚毫秒，连接开销
    # 占延迟大头。改为小连接池复用（实测 10 个请求周期由 10 次建连降为 1 次）。语义不变：PRAGMA
    # 监听器仅在建新连接时执行；WAL 持久于库文件；单写者由 busy_timeout 兜底（部署本就单 worker）。
    **({"poolclass": AsyncAdaptedQueuePool, "pool_size": 5, "max_overflow": 10} if _sqlite_file_db else {}),
)
async_session_factory = async_sessionmaker(engine, expire_on_commit=False)


if _is_sqlite_db:

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


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI 依赖：每个请求一个独立 Session。"""
    async with async_session_factory() as session:
        yield session

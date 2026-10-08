"""审计日志概览统计的时间口径回归测试（F-87）。

口径（实现为准，本轮补记进 `database-design §2.11`）：
- 落库时间为 **naive UTC**；
- 「今日」按**北京时间（UTC+8）零点**划分，查询边界 = 北京零点 − 8 小时；
- 「近 7 天错误分布」按北京日期分组（SQL `date(created_at, '+8 hours')`），桶**由旧到新**共 7 个；
- 窗口起点 = 今日零点 − 6 天，更早的错误不计入。

本文件锁定午夜前后与窗口最旧一天两个易错边界（`get_log_stats` 此前无测试）。
"""

from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.database import Base
from app.models.operation_log import OperationLog
from app.services import log_service

STATS_TZ = timezone(timedelta(hours=8))


def _bj_today_start_naive_utc() -> datetime:
    """与实现同源：北京零点对应的 naive-UTC 时刻。"""
    now_bj = datetime.now(STATS_TZ).replace(tzinfo=None)
    return now_bj.replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(hours=8)


class _Base(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self.maker = async_sessionmaker(self.engine, expire_on_commit=False)
        self.session = self.maker()
        self.today_start = _bj_today_start_naive_utc()

    async def asyncTearDown(self) -> None:
        await self.session.close()
        await self.engine.dispose()

    async def _log(self, created_at: datetime, level: str = "info") -> None:
        self.session.add(
            OperationLog(
                username="u",
                module="other",
                action="update",
                method="PUT",
                path="/x",
                level=level,
                created_at=created_at,
            )
        )
        await self.session.commit()


class LogStatsTest(_Base):
    async def test_today_boundary_is_beijing_midnight(self) -> None:
        """北京零点前 1 秒不算今日；恰好到北京零点算今日。"""
        await self._log(self.today_start - timedelta(seconds=1))  # 北京昨日 23:59:59
        await self._log(self.today_start)  # 北京今日 00:00:00
        stats = await log_service.get_log_stats(self.session)
        self.assertEqual(stats["today_requests"], 1, "只有北京零点及之后的记录计入今日")

    async def test_today_errors_count(self) -> None:
        await self._log(self.today_start + timedelta(hours=1), level="info")
        await self._log(self.today_start + timedelta(hours=2), level="error")
        await self._log(self.today_start + timedelta(hours=3), level="error")
        await self._log(self.today_start - timedelta(days=1), level="error")  # 昨日（北京）
        stats = await log_service.get_log_stats(self.session)
        self.assertEqual(stats["today_requests"], 3)
        self.assertEqual(stats["today_errors"], 2, "昨日错误不计入今日")

    async def test_beijing_label_for_late_night_log(self) -> None:
        """北京 00:30 的记录（UTC 为前一日 16:30）应计入今日，并归到今日的北京日期桶。"""
        await self._log(self.today_start + timedelta(minutes=30), level="error")
        stats = await log_service.get_log_stats(self.session)
        self.assertEqual(stats["today_errors"], 1)
        today_bj = (self.today_start + timedelta(hours=8)).strftime("%Y-%m-%d")
        labels = [row["date"] for row in stats["weekly_errors"]]
        self.assertIn(today_bj, labels)
        self.assertEqual(dict((r["date"], r["count"]) for r in stats["weekly_errors"])[today_bj], 1)

    async def test_weekly_buckets_are_seven_oldest_first(self) -> None:
        stats = await log_service.get_log_stats(self.session)
        rows = stats["weekly_errors"]
        self.assertEqual(len(rows), 7, "近 7 天应有 7 个桶")
        labels = [r["date"] for r in rows]
        self.assertEqual(labels, sorted(labels), "桶应按日期升序（由旧到新）")
        self.assertEqual(
            labels[-1], (self.today_start + timedelta(hours=8)).strftime("%Y-%m-%d"), "最后一个桶是北京今日"
        )

    async def test_week_window_excludes_eighth_day(self) -> None:
        """窗口内（3 天前）计入；窗口外（8 天前）不计入。"""
        await self._log(self.today_start + timedelta(hours=9), level="error")  # 今日
        await self._log(self.today_start - timedelta(days=3) + timedelta(hours=9), level="error")
        await self._log(self.today_start - timedelta(days=8), level="error")  # 太早
        stats = await log_service.get_log_stats(self.session)
        counts = {r["date"]: r["count"] for r in stats["weekly_errors"]}
        self.assertEqual(sum(counts.values()), 2, "窗口外错误不计入分布")
        self.assertEqual(counts[((self.today_start + timedelta(hours=8)) - timedelta(days=3)).strftime("%Y-%m-%d")], 1)

    async def test_empty_database_returns_zeros(self) -> None:
        stats = await log_service.get_log_stats(self.session)
        self.assertEqual(stats["today_requests"], 0)
        self.assertEqual(stats["today_errors"], 0)
        self.assertEqual([r["count"] for r in stats["weekly_errors"]], [0] * 7)


if __name__ == "__main__":
    unittest.main()

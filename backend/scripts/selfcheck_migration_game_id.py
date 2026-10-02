"""Alembic 迁移隔离验证：临时库「空库升级 → 回退 → 再升级」，不接触业务库。

运行：backend/.venv/Scripts/python.exe backend/scripts/selfcheck_migration_game_id.py
校验：迁移链完整、member_game_id_requests 表与索引/部分唯一索引真实落库、downgrade 可回退。
"""
import os
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

HEAD_REVISION = "o9p0q1r2s3t4"
NEW_TABLE = "member_game_id_requests"


def _run_alembic(db_path: Path, *args: str) -> str:
    env = {**os.environ, "DATABASE_URL": f"sqlite+aiosqlite:///{db_path.as_posix()}"}
    result = subprocess.run(
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        raise AssertionError(f"alembic {' '.join(args)} 失败：\n{result.stdout}\n{result.stderr}")
    return f"{result.stdout}\n{result.stderr}"


def _table_names(db_path: Path) -> set[str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        return {row[0] for row in rows}
    finally:
        conn.close()


def _index_sql(db_path: Path) -> dict[str, str]:
    conn = sqlite3.connect(db_path)
    try:
        rows = conn.execute(
            "SELECT name, COALESCE(sql, '') FROM sqlite_master WHERE type='index' AND tbl_name=?",
            (NEW_TABLE,),
        ).fetchall()
        return {name: sql for name, sql in rows}
    finally:
        conn.close()


def _current_revision(db_path: Path) -> str:
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute("SELECT version_num FROM alembic_version").fetchone()[0]
    finally:
        conn.close()


def _fails_with_integrity(conn: sqlite3.Connection, sql: str, params: tuple) -> bool:
    """执行 INSERT，若被 CHECK/唯一索引拒绝返回 True。"""
    try:
        conn.execute(sql, params)
    except sqlite3.IntegrityError:
        return True
    return False


class MigrationTests(unittest.TestCase):
    def test_empty_database_upgrade_downgrade_reupgrade(self):
        with tempfile.TemporaryDirectory(prefix="nsh_mig_check_") as tmp:
            db_path = Path(tmp) / "migration.db"

            up_log = _run_alembic(db_path, "upgrade", "head")
            self.assertIn("Running upgrade", up_log)
            self.assertIn(HEAD_REVISION, up_log)
            self.assertEqual(_current_revision(db_path), HEAD_REVISION)
            self.assertIn(NEW_TABLE, _table_names(db_path))

            indexes = _index_sql(db_path)
            self.assertIn("uq_game_id_requests_pending_member", indexes)
            self.assertIn("WHERE status = 'pending'", indexes["uq_game_id_requests_pending_member"])
            self.assertIn("ix_game_id_requests_old_approved", indexes)
            self.assertIn("ix_game_id_requests_new_approved", indexes)
            self.assertIn(
                "WHERE status = 'approved'", indexes["ix_game_id_requests_new_approved"]
            )

            # 约束真实生效：状态白名单 + 同一成员仅一条待审
            now = "2026-09-20 00:00:00"
            insert_sql = (
                "INSERT INTO member_game_id_requests (guild_id, member_id, old_game_id, new_game_id,"
                " requester_username, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
            )
            conn = sqlite3.connect(db_path)
            try:
                conn.execute(insert_sql, (1, 1, "甲", "乙", "actor", "pending", now, now))
                self.assertTrue(_fails_with_integrity(conn, insert_sql, (1, 1, "甲", "丙", "actor", "pending", now, now)))
                self.assertTrue(_fails_with_integrity(conn, insert_sql, (1, 1, "甲", "乙", "actor", "bogus", now, now)))
                # 其他成员、其他状态不受唯一索引限制
                conn.execute(insert_sql, (1, 2, "戊", "己", "actor", "pending", now, now))
                conn.execute(insert_sql, (1, 1, "甲", "乙", "actor", "rejected", now, now))
                conn.rollback()
            finally:
                conn.close()

            down_log = _run_alembic(db_path, "downgrade", "-1")
            self.assertIn(f"Running downgrade {HEAD_REVISION}", down_log)
            self.assertNotIn(NEW_TABLE, _table_names(db_path))
            self.assertNotEqual(_current_revision(db_path), HEAD_REVISION)

            _run_alembic(db_path, "upgrade", "head")
            self.assertEqual(_current_revision(db_path), HEAD_REVISION)
            self.assertIn(NEW_TABLE, _table_names(db_path))


if __name__ == "__main__":
    unittest.main(verbosity=2)

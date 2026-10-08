"""新增复合索引：优化常用组合条件的查询（SQLite 单查询只能用一索引）。

- match_data (schedule_id, round_no)      局数据加载（数据分析各 Tab）
- match_data (schedule_id, player_name)   单局内按玩家过滤
- match_data (player_name)                个人战绩按名查询
- schedules (guild_id, match_time)        帮会赛程按时间排序
- attendance_records (schedule_id, status) 出勤按状态过滤
- operation_logs (guild_id, created_at)   帮会日志按时间查询

Revision ID: m7n8o9p0q1r2
Revises: l6m7n8o9p0q1
Create Date: 2026-09-11 15:00:00.000000
"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'm7n8o9p0q1r2'
down_revision: Union[str, None] = 'l6m7n8o9p0q1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """创建复合/单列索引（CREATE INDEX 对 SQLite 为在线操作，无表重建）。"""
    op.create_index('ix_match_data_player_name', 'match_data', ['player_name'])
    op.create_index('ix_match_data_schedule_round', 'match_data', ['schedule_id', 'round_no'])
    op.create_index('ix_match_data_schedule_player', 'match_data', ['schedule_id', 'player_name'])
    op.create_index('ix_schedules_guild_match_time', 'schedules', ['guild_id', 'match_time'])
    op.create_index('ix_attendance_records_schedule_status', 'attendance_records', ['schedule_id', 'status'])
    op.create_index('ix_operation_logs_guild_created', 'operation_logs', ['guild_id', 'created_at'])


def downgrade() -> None:
    """回滚：删除新增索引。"""
    op.drop_index('ix_operation_logs_guild_created', table_name='operation_logs')
    op.drop_index('ix_attendance_records_schedule_status', table_name='attendance_records')
    op.drop_index('ix_schedules_guild_match_time', table_name='schedules')
    op.drop_index('ix_match_data_schedule_player', table_name='match_data')
    op.drop_index('ix_match_data_schedule_round', table_name='match_data')
    op.drop_index('ix_match_data_player_name', table_name='match_data')

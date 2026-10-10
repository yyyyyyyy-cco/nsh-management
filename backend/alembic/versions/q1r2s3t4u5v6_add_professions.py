"""新增 professions 职业目录表（全局）并写入初始 11 职业种子。

职业目录动态化（方案 B）：职业清单从代码常量迁至数据库，开发者在
「系统配置 → 职业目录」维护名称/排序/颜色/启停。种子与升级前的
PROF_ORDER（展示顺序）/ PROF_COLORS（色值，原样大小写）完全一致，
保证升级后全站展示不变。本迁移自包含（不从 app 代码导入）。

Revision ID: q1r2s3t4u5v6
Revises: p0q1r2s3t4u5
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'q1r2s3t4u5v6'
down_revision: Union[str, None] = 'p0q1r2s3t4u5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# 初始职业种子：(名称, 展示排序, 职业色) —— 与旧前端 PROF_ORDER / PROF_COLORS 一致
SEED: list[tuple[str, int, str]] = [
    ("铁衣", 1, "#ffc800"),
    ("素问", 2, "#FF9CF2"),
    ("神相", 3, "#3E6BF4"),
    ("碎梦", 4, "#00FFFB"),
    ("血河", 5, "#F04545"),
    ("玄机", 6, "#f6ff00"),
    ("九灵", 7, "#8B5CF6"),
    ("潮光", 8, "#4F95FF"),
    ("龙吟", 9, "#3fe155"),
    ("鸿音", 10, "#C6834D"),
    ("沧澜", 11, "#605EF0"),
]


def upgrade() -> None:
    """建表 + 唯一索引 + 种子（created_at 显式写入，与项目风格一致：无 server_default）。"""
    op.create_table(
        'professions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(length=16), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('color', sa.String(length=9), nullable=False, server_default='#c9a13b'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index('ix_professions_name', 'professions', ['name'], unique=True)

    conn = op.get_bind()
    stmt = sa.text(
        "INSERT INTO professions (name, sort_order, color, is_active, created_at) "
        "VALUES (:name, :sort_order, :color, 1, CURRENT_TIMESTAMP)"
    )
    for name, sort_order, color in SEED:
        conn.execute(stmt, {"name": name, "sort_order": sort_order, "color": color})


def downgrade() -> None:
    """回滚：删表（成员/出勤等表中的职业字符串快照不受影响）。"""
    op.drop_index('ix_professions_name', table_name='professions')
    op.drop_table('professions')

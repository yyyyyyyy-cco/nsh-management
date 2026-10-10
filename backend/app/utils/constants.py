"""业务常量。"""

MAX_PROFESSION_TARGET = 999  # 职业目标人数上限（与前端输入 max=999 一致，见 database-design §2.3）

# 成员状态
MEMBER_STATUSES = ["formal", "substitute"]

# 排表结构：10 队 × 6 槽 = 60（database-design §2.7）
LINEUP_LAYOUT: list[tuple[str, int]] = [("进攻1", 3), ("进攻2", 3), ("防守1", 2), ("防守2", 2)]
SLOTS_PER_TEAM = 6

"""成员档案响应模型：出勤明细 / 录屏记录 / 排表历史（成员详情页档案 Tab）。

设计依据：memory-bank/design-member-archive.md §4（接口合同）。
"""

from datetime import datetime

from pydantic import BaseModel


class AttendanceHistoryOut(BaseModel):
    """出勤明细行。"""

    schedule_id: int
    opponent: str
    match_time: datetime  # naive 北京墙上时间（与赛程模块口径一致）
    schedule_result: str  # win / lose / draw / pending
    status: str  # normal / leave
    remark: str | None  # 出勤行备注（可空）


class RecordingHistoryOut(BaseModel):
    """录屏记录行（「未提交」由展示层按 url 为空 + status=pending 派生）。"""

    schedule_id: int
    opponent: str
    match_time: datetime
    round_number: int
    url: str | None
    status: str  # pending / approved / rejected
    review_remark: str | None


class LineupHistoryOut(BaseModel):
    """排表历史行：该成员在某场被排入的分类 / 队号 / 槽位。"""

    schedule_id: int
    opponent: str
    match_time: datetime
    category: str
    team_index: int
    slot_index: int
    slot_remark: str | None

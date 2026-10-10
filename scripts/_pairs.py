#!/usr/bin/env python
"""前后端配对表（人工维护）——由 check_type_drift / check_nullability / check_request_required 共用。

从原 `check_type_drift.py`（421 行）拆分而来，三处共用同一份配对表，避免各自维护导致口径漂移。
"""
PAIRS: dict[str, list[str]] = {
    "MemberInfo": ["MemberOut"],
    "AttendanceRecord": ["AttendanceRecordOut"],
    "LineupInfo": ["LineupOut"],
    "LineupSlot": ["LineupSlot"],
    "LineupTeam": ["LineupTeam"],
    "ScheduleInfo": ["ScheduleOut"],
    "Recording": ["RecordingOut"],
    "MatchData": ["MatchDataOut"],
    "ProfessionConfig": ["ProfessionConfigOut"],
    "ProfessionOut": ["ProfessionOut"],
    "Account": ["AccountOut"],
    "Guild": ["GuildOut"],
    "OperationLog": ["OperationLogOut"],
    "GameIdRequestItem": ["GameIdRequestMemberOut"],
    "UserInfo": ["UserOut"],
    "LogStats": ["LogStatsOut"],
    "WeeklyErrorItem": ["WeeklyErrorItem"],
}

# 前端类型名 → 后端请求模型名（*Update 类全可选，配对后天然通过）
PAIRS_REQ: dict[str, list[str]] = {
    # F-111：原键 `SchedulePayload` 在 F-102 拆分后失效，改用现行类型名
    "ScheduleCreatePayload": ["ScheduleCreate"],
    "GuildCreateRequest": ["GuildCreate"],
    "AccountCreateRequest": ["AccountCreate"],
    "AccountUpdateRequest": ["AccountUpdate"],
    "AccountStatusUpdateRequest": ["AccountStatusUpdate"],
    "ProfessionCreateRequest": ["ProfessionCreate"],
    "ProfessionUpdateRequest": ["ProfessionUpdate"],
    "GameIdRequestItem": ["GameIdRequestMemberOut"],
    "GameIdRequestMemberPage": ["GameIdRequestMemberPage"],
}
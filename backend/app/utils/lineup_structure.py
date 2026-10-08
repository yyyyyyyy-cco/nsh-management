"""排表结构工具：标准空结构与固定布局校验。

从 `app/services/lineup_service.py` 抽出（2026-10-03，F-85 修复时该服务已接近 300 行上限；
`AGENTS §4` / `.agent/rules/file-length-rule.md` 规定 Python 服务 ≤ 300 行、工具函数 ≤ 200 行）。
`lineup_service` 继续转出这两个名字，调用方无需改动。
"""

from app.services.lineup_attendance import LineupServiceError
from app.utils.constants import LINEUP_LAYOUT, SLOTS_PER_TEAM
from app.utils.member_names import normalize_member_name


def empty_lineup_data() -> list[dict]:
    """生成标准空排表结构：10 队 × 6 槽。"""
    data = []
    for category, team_count in LINEUP_LAYOUT:
        for team_index in range(team_count):
            data.append(
                {
                    "category": category,
                    "team_index": team_index,
                    "remark": "",
                    "slots": [
                        {"slot_index": i, "member_id": None, "member_name": "", "remark": ""}
                        for i in range(SLOTS_PER_TEAM)
                    ],
                }
            )
    return data


def validate_structure(data: list[dict]) -> None:
    """校验排表结构与固定布局一致（分类、队序、槽位），并禁止同一成员占用多个槽位。"""
    if len(data) != sum(count for _, count in LINEUP_LAYOUT):
        raise LineupServiceError("排表队伍数量必须为 10 队")
    expected = [(cat, idx) for cat, count in LINEUP_LAYOUT for idx in range(count)]
    for team, (cat, idx) in zip(data, expected):
        if team.get("category") != cat or team.get("team_index") != idx:
            raise LineupServiceError("排表队伍分类或顺序与固定结构不一致")
        slots = team.get("slots", [])
        if len(slots) != SLOTS_PER_TEAM:
            raise LineupServiceError(f"{cat} 第 {idx + 1} 队槽位数必须为 {SLOTS_PER_TEAM}")
        for slot, slot_index in zip(slots, range(SLOTS_PER_TEAM)):
            if slot.get("slot_index") != slot_index:
                raise LineupServiceError(f"{cat} 第 {idx + 1} 队槽位序号不合法")

    # 同一成员不得占用多个槽位（2026-10-03 补，见 F-85）：前端拖拽是「移动」故产生不了，
    # 但直接调接口可以写入，重复会导致小队分析重复计数。正式按 member_id、补人按姓名分别去重
    # （正式成员与补人同名是合法的，与出勤库的补人唯一性口径一致）。
    seen_ids: set[int] = set()
    seen_filler_names: set[str] = set()
    for team in data:
        for slot in team.get("slots", []):
            mid = slot.get("member_id")
            if mid is not None:
                if mid in seen_ids:
                    raise LineupServiceError("同一成员不能在排表中出现多次")
                seen_ids.add(mid)
                continue
            name = normalize_member_name(slot.get("member_name"))
            if not name:
                continue
            if name in seen_filler_names:
                raise LineupServiceError("同一补人不能在排表中出现多次")
            seen_filler_names.add(name)

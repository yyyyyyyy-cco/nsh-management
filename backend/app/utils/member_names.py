"""出勤与排表共用的姓名规范化规则。"""


def normalize_member_name(name: str | None) -> str:
    """仅去除首尾空白（含全角空格），保留内部空格及大小写。"""
    return (name or "").strip()

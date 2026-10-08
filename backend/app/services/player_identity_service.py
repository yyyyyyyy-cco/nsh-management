"""战绩名称关联：按已审核通过的游戏 ID 改名申请解析新旧 ID 归属与可检测冲突。

设计依据：memory-bank/design-game-id-change.md §5（关联算法与边界）。
只依赖模型（不反向依赖 my_stats_service），冲突一律抛 PlayerIdentityError(409)。
"""

from dataclasses import dataclass, field

from sqlalchemy import distinct, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_id_request import MemberGameIdRequest
from app.models.match_data import MatchData
from app.models.member import Member
from app.models.schedule import Schedule

MERGE_CONFLICT_MESSAGE = "该 ID 关联到多个成员或存在可检测的名称归属冲突，请改用「仅查此 ID」"


class PlayerIdentityError(Exception):
    """战绩名称关联冲突异常（409，可显式切换精确查询）。"""

    def __init__(self, message: str = MERGE_CONFLICT_MESSAGE, status_code: int = 409):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


@dataclass
class PlayerIdentity:
    """一次战绩查询的名称归属解析结果。"""

    mode: str  # merged / exact
    query_player_name: str
    display_name: str  # merged 时为成员当前 ID；exact 时为输入 ID
    member_id: int | None = None
    current_game_id: str | None = None
    aliases: list[str] = field(default_factory=list)


def _exact(name: str) -> PlayerIdentity:
    return PlayerIdentity(
        mode="exact",
        query_player_name=name,
        display_name=name,
        aliases=[name],
    )


async def resolve_player_identity(
    session: AsyncSession, guild_id: int, query_name: str, merge_aliases: bool
) -> PlayerIdentity:
    """解析查询名的归属：merged（唯一成员且无冲突）或 exact（原始名称查询）。"""
    if not merge_aliases:
        return _exact(query_name)

    # 1) 当前成员命中
    member_rows = (
        await session.execute(
            select(Member.id, Member.name).where(Member.guild_id == guild_id, Member.name == query_name)
        )
    ).all()
    # 2) 已通过申请命中（新/旧任一端）
    rel_rows = (
        await session.execute(
            select(
                MemberGameIdRequest.member_id,
                MemberGameIdRequest.old_game_id,
                MemberGameIdRequest.new_game_id,
            ).where(
                MemberGameIdRequest.guild_id == guild_id,
                MemberGameIdRequest.status == "approved",
                or_(
                    MemberGameIdRequest.old_game_id == query_name,
                    MemberGameIdRequest.new_game_id == query_name,
                ),
            )
        )
    ).all()

    member_ids = {row.id for row in member_rows}
    member_ids |= {row.member_id for row in rel_rows if row.member_id is not None}
    if len(member_ids) > 1:
        raise PlayerIdentityError()
    if not member_ids:
        # 无当前成员、无存续关系：若查询名出现在已失去成员的批准记录中，视为歧义证据
        if any(row.member_id is None for row in rel_rows):
            raise PlayerIdentityError()
        return _exact(query_name)

    member_id = member_ids.pop()
    member = await session.get(Member, member_id)
    if member is None or member.guild_id != guild_id:
        # 存续关系指向已不存在的成员（异常数据）：停止自动归属
        raise PlayerIdentityError()

    # 3) 汇总该成员全部已确认名称（当前名 + 全部批准记录两端）
    alias_set: set[str] = {member.name}
    own_rows = (
        await session.execute(
            select(MemberGameIdRequest.old_game_id, MemberGameIdRequest.new_game_id).where(
                MemberGameIdRequest.guild_id == guild_id,
                MemberGameIdRequest.status == "approved",
                MemberGameIdRequest.member_id == member_id,
            )
        )
    ).all()
    for old_game_id, new_game_id in own_rows:
        alias_set.add(old_game_id)
        alias_set.add(new_game_id)

    # 4) 冲突：其他当前成员占用集合内名称
    other_member = (
        await session.execute(
            select(Member.id).where(
                Member.guild_id == guild_id,
                Member.id != member_id,
                Member.name.in_(alias_set),
            )
        )
    ).first()
    if other_member is not None:
        raise PlayerIdentityError()

    # 5) 冲突：其他成员（含已删除成员留下的空引用记录）的批准记录与集合重叠
    overlap = (
        await session.execute(
            select(MemberGameIdRequest.id).where(
                MemberGameIdRequest.guild_id == guild_id,
                MemberGameIdRequest.status == "approved",
                or_(
                    MemberGameIdRequest.member_id.is_(None),
                    MemberGameIdRequest.member_id != member_id,
                ),
                or_(
                    MemberGameIdRequest.old_game_id.in_(alias_set),
                    MemberGameIdRequest.new_game_id.in_(alias_set),
                ),
            )
        )
    ).first()
    if overlap is not None:
        raise PlayerIdentityError()

    # 6) 冲突：同一场同一局出现多个关联名称或阵营（先全量检测，再截取最近 10 场）
    ambiguous = (
        await session.execute(
            select(MatchData.schedule_id)
            .join(Schedule, MatchData.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, MatchData.player_name.in_(alias_set))
            .group_by(MatchData.schedule_id, MatchData.round_no)
            .having(
                or_(
                    func.count(distinct(MatchData.player_name)) > 1,
                    func.count(distinct(MatchData.camp)) > 1,
                )
            )
        )
    ).first()
    if ambiguous is not None:
        raise PlayerIdentityError()

    return PlayerIdentity(
        mode="merged",
        query_player_name=query_name,
        display_name=member.name,
        member_id=member.id,
        current_game_id=member.name,
        aliases=sorted(alias_set),
    )


async def search_identity_names(session: AsyncSession, guild_id: int, keyword: str, limit: int = 10) -> list[str]:
    """自动补全候选：比赛数据中的名称 + 已确认改名关系的新旧名称与存续成员当前名。

    排序：精确输入优先 → 已有比赛记录数倒序 → 名称升序；去重后截断。
    """
    like = f"%{keyword}%"
    counts: dict[str, int] = {}
    rows = (
        await session.execute(
            select(MatchData.player_name, func.count(MatchData.player_name))
            .join(Schedule, MatchData.schedule_id == Schedule.id)
            .where(Schedule.guild_id == guild_id, MatchData.player_name.ilike(like))
            .group_by(MatchData.player_name)
        )
    ).all()
    for name, count in rows:
        counts[name] = int(count)

    # 已确认改名关系：命中任一端时把两端与该成员当前名一并作为候选
    rel_rows = (
        await session.execute(
            select(
                MemberGameIdRequest.member_id,
                MemberGameIdRequest.old_game_id,
                MemberGameIdRequest.new_game_id,
            )
            .where(
                MemberGameIdRequest.guild_id == guild_id,
                MemberGameIdRequest.status == "approved",
                or_(
                    MemberGameIdRequest.old_game_id.ilike(like),
                    MemberGameIdRequest.new_game_id.ilike(like),
                ),
            )
            .limit(50)
        )
    ).all()
    candidate_names: set[str] = set()
    member_ids: set[int] = set()
    for member_id, old_game_id, new_game_id in rel_rows:
        candidate_names.update({old_game_id, new_game_id})
        if member_id is not None:
            member_ids.add(member_id)
    if member_ids:
        current_rows = (
            await session.execute(select(Member.name).where(Member.guild_id == guild_id, Member.id.in_(member_ids)))
        ).all()
        candidate_names.update(name for (name,) in current_rows)

    # 当前成员名（刚获批、尚无比赛数据时也能补全）
    member_rows = (
        await session.execute(select(Member.name).where(Member.guild_id == guild_id, Member.name.ilike(like)))
    ).all()
    candidate_names.update(name for (name,) in member_rows)

    for name in candidate_names:
        counts.setdefault(name, 0)

    ordered = sorted(counts.items(), key=lambda item: (item[0] != keyword, -item[1], item[0]))
    return [name for name, _ in ordered[:limit]]

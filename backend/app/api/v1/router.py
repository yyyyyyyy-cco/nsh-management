"""API v1 路由汇总。"""

from fastapi import APIRouter

from app.api.v1 import (
    accounts,
    attendance,
    auth,
    config,
    developer,
    game_id_requests,
    guilds,
    lineups,
    logs,
    match_data,
    member_archive,
    members,
    my_stats,
    recording,
    schedules,
    squad_adjustments,
)

api_router = APIRouter()
api_router.include_router(auth.router)
# 注意：game_id_requests 与 member_archive 均挂在 /members 前缀下，必须先于 members.router 注册——
# 前者是单段路径（/members/game-id-options 等）会被 /members/{member_id} 捕获；后者为两段路径
# （如 /{member_id}/attendance-history）实际不会被捕获，前置注册仅为防御性顺序（design-member-archive.md §4）
api_router.include_router(game_id_requests.router)
api_router.include_router(member_archive.router)
api_router.include_router(members.router)
api_router.include_router(schedules.router)
api_router.include_router(attendance.router)
api_router.include_router(lineups.router)
api_router.include_router(recording.router)
api_router.include_router(match_data.router)
api_router.include_router(config.router)
api_router.include_router(accounts.router)
api_router.include_router(guilds.router)
api_router.include_router(developer.router)
api_router.include_router(logs.router)
api_router.include_router(squad_adjustments.router)
api_router.include_router(my_stats.router)

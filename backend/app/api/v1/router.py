"""API v1 路由汇总。"""
from fastapi import APIRouter

from app.api.v1 import attendance, auth, config, developer, lineups, match_data, members, recording, schedules

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(members.router)
api_router.include_router(schedules.router)
api_router.include_router(attendance.router)
api_router.include_router(lineups.router)
api_router.include_router(recording.router)
api_router.include_router(match_data.router)
api_router.include_router(config.router)
api_router.include_router(developer.router)

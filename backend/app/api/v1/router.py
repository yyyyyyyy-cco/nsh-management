"""API v1 路由汇总。"""
from fastapi import APIRouter

from app.api.v1 import attendance, auth, lineups, members, schedules

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(members.router)
api_router.include_router(schedules.router)
api_router.include_router(attendance.router)
api_router.include_router(lineups.router)

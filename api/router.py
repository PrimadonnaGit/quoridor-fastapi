from fastapi import APIRouter

from api.endpoint.auth import router as auth_router
from api.endpoint.leaderboard import router as leaderboard_router
from api.endpoint.users import router as users_router
from api.endpoint.websocket import router as websocket_router

api_router = APIRouter()

api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)
api_router.include_router(
    users_router,
    prefix="/users",
    tags=["users"],
)
api_router.include_router(
    websocket_router,
    prefix="/ws",
    tags=["websocket"],
)
api_router.include_router(
    leaderboard_router,
    prefix="/leaderboard",
    tags=["leaderboard"],
)

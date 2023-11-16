from fastapi import APIRouter, Depends

from api.service import leaderboard as leaderboard_service
from core.database import Database, get_database

router = APIRouter()


@router.get("")
async def get_leaderboard(db: Database = Depends(get_database)):
    return await leaderboard_service.get_leaderboard(db)

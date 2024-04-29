from fastapi import APIRouter, Depends, Query

from api.service import leaderboard as leaderboard_service
from core.database import Database, get_database

router = APIRouter()


@router.get("")
async def get_leaderboard(
    db: Database = Depends(get_database), limit: int = Query(10, gt=0, le=100)
):
    return await leaderboard_service.get_leaderboard(db, limit)

from fastapi import APIRouter, Body, Depends

from api.service import leaderboard
from core.database import Database, get_database

router = APIRouter()


@router.get("")
async def get_leaderboard(db: Database = Depends(get_database)):
    return await leaderboard.get_leaderboard(db)


@router.post("")
async def save_result(
    db: Database = Depends(get_database),
    player1_id: int = Body(..., description="player1", embed=True),
    player2_id: int = Body(..., description="player2", embed=True),
    winner_id: int = Body(..., description="winner", embed=True),
):
    return await leaderboard.update_game_result(db, player1_id, player2_id, winner_id)

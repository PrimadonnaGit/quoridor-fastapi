from fastapi import APIRouter, Depends, Path

from api.service.auth import get_user_from_user
from core.database import Database, get_database

router = APIRouter()


@router.get("/{user_id}")
async def get_user(db: Database = Depends(get_database), user_id: str = Path(...)):
    return await get_user_from_user(db, user_id)

from fastapi import APIRouter, Body, Depends, Path

from api.service import user as user_service
from core.database import Database, get_database

router = APIRouter()


@router.get("/{user_id}")
async def get_user(db: Database = Depends(get_database), user_id: int = Path(...)):
    return await user_service.get_user_by_user_id(db, user_id)


@router.patch("/{user_id}")
async def update_user(
    db: Database = Depends(get_database),
    user_id: int = Path(...),
    nickname: str | None = Body(None, description="nickname", embed=True),
    profile_image: str | None = Body(None, description="profile_image", embed=True),
):
    return await user_service.update_user(db, user_id, nickname, profile_image)

from fastapi import APIRouter, Body, Depends

from api.service.auth import kakao_callback
from core.database import Database, get_database

router = APIRouter()


@router.post("/kakao-login")
async def kakao_login_callback(
    db: Database = Depends(get_database),
    code: str = Body(..., description="Authorization Code", embed=True),
):
    return await kakao_callback(db, code)

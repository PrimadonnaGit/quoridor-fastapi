from fastapi import APIRouter, Body, Depends

from api.service import auth as auth_service
from core.database import Database, get_database

router = APIRouter()


@router.post("/kakao-login")
async def kakao_login_callback(
    db: Database = Depends(get_database),
    code: str = Body(..., description="Authorization Code", embed=True),
):
    return await auth_service.kakao_callback(db, code)

from datetime import datetime

import httpx
from fastapi.requests import Request
from fastapi.security import OAuth2PasswordBearer

from api.service import user as user_service
from core.config import KAKAO_CLIENT_ID, KAKAO_TOKEN_URL, REDIRECT_URI
from core.database import Database
from core.utils import generate_random_nickname


class OAuth2KakaoPasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str:
        token = await super().__call__(request)
        return token


oauth2_scheme = OAuth2KakaoPasswordBearer(tokenUrl=KAKAO_TOKEN_URL)


async def kakao_callback(db: Database, code: str):
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": KAKAO_CLIENT_ID,
                "redirect_uri": REDIRECT_URI,
                "code": code,
            },
        )
        token_data = token_response.json()

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f'Bearer {token_data["access_token"]}'},
        )

    user_data = user_response.json()

    user = await user_service.get_user_by_social_id(db, user_data["id"])

    if not user:
        user = (
            db.client.table("users")
            .upsert(
                {
                    "nickname": await generate_random_nickname(),
                    "social_nickname": user_data["properties"]["nickname"],
                    "profile_image": user_data["properties"]["profile_image"],
                    "social_provider": "kakao",
                    "social_user_id": user_data["id"],
                    "email": user_data["kakao_account"].get("email"),
                    "social_access_token": token_data["access_token"],
                    "social_refresh_token": token_data["refresh_token"],
                    "last_login_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
            .execute()
        )

        return {"message": "Kakao Sign Up and Login Successful!", "user": user.data[0]}

    return {"message": "Kakao Login Successful!", "user": user}

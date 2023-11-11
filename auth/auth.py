import os

import httpx
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer

from database.database import user_db

from datetime import datetime

CLIENT_ID = os.getenv("KAKAO_CLIENT_ID", "")
REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI", "")
KAKAO_TOKEN_URL = os.getenv("KAKAO_TOKEN_URL", "")


class OAuth2KakaoPasswordBearer(OAuth2PasswordBearer):
    async def __call__(self, request: Request) -> str:
        token = await super().__call__(request)
        return token


oauth2_scheme = OAuth2KakaoPasswordBearer(tokenUrl=KAKAO_TOKEN_URL)


def redirect_to_login():
    redirect_url = f"https://kauth.kakao.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&response_type=code"

    return RedirectResponse(redirect_url)


async def kakao_callback(code: str = None):
    if code is None:
        raise HTTPException(status_code=400, detail="Missing authorization code")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            KAKAO_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "redirect_uri": "https://quoridor-web-koreaboardgamearena.koyeb.app/api/auth/kakao",
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
        user, _ = user_db.upsert(
            {
                "nickname": user_data["properties"]["nickname"],
                "profile_image": user_data["properties"]["profile_image"],
                "social_provider": "kakao",
                "social_user_id": "222222",
                "email": user_data["kakao_account"]["email"],
                "social_access_token": token_data["access_token"],
                "social_refresh_token": token_data["refresh_token"],
                "last_login_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        ).execute()

    return {"message": "Kakao Login Successful!", "user": user}


def get_user_from_user(user_id: str):
    user = user_db.select("*").eq("id", user_id).execute()
    return user.data[0]

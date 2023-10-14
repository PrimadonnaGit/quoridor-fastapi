import os

from fastapi.requests import Request

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import httpx


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
                "code": code,
            },
        )
        token_data = token_response.json()
        print(token_data)

    async with httpx.AsyncClient() as client:
        user_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f'Bearer {token_data["access_token"]}'},
        )
        user_data = user_response.json()

    return {"message": "Kakao Login Successful!", "user_data": user_data}

import logging

import uvicorn
from fastapi import Body, FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware

from auth.auth import kakao_callback, redirect_to_login
from connection.connection import ConnectionManager

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    room_number = await manager.new_connection(websocket)

    try:
        while True:
            await manager.play_game(
                websocket,
                room_number,
            )
    except Exception as e:
        logging.error(e)
    finally:
        print("disconnect", websocket, room_number)
        await manager.disconnect(websocket, room_number)


@app.websocket("/ws/{room_number}")
async def websocket_endpoint_with_rood_id(websocket: WebSocket, room_number: int):
    await manager.connect(websocket, room_number)

    try:
        while True:
            await manager.play_game(
                websocket,
                room_number,
            )
    except Exception as e:
        logging.error(e)
    finally:
        await manager.disconnect(websocket, room_number)


@app.get("/login")
async def login():
    return redirect_to_login()


@app.post("/kakao-login")
async def kakao_login_callback(
    code: str = Body(..., description="Authorization Code", embed=True)
):
    return await kakao_callback(code)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)

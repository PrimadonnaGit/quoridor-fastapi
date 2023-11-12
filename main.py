import logging

import uvicorn
from fastapi import Body, FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketDisconnect
from websockets import ConnectionClosedError, ConnectionClosedOK

from auth.auth import kakao_callback, get_user_from_user
from connection.connection import ConnectionManager

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "localhost:3000",
        "https://quoridor-web-koreaboardgamearena.koyeb.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    room_number = await manager.new_connection(websocket)

    try:
        while True:
            await manager.communicate(
                websocket,
                room_number,
            )

    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        logging.info("ws, client disconnected")
        await manager.stop_countdown(room_number)
        await manager.disconnect(websocket, room_number)
    except Exception as e:
        logging.error(f"ws, {e}")


@app.websocket("/ws/{room_number}")
async def websocket_endpoint_with_rood_id(websocket: WebSocket, room_number: int):
    await manager.connect(websocket, room_number)

    try:
        while True:
            await manager.communicate(
                websocket,
                room_number,
            )

    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        logging.info("ws, client disconnected")
        await manager.stop_countdown(room_number)
        await manager.disconnect(websocket, room_number)
    except Exception as e:
        logging.error(f"ws, {e}")


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    pass


@app.on_event("shutdown")
async def shutdown_event():
    for room in manager.rooms.values():
        for client in room.clients:
            await client.close()


@app.post("/kakao-login")
async def kakao_login_callback(
    code: str = Body(..., description="Authorization Code", embed=True)
):
    return await kakao_callback(code)


@app.get("/users/{user_id}")
async def get_me(user_id: str):
    return get_user_from_user(user_id)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)

from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.requests import Request
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from auth.auth import redirect_to_login, kakao_callback
from connection.connection import ConnectionManager

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()


@app.get("/test", response_class=HTMLResponse)
async def test_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.new_connection(websocket)
    try:
        while True:
            await manager.start_game(
                websocket,
                manager.client_info[websocket]['room_id'],
            )
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(websocket)


@app.websocket("/ws/{room_id}")
async def websocket_endpoint_with_rood_id(websocket: WebSocket, room_id: int):
    await manager.connect(websocket, room_id)
    try:
        while True:
            await manager.start_game(
                websocket,
                room_id,
            )
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(websocket)


@app.get("/login")
async def login():
    return redirect_to_login()


@app.get("/kakao-login")
async def kakao_login_callback(code: str = None):
    return await kakao_callback(code)


if __name__ == "__main__":
    uvicorn.run(app, port=8000)

import random
import uuid

from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.requests import Request
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

app = FastAPI()

# 템플릿 엔진을 초기화합니다.
templates = Jinja2Templates(directory="templates")

# CORS 설정을 추가합니다. (모든 도메인에서 접근을 허용합니다.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인을 설정하세요.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.client_info = {}
        self.room_info = {}
        self.game_history = {}

    def check_available_room(self, room_id: int):
        if room_id in self.room_info:
            if len(self.room_info[room_id]) < 2:
                return True
            else:
                return False, "Room is full. Connection denied."
        else:
            return False, "Room does not exist. Connection denied."

    async def new_connection(self, websocket: WebSocket):
        await websocket.accept()
        rood_id = random.randint(0, 100000)
        self.room_info[rood_id] = [websocket]
        self.client_info[websocket] = {'id': str(uuid.uuid4()), 'turn': True, 'room_id': rood_id}
        self.game_history[rood_id] = []
        await websocket.send_text(f"Your room id is {rood_id}")

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id in self.room_info:
            if len(self.room_info[room_id]) < 2:
                self.room_info[room_id].append(websocket)
                self.client_info[websocket] = {'id': str(uuid.uuid4()), 'turn': False, 'room_id': room_id}
                await websocket.send_text(f"Connected to room {room_id}")
                await websocket.send_text(f"Your id is {self.client_info[websocket]['id']}")
                await self.broadcast("game start!", room_id)

            else:
                await websocket.send_text("Room is full. Connection denied.")
                return
        else:
            await websocket.send_text("Room does not exist. Connection denied.")
            return

    async def disconnect(self, websocket: WebSocket):
        self.room_info[self.client_info[websocket]['room_id']].remove(websocket)
        await websocket.close()

    async def broadcast(self, message: str, room_id: int):
        for room_user in self.room_info[room_id]:
            await room_user.send_text(message)


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.new_connection(websocket)
    try:
        while True:
            await start_game(websocket, manager.client_info[websocket]['room_id'])
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(websocket)


@app.websocket("/ws/{room_id}")
async def websocket_endpoint_with_rood_id(websocket: WebSocket, room_id: int):
    await manager.connect(websocket, room_id)
    try:
        while True:
            await start_game(websocket, room_id)
    except Exception as e:
        print(e)
    finally:
        await manager.disconnect(websocket)


async def start_game(websocket: WebSocket, room_id: int):
    data = await websocket.receive_text()
    if manager.client_info[websocket]['turn']:
        manager.game_history[room_id].append(data)
        for client in manager.room_info[room_id]:
            if client != websocket:
                await client.send_text(f"{manager.client_info[websocket]['id']}Player : {data}")

        # 상대 클라이언트의 턴으로 변경
        manager.client_info[websocket]['turn'] = False
        for client in manager.room_info[room_id]:
            if client != websocket:
                manager.client_info[client]['turn'] = True
    else:
        await websocket.send_text("Not your turn")

if __name__ == "__main__":
    uvicorn.run(app, port=8000)

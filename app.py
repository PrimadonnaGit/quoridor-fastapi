import json
import random
import uuid

from fastapi import FastAPI, WebSocket
import uvicorn
from fastapi.requests import Request
from starlette.middleware.cors import CORSMiddleware

from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates

from status import STATUS_CODE

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


# 응답 객체 (게임 상태와 에러 코드를 포함합니다.)
# {
# 	"message_type" : "user_action",
#    #one of below
# 	"user_action": {
# 		…
# 	},
# 	"server_info": {
# 		"code": 201,
# 		"message": "room is created",
# 		"data": {
# 			…
# 		}
# 	},
# 	"error" : {
# 		"code": 100,
# 		"message": "invalid move"
# 	}
# }

class Response:
    def __init__(self, message_type: str, status_code: int, data: dict = None, client: dict = None):
        if message_type == "server_info":
            self.message_type = message_type
            self.code = status_code
            self.message = STATUS_CODE[status_code]
            self.data = data
        elif message_type == "error":
            self.message_type = message_type
            self.code = status_code
            self.message = STATUS_CODE[status_code]

    def to_dict(self):
        if self.message_type == "server_info":
            return {
                "message_type": self.message_type,
                "server_info": {
                    "code": self.code,
                    "message": self.message,
                    "data": self.data,
                }
            }
        elif self.message_type == "error":
            return {
                "message_type": self.message_type,
                "error": {
                    "code": self.code,
                    "message": self.message,
                }
            }


class ConnectionManager:
    def __init__(self):
        self.client_info = {}
        self.room_info = {}
        self.game_history = {}

    async def new_connection(self, websocket: WebSocket):
        await websocket.accept()
        rood_id = random.randint(0, 100000)
        self.room_info[rood_id] = [websocket]
        self.client_info[websocket] = {'id': str(uuid.uuid4()), 'turn': True, 'room_id': rood_id}
        self.game_history[rood_id] = []
        response = Response("server_info", 102, {
            "room_id": rood_id,
        }).to_dict()
        await websocket.send_json(response)

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id in self.room_info:
            if len(self.room_info[room_id]) < 2:
                self.room_info[room_id].append(websocket)
                self.client_info[websocket] = {'id': str(uuid.uuid4()), 'turn': False, 'room_id': room_id}
                await websocket.send_json(
                    Response("server_info", 102, {
                        "room_id": room_id,
                    }).to_dict()
                )
                await self.broadcast_json(
                    Response("server_info", 301).to_dict()
                )
                # broadcast
            else:
                await websocket.send_json(
                    Response("error", 100).to_dict()
                )
                return
        else:
            await websocket.send_json(
                Response("error", 101).to_dict()
            )
            return

    async def disconnect(self, websocket: WebSocket):
        self.room_info[self.client_info[websocket]['room_id']].remove(websocket)

    async def broadcast(self, message: str, room_id: int):
        for room_user in self.room_info[room_id]:
            await room_user.send_text(message)

    async def broadcast_json(self, message: dict, room_id: int):
        for room_user in self.room_info[room_id]:
            await room_user.send_json(message)


manager = ConnectionManager()


@app.get("/test", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/")
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
    if len(manager.room_info[room_id]) != 2:
        await websocket.send_text("Another player has left the game. Start a new game")
        return
    if manager.client_info[websocket]['turn']:
        manager.game_history[room_id].append(data)
        for client in manager.room_info[room_id]:
            if client != websocket:
                await client.send_json(data)

        # 상대 클라이언트의 턴으로 변경
        manager.client_info[websocket]['turn'] = False
        for client in manager.room_info[room_id]:
            if client != websocket:
                manager.client_info[client]['turn'] = True
    else:
        await websocket.send_text("Not your turn")


if __name__ == "__main__":
    uvicorn.run(app, port=8000)

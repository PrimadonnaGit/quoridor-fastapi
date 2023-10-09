import json
import random
import uuid

from starlette.websockets import WebSocket

from util.util import ServerInfoResponse, ErrorResponse


class ConnectionManager:
    def __init__(self):
        self.client_info = {}
        self.room_info = {}
        self.game_history = {}

    async def new_connection(self, websocket: WebSocket):
        await websocket.accept()
        rood_id = random.randint(0, 100000)
        self.room_info[rood_id] = [websocket]
        self.client_info[websocket] = {
            "id": str(uuid.uuid4()),
            "turn": True,
            "room_id": rood_id,
        }
        self.game_history[rood_id] = []
        await websocket.send_json(
            ServerInfoResponse(102, self.client_info[websocket]).to_dict()
        )

    async def connect(self, websocket: WebSocket, room_id: int):
        await websocket.accept()
        if room_id in self.room_info:
            if len(self.room_info[room_id]) < 2:
                self.room_info[room_id].append(websocket)
                self.client_info[websocket] = {
                    "id": str(uuid.uuid4()),
                    "turn": False,
                    "room_id": room_id,
                }
                await websocket.send_json(
                    ServerInfoResponse(102, self.client_info[websocket]).to_dict()
                )
                await self.broadcast_json(ServerInfoResponse(301).to_dict(), room_id)
            else:
                await websocket.send_json(ErrorResponse(100).to_dict())
                return
        else:
            await websocket.send_json(ErrorResponse(101).to_dict())
            return

    async def disconnect(self, websocket: WebSocket):
        self.room_info[self.client_info[websocket]["room_id"]].remove(websocket)
        await self.broadcast_json(
            ErrorResponse(202).to_dict(), self.client_info[websocket]["room_id"]
        )

    async def broadcast_json(self, message: dict, room_id: int):
        for room_user in self.room_info[room_id]:
            await room_user.send_json(message)

    async def start_game(self, websocket: WebSocket, room_id: int):
        data = await websocket.receive_text()

        if self.client_info[websocket]["turn"]:
            try:
                json_data = json.loads(data)
                self.game_history[room_id].append(json_data)

                for client in self.room_info[room_id]:
                    if client != websocket:
                        await client.send_json(json_data)

                self.client_info[websocket]["turn"] = False
                for client in self.room_info[room_id]:
                    if client != websocket:
                        self.client_info[client]["turn"] = True

            except json.JSONDecodeError:
                await websocket.send_json(ErrorResponse(203).to_dict())

        else:
            await websocket.send_json(ErrorResponse(200).to_dict())

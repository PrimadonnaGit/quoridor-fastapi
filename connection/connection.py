import asyncio
import json
import random
import uuid
from collections import defaultdict

from starlette.websockets import WebSocket

from schemes.connection import (
    ErrorStatus,
    InfoStatus,
    RoomInfo,
    ServerErrorScheme,
    ServerInfoScheme,
    ServerMessageType,
    ServerResponse,
)


class ConnectionManager:
    """Websocket Connection manager."""

    def __init__(self):
        self.rooms: dict[int, RoomInfo] = defaultdict(RoomInfo)

    async def make_new_room_number(self) -> int:
        """Make new room number."""
        room_number = random.randint(1000, 9999)
        while room_number in self.rooms.keys():
            room_number = random.randint(1000, 9999)

        return room_number

    async def reset_countdown(self, room_number: int) -> None:
        self.rooms[room_number].tic = 90

    async def stop_countdown(self, room_number: int) -> None:
        self.rooms[room_number].tic = 0

    async def countdown(self, room_number: int) -> None:
        while (
            self.rooms[room_number].tic > 0
            and len(self.rooms[room_number].clients) == 2
        ):
            try:
                await self.broadcast_to_room(
                    ServerResponse(
                        message_type=ServerMessageType.SERVER_INFO.value,
                        server_info=ServerInfoScheme(
                            code=InfoStatus.COUNTDOWN.value,
                            message="Countdown",
                            data={
                                "countdown": self.rooms[room_number].tic,
                            },
                        ),
                    ).model_dump(),
                    room_number,
                )
            except Exception as e:
                print(e)
                break
            await asyncio.sleep(1)
            self.rooms[room_number].tic -= 1

    async def new_connection(self, client: WebSocket) -> int:
        """Make new connection."""
        await client.accept()

        room_number = await self.make_new_room_number()

        self.rooms[room_number].clients.append(client)
        self.rooms[room_number].current_player = client

        await client.send_json(
            ServerResponse(
                message_type=ServerMessageType.SERVER_INFO.value,
                server_info=ServerInfoScheme(
                    code=InfoStatus.CONNECTED_TO_ROOM.value,
                    message="Connected to room",
                    data={
                        "client_id": str(uuid.uuid4()),
                        "is_your_turn": True,
                        "room_number": room_number,
                        "clients_count": len(self.rooms[room_number].clients),
                    },
                ),
            ).model_dump()
        )

        return room_number

    async def connect(self, client: WebSocket, room_number: int) -> None:
        """Connect client to room."""
        await client.accept()

        if room_number in self.rooms:
            # if room is not full
            if len(self.rooms[room_number].clients) < 2:
                self.rooms[room_number].clients.append(client)

                await client.send_json(
                    ServerResponse(
                        message_type=ServerMessageType.SERVER_INFO.value,
                        server_info=ServerInfoScheme(
                            code=InfoStatus.CONNECTED_TO_ROOM.value,
                            message="Connected to room",
                            data={
                                "client_id": str(uuid.uuid4()),
                                "is_your_turn": False,
                                "room_number": room_number,
                                "clients_count": len(self.rooms[room_number].clients),
                            },
                        ),
                    ).model_dump()
                )

                await self.broadcast_to_room(
                    ServerResponse(
                        message_type=ServerMessageType.SERVER_INFO.value,
                        server_info=ServerInfoScheme(
                            code=InfoStatus.READY_TO_PLAY.value,
                            message="Ready for play",
                        ),
                    ).model_dump(),
                    room_number,
                )
            else:
                # if room is full
                await client.send_json(
                    ServerResponse(
                        message_type=ServerMessageType.ERROR.value,
                        error=ServerErrorScheme(
                            code=ErrorStatus.ROOM_IS_FULL.value,
                            message=f"Room is full {len(self.rooms[room_number].clients)}",
                        ),
                    ).model_dump()
                )
        else:
            # if room does not exist
            await client.send_json(
                ServerResponse(
                    message_type=ServerMessageType.ERROR.value,
                    error=ServerErrorScheme(
                        code=ErrorStatus.ROOM_DOES_NOT_EXIST.value,
                        message="Room does not exist",
                    ),
                ).model_dump()
            )

    async def disconnect(self, client: WebSocket, room_number: int) -> None:
        """Disconnect client from room."""
        print("disconnect", client, room_number, self.rooms[room_number].clients)
        if room_number in self.rooms.keys():
            if client in self.rooms[room_number].clients:
                self.rooms[room_number].clients.remove(client)
            if len(self.rooms[room_number].clients) == 0:
                del self.rooms[room_number]
            else:
                await self.broadcast_to_room(
                    ServerResponse(
                        message_type=ServerMessageType.SERVER_INFO.value,
                        server_info=ServerInfoScheme(
                            code=InfoStatus.CONNECTION_ENDED.value,
                            message="Connection ended",
                        ),
                    ).model_dump(),
                    room_number,
                )

    async def broadcast_to_room(self, message: dict, room_number: int) -> None:
        """Broadcast message to all clients in the room."""
        for client in self.rooms[room_number].clients:
            await client.send_json(message)

    async def switch_current_player(self, room_number: int) -> None:
        """Switch current player."""
        self.rooms[room_number].current_player = (
            self.rooms[room_number].clients[0]
            if self.rooms[room_number].clients[0]
            != self.rooms[room_number].current_player
            else self.rooms[room_number].clients[1]
        )

    async def handle_server_info_message(self, room_number: int, message: dict) -> None:
        if message["server_info"]["code"] == 103:
            # 게임 준비여부 확인
            self.rooms[room_number].ready_to_play += 1

            if self.rooms[room_number].ready_to_play == 2:
                # 게임 시작
                self.rooms[room_number].ready_to_play = 0

                for client in self.rooms[room_number].clients:
                    is_your_turn = (
                        True
                        if client == self.rooms[room_number].current_player
                        else False
                    )
                    await client.send_json(
                        ServerResponse(
                            message_type=ServerMessageType.SERVER_INFO.value,
                            server_info=ServerInfoScheme(
                                code=InfoStatus.GAME_START.value,
                                message="Game start",
                                data={
                                    "is_your_turn": is_your_turn,
                                },
                            ),
                        ).model_dump()
                    )

                asyncio.create_task(self.countdown(room_number))
                asyncio.create_task(self.heartbeat(room_number))
                return
        if message["server_info"]["code"] == 202:
            # 상대방이 나갔을 때
            await self.broadcast_to_room(
                ServerResponse(
                    message_type=ServerMessageType.SERVER_INFO.value,
                    server_info=ServerInfoScheme(
                        code=InfoStatus.PLAYER_HAS_LEFT_THE_CONNECTION.value,
                        message="Player has left the connection",
                    ),
                ).model_dump(),
                room_number,
            )
            return

    async def heartbeat(self, room_number: int) -> None:
        while len(self.rooms[room_number].clients) == 2:
            try:
                await self.broadcast_to_room(
                    ServerResponse(
                        message_type=ServerMessageType.HEARTBEAT.value,
                        server_info=ServerInfoScheme(
                            code=InfoStatus.PING.value,
                            message="ping",
                        ),
                    ).model_dump(),
                    room_number,
                )
                for client in self.rooms[room_number].clients:
                    if self.rooms[room_number].player_heartbeats[client] > 5:
                        await self.broadcast_to_room(
                            ServerResponse(
                                message_type=ServerMessageType.SERVER_INFO.value,
                                server_info=ServerInfoScheme(
                                    code=InfoStatus.PLAYER_HAS_LEFT_THE_CONNECTION.value,
                                    message="Player has left the connection",
                                ),
                            ).model_dump(),
                            room_number,
                        )
                        return
                    self.rooms[room_number].player_heartbeats[client] += 1

            except Exception as e:
                print(e)
                break
            await asyncio.sleep(1)

    async def communicate(self, client: WebSocket, room_number: int) -> None:
        """Play game with client."""
        text = await client.receive_text()

        try:
            message = json.loads(text)
        except json.JSONDecodeError:
            await client.send_json(
                ServerResponse(
                    message_type=ServerMessageType.ERROR.value,
                    error=ServerErrorScheme(
                        code=ErrorStatus.INVALID_INPUT_FORMAT.value,
                        message="Invalid input format",
                    ),
                ).model_dump()
            )

            return

        if message["message_type"] == ServerMessageType.HEARTBEAT.value:
            self.rooms[room_number].player_heartbeats[client] = 0
            return

        if message["message_type"] == ServerMessageType.SERVER_INFO.value:
            await self.handle_server_info_message(room_number, message)

        if message["message_type"] == ServerMessageType.USER_ACTION.value:
            if self.rooms[room_number].current_player == client:
                self.rooms[room_number].histories.append(message)

                for room_client in self.rooms[room_number].clients:
                    if room_client != client:
                        await room_client.send_json(message)

                # 유저 행동이 들어왔을 때 카운트다운 재시작
                await self.reset_countdown(room_number)
                await self.switch_current_player(room_number)
            else:
                await client.send_json(
                    ServerResponse(
                        message_type=ServerMessageType.ERROR.value,
                        error=ServerErrorScheme(
                            code=ErrorStatus.NOT_YOUR_TURN.value,
                            message="Not your turn",
                        ),
                    ).model_dump()
                )

        if message["message_type"] == ServerMessageType.ERROR.value:
            return

        return

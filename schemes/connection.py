from enum import Enum

from pydantic import BaseModel, Field
from starlette.websockets import WebSocket


class InfoStatus(Enum):
    CONNECTED_TO_ROOM = 102
    READY_TO_PLAY = 103
    GAME_START = 301
    CONNECTION_ENDED = 302
    PLAYER_HAS_LEFT_THE_CONNECTION = 202


class ErrorStatus(Enum):
    ROOM_IS_FULL = 100
    ROOM_DOES_NOT_EXIST = 101
    NOT_YOUR_TURN = 200
    INVALID_MOVE = 201
    INVALID_INPUT_FORMAT = 203
    CONNECTION_NOT_STARTED = 300
    CONNECTION_LOST = 400
    INTERNAL_SERVER_ERROR = 500


class ServerMessageType(Enum):
    SERVER_INFO = "server_info"
    ERROR = "error"


class RoomInfo(BaseModel):
    clients: list[WebSocket] = Field(
        default=[], description="List of clients in the room"
    )
    current_player: WebSocket | None = Field(
        description="Current player in the room", default=None
    )
    histories: list[dict] = Field(description="Game history", default=[])
    ready_to_play: int = Field(description="Ready Players", default=0)

    class Config:
        arbitrary_types_allowed = True


class ServerInfoScheme(BaseModel):
    code: int = Field(..., description="status code")
    message: str = Field(..., description="status message")
    data: dict | None = Field(None, description="data")


class ServerErrorScheme(BaseModel):
    code: int = Field(..., description="status code")
    message: str = Field(..., description="status message")


class ServerResponse(BaseModel):
    message_type: ServerMessageType = Field(..., description="message type")
    server_info: ServerInfoScheme | None = Field(None, description="server info")
    error: ServerErrorScheme | None = Field(None, description="error")

    class Config:
        use_enum_values = True

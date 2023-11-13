from pydantic import BaseModel, Field
from starlette.websockets import WebSocket

from core.enum import ServerMessageType


class RoomInfo(BaseModel):
    clients: list[WebSocket] = Field(
        default=[], description="List of clients in the room"
    )
    current_player: WebSocket | None = Field(
        description="Current player in the room", default=None
    )
    histories: list[dict] = Field(description="Game history", default=[])
    ready_to_play: int = Field(description="Ready Players", default=0)
    tic: int = Field(description="Countdown", default=90)
    player_heartbeats: dict[WebSocket, int] = Field(
        description="Player heartbeats", default={}
    )

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

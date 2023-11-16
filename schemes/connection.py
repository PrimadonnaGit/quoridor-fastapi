from pydantic import BaseModel, Field
from starlette.websockets import WebSocket

from core.enum import ErrorStatus, InfoStatus, ServerMessageType


class RoomInfo(BaseModel):
    clients: list[WebSocket] = Field(
        default=[], description="List of clients in the room"
    )
    current_player: WebSocket | None = Field(
        description="Current player in the room", default=None
    )
    player_ids: list[int] = Field(description="Player ids", default=[])
    histories: list[dict] = Field(description="Game history", default=[])
    ready_to_play: int = Field(description="Ready Players", default=0)
    tic: int = Field(description="Countdown", default=90)
    player_heartbeats: dict[WebSocket, int] = Field(
        description="Player heartbeats", default={}
    )

    class Config:
        arbitrary_types_allowed = True


class ServerInfoScheme(BaseModel):
    code: InfoStatus = Field(..., description="status code")
    message: str = Field(..., description="status message")
    data: dict | None = Field(None, description="data")

    class Config:
        use_enum_values = True


class ServerErrorScheme(BaseModel):
    code: ErrorStatus = Field(..., description="status code")
    message: str = Field(..., description="status message")

    class Config:
        use_enum_values = True


class WebsocketMessageScheme(BaseModel):
    message_type: ServerMessageType = Field(..., description="message type")
    server_info: ServerInfoScheme | None = Field(None, description="server info")
    error: ServerErrorScheme | None = Field(None, description="error")

    class Config:
        use_enum_values = True

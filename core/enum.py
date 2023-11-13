from enum import Enum


class InfoStatus(Enum):
    PING = 0
    CONNECTED_TO_ROOM = 102
    READY_TO_PLAY = 103
    GAME_START = 301
    CONNECTION_ENDED = 302
    PLAYER_HAS_LEFT_THE_CONNECTION = 202
    COUNTDOWN = 303
    GAME_END = 304


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
    USER_ACTION = "user_action"
    HEARTBEAT = "heartbeat"

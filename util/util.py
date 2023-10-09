STATUS_CODE = {
    100: "room is full",
    101: "room does not exist",
    102: "connected to room",
    200: "not your turn",
    201: "invalid move",
    202: "player has left the connection. Start a new connection",
    203: "invalid input format",
    300: "connection not started",
    301: "connection started",
    302: "connection ended",
    400: "connection lost",
    500: "internal server error",
}


class ServerInfoResponse:
    def __init__(self, status_code: int, data: dict = None):
        self.message_type = "server_info"
        self.code = status_code
        self.message = STATUS_CODE[status_code]
        self.data = data

    def to_dict(self):
        return {
            "message_type": self.message_type,
            "server_info": {
                "code": self.code,
                "message": self.message,
                "data": self.data,
            },
        }


class ErrorResponse:
    def __init__(self, status_code: int):
        self.message_type = "error"
        self.code = status_code
        self.message = STATUS_CODE[status_code]

    def to_dict(self):
        return {
            "message_type": self.message_type,
            "error": {
                "code": self.code,
                "message": self.message,
            },
        }

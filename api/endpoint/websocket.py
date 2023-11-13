import logging

from fastapi import APIRouter
from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from api.service.websocket import WebsocketConnectionManager

router = APIRouter()

manager = WebsocketConnectionManager()


@router.websocket("")
async def websocket_endpoint(websocket: WebSocket):
    room_number = await manager.new_connection(websocket)

    try:
        while True:
            await manager.communicate(
                websocket,
                room_number,
            )

    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        logging.info("ws, client disconnected")
        await manager.stop_countdown(room_number)
        await manager.disconnect(websocket, room_number)
    except Exception as e:
        logging.error(f"ws, {e}")


@router.websocket("/{room_number}")
async def websocket_endpoint_with_rood_id(websocket: WebSocket, room_number: int):
    await manager.connect(websocket, room_number)

    try:
        while True:
            await manager.communicate(
                websocket,
                room_number,
            )

    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        logging.info("ws, client disconnected")
        await manager.stop_countdown(room_number)
        await manager.disconnect(websocket, room_number)
    except Exception as e:
        logging.error(f"ws, {e}")

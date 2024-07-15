from fastapi import WebSocket, WebSocketDisconnect, APIRouter
from config import manager


router = APIRouter(
    prefix='/notification',
    tags=['Notification']
)


@router.websocket("/{user_id}")
async def notification_feed(
    user_id: int,
    websocket: WebSocket,
):
    await manager.connect(user_id, websocket)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)



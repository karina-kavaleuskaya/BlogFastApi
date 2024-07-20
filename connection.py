from typing import Dict
from fastapi import WebSocket
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_multiple(self, users: list[int], text: str):
        for user_id in users:
            conn = self.active_connections.get(user_id)

            if conn is None:
                logger.warning(
                    f"Connection for a user (user_id={user_id}) is not found.")
                continue

            try:
                await conn.send_text(text)
            except Exception:
                logger.warning(
                    f"Something went wrong while sending message to a user (user_id={user_id})")
import json
import enum
from dataclasses import dataclass
import logging
from connection import ConnectionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(str, enum.Enum):
    new_post = "New post",
    new_sub = "New sub"


@dataclass
class Notification:
    type: NotificationType
    text: str

    def to_json_str(self):
        return json.dumps({
            "type": self.type,
            "text": self.text
        })


class NotificationService:
    def __init__(self, conn_manager: ConnectionManager):
        self.conn_manager = conn_manager

    async def send_new_post_notification(self, users: list[int], author_id: int):
        await self.conn_manager.send_multiple(users, Notification(
            type=NotificationType.new_post,
            text=f"User with id {author_id} created new post!"
        ).to_json_str())


manager = ConnectionManager()
notification_service = NotificationService(manager)
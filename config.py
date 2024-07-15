import os
from fastapi_mail import ConnectionConfig
from fastapi import UploadFile, HTTPException, status
from aiobotocore.session import get_session
import json
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
import logging
from typing import Dict
from fastapi import WebSocket
import enum
from dataclasses import dataclass



load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationType(str, enum.Enum):
    NEW_POST = "NEW_POST"


@dataclass
class Notification:
    type: NotificationType
    text: str

    def to_json_str(self):
        return json.dumps({
            "type": self.type,
            "text": self.text
        })


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


class NotificationService:
    def __init__(self, conn_manager: ConnectionManager):
        self.conn_manager = conn_manager

    async def send_new_post_notification(self, users: list[int], author_id: int):
        await self.conn_manager.send_multiple(users, Notification(
            type=NotificationType.NEW_POST,
            text=f"User with id {author_id} created new post!"
        ).to_json_str())


manager = ConnectionManager()
notification_service = NotificationService(manager)


SQLALCHEMY_DATABASE_URL = os.getenv('SQLALCHEMY_DATABASE_URL')
ALGORITHM = 'HS256'
SECRET_KEY = os.getenv('SECRET_KEY')
REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES = 25
REFRESH_TOKEN_EXPIRE_DAYS = 15
PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_SCHEME = OAuth2PasswordBearer(tokenUrl='auth/login')


class Envs:
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_PORT = int(os.getenv('MAIL_PORT'))
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_FROM_NAME = os.getenv('MAIL_FROM_NAME')


conf = ConnectionConfig(
    MAIL_USERNAME=Envs.MAIL_USERNAME,
    MAIL_PASSWORD=Envs.MAIL_PASSWORD,
    MAIL_FROM=Envs.MAIL_FROM,
    MAIL_PORT=Envs.MAIL_PORT,
    MAIL_SERVER=Envs.MAIL_SERVER,
    MAIL_FROM_NAME=Envs.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)


class FileManager:
    def __init__(self):
        self.bucket_name = os.getenv("BUCKET_NAME")
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.endpoint_url = os.getenv('ENDPOINT_URL')
        self.region_name = os.getenv('REGION_NAME')

    async def save_file(self, file: UploadFile, file_name: str) -> None:
        session = get_session()
        async with session.create_client(
            's3',
            region_name=self.region_name,
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key
        ) as client:
            try:
                data = await file.read()
                await client.put_object(Bucket=self.bucket_name, Key=file_name, Body=data)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Can't save file")

    async def get_file(self, file_path: str) -> bytes:
        session = get_session()
        async with session.create_client(
                's3',
                region_name=self.region_name,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
        ) as client:
            try:
                response = await client.get_object(Bucket=self.bucket_name, Key=file_path)
                async with response['Body'] as stream:
                    data = await stream.read()
                    return data
            except client.exceptions.NoSuchKey as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Song file not found')
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Could not save file')

    async def delete_file(self,file_path:str) -> None:
        session = get_session()
        async with session.create_client(
                's3',
                region_name=self.region_name,
                endpoint_url=self.endpoint_url,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key
        ) as client:
            try:
                await client.delete_object(Bucket=self.bucket_name, Key=file_path)
            except client.exceptions.NoSuchKey as e:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Song file not found')
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='Could not save file')


file_manager = FileManager()
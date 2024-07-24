import os
from fastapi_mail import ConnectionConfig
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv
from services.notification import NotificationService
from services.files import FileSerivce
from connection import ConnectionManager


load_dotenv()

reset_link = f"https://127.0.0.1/auth/reset-password/confirm?token="
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


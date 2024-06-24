import os
from fastapi import Depends, HTTPException, status
from db.async_db import get_db
from sqlalchemy.future import select
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import models
from dotenv import load_dotenv
from config import ALGORITHM, SECRET_KEY, REFRESH_SECRET_KEY, REFRESH_TOKEN_EXPIRE_DAYS

load_dotenv()


PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_SCHEME = OAuth2PasswordBearer(tokenUrl='auth/login')


async def get_user(db:AsyncSession, email):
    async with db:
        result = await db.execute(select(models.User).filter(models.User.email == email))
        return result.scalars().first()


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta):
    data_to_process = data.copy()
    expire = datetime.utcnow() + expires_delta
    data_to_process.update({'exp': expire})
    encode_jwt = jwt.encode(data_to_process, SECRET_KEY, algorithm=ALGORITHM)
    return encode_jwt


def create_refresh_token(data: dict, expires_delta: timedelta):
    data_to_process = data.copy()
    expire = datetime.utcnow() + expires_delta
    data_to_process.update({'exp': expire})
    refresh_token = jwt.encode(data_to_process, REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return refresh_token


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user(db, email)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


def create_password_reset_token(data: dict):
    return jwt.encode(data, REFRESH_SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(OAuth2_SCHEME),
                           db: AsyncSession = Depends(get_db)):

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(token.access_token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get('sub')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate credentials',
                headers={'WWW-Authenticate': 'Bearer'}
            )

        user = await db.execute(select(models.User).filter(models.User.email == email))
        user = user.scalars().first()
        if not user:
            raise credential_exception
        refresh_payload = jwt.decode(token.refresh_token, REFRESH_SECRET_KEY, algorithms=ALGORITHM)
        if refresh_payload.get('sub') != email:
            raise credential_exception

        return user
    except (JWTError, AttributeError):
        raise credential_exception


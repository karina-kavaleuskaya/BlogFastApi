from fastapi import Depends, HTTPException, status, Request
from db.async_db import get_db
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import logging
import models
from config import (ALGORITHM, SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS,
                    PWD_CONTEXT)
from repository.user import get_user_by_email_db, get_user_by_id_db
from repository.auth import register_db, reset_token_db, get_token_db, get_user_by_token_db, change_password_db
from services.send_email import send_password_reset_email


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def get_user(db: AsyncSession, email):
    user = await get_user_by_email_db(db, email)
    return user


async def get_id_user(db, user_id):
    user = await get_user_by_id_db(db, user_id)
    return user


def verify_password(plain_password, hashed_password):
    return PWD_CONTEXT.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(user_id: int, expires_delta: timedelta = None):
    to_encode = {"user_id": user_id}
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email_db(db, email)
    if not user or not verify_password(password, user.password_hash):
        return False
    return user


def create_password_reset_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def get_access_token_from_cookie(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found in cookie"
        )
    return access_token


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    access_token: str = Depends(get_access_token_from_cookie)
) -> models.User:
    try:
        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=ALGORITHM
        )
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )

    user = await get_user_by_id_db(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


def verify_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.InvalidTokenError:
        return None


async def set_user_authorized_state(request: Request, user: models.User):
    try:
        logger.info(f"Setting authorized state for user: {user.id}")
        request.state.user = user
        request.state.access_token = create_access_token({"sub": str(user.id)})
        logger.info("User authorized state set successfully")
    except Exception as e:
        logger.error(f"Error setting user authorized state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set user authorized state"
        )


async def register_user(db, user):
    db_user = await get_user_by_email_db(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists!')

    hashed_password = PWD_CONTEXT.hash(user.password)
    db_user = await register_db(db, user, hashed_password)
    return db_user


async def reset_user_password(db, request):
    user = await get_user_by_email_db(db, request.email)
    if user:
        reset_token = create_password_reset_token(data={"sub": user.email})
        await send_password_reset_email(user.email, reset_token)
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        reset_token_obj = await reset_token_db(db, reset_token, expire, user)

        return reset_token_obj
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist."
        )


async def reset_password_confirm(db, request):
    token = await get_token_db(db, request)

    if token:
        if token.reset_token_expire > datetime.utcnow():
            user = await get_user_by_token_db(db, token)

            if user:
                user.password_hash = PWD_CONTEXT.hash(request.new_password)
                user = change_password_db(db, user, token)

                return user

            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired.",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reset token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
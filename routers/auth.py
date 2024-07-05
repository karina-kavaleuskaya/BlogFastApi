from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Form
from db.async_db import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
from schemas import users
import logging
import models
from services.send_email import send_password_reset_email
from schemas.auth import PasswordResetRequest, PasswordResetResponse, PasswordResetToken
from services.auth import (get_user, create_access_token, create_refresh_token, authenticate_user,
                           create_password_reset_token)
from config import REFRESH_TOKEN_EXPIRE_DAYS, PWD_CONTEXT


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/register/', response_model=users.User)
async def register(user: users.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await get_user(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='User already exists!')

    hashed_password = PWD_CONTEXT.hash(user.password)
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        second_name=user.second_name,
        nickname=user.nickname,
        password_hash=hashed_password,
        sex_id=user.sex_id,
        country_id=user.country_id,
        created_at=datetime.now(),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/login/")
async def login(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
    username: str = Form(...),
    password: str = Form(...)
):
    user = await authenticate_user(db, username, password)
    if not user:
        return JSONResponse(status_code=401, content={"error": "Invalid credentials"})

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token(user.id)

    response.set_cookie(key="access_token", value=access_token, httponly=True)
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True)

    return {"access_token": access_token}


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await db.execute(
        select(models.User).where(models.User.email == request.email)
    )
    user = user.scalar()

    if user:
        reset_token = create_password_reset_token(data={"sub": user.email})
        await send_password_reset_email(user.email, reset_token)
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        expire = datetime.utcnow() + expires_delta
        reset_token_obj = models.Tokens(
            reset_token=reset_token,
            reset_token_expire=expire,
            user_id=user.id
        )
        db.add(reset_token_obj)
        await db.commit()

        return PasswordResetResponse(message="Password reset instructions sent to your email.")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist."
        )


@router.post("/reset-password/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    request: PasswordResetToken,
    db: AsyncSession = Depends(get_db)
):
    token = await db.execute(
        select(models.Tokens).where(models.Tokens.reset_token == request.token)
    )
    token = token.scalar()

    if token:
        if token.reset_token_expire > datetime.utcnow():
            user = await db.get(models.User, token.user_id)

            if user:
                user.password_hash = PWD_CONTEXT.hash(request.new_password)
                db.add(user)
                await db.commit()

                await db.delete(token)
                await db.commit()

                return PasswordResetResponse(message="Password reset successfully.")
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
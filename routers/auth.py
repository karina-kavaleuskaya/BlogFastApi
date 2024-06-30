from fastapi import APIRouter, Depends, HTTPException, status
from db.async_db import get_db
from sqlalchemy.future import select
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from schemas import users, auth
import models
from services.send_email import send_password_reset_email
from schemas.auth import Token, PasswordResetRequest, PasswordResetResponse, PasswordResetToken
from dotenv import load_dotenv
from services.auth import (get_user, create_access_token, create_refresh_token, authenticate_user,
                           create_password_reset_token, )
from config import ALGORITHM, REFRESH_SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS

load_dotenv()


PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
OAuth2_SCHEME = OAuth2PasswordBearer(tokenUrl='auth/login')

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):

    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=15))
    refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=timedelta(days=7))
    user.refresh_token = refresh_token
    await db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/token/refresh", response_model=Token)
async def refresh_token(reset_token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(reset_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await db.execute(select(models.User).filter(models.User.email == email))
        user = user.scalars().first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=15))

        new_refresh_token = create_refresh_token(data={"sub": user.email}, expires_delta=timedelta(days=7))
        user.refresh_token = new_refresh_token
        await db.commit()

        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
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


@router.post('/login/', response_model=auth.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect email or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    access_token_expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expire = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={'sub': user.email}, expires_delta=access_token_expire
    )
    refresh_token = create_refresh_token(
        data={'sub': user.email}, expires_delta=refresh_token_expire
    )

    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


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
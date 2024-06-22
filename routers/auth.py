from fastapi import APIRouter, Depends, HTTPException, status
from configs.async_db import get_db
from sqlalchemy.future import select
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from schemas import users, auth
import models
from typing import Optional
from schemas.auth import Token

PWD_CONTEXT = CryptContext(schemes=['bcrypt'], deprecated='auto')
ALGORITHM = 'HS256'
SECRET_KEY = 'dcfvghjkljhvcxvbnm'
REFRESH_SECRET_KEY = "xcgyuciosl8v6bn2mj5hbghjfkdxsl"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 5
OAuth2_SCHEME = OAuth2PasswordBearer(tokenUrl='auth/login')

router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


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
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
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
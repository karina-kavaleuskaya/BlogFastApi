from fastapi import APIRouter, Depends, Request, Response, Form
from db.async_db import get_db
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import users
import logging
from schemas.auth import PasswordResetRequest, PasswordResetResponse, PasswordResetToken
from services.auth import (create_access_token, create_refresh_token, authenticate_user,
                           reset_user_password, register_user, reset_password_confirm)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


router = APIRouter(
    prefix='/auth',
    tags=['Auth']
)


@router.post('/register/', response_model=users.User)
async def register(user: users.UserCreate, db: AsyncSession = Depends(get_db)):
    db_user = await register_user(user, db)
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

    return {"access_token": access_token}


@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(
    request: PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    token = await reset_user_password(request, db)
    return PasswordResetResponse(message=f"{token} reset instructions sent to your email.")


@router.post("/reset-password/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(
    request: PasswordResetToken,
    db: AsyncSession = Depends(get_db)
):
    user = reset_password_confirm(request, db)
    return PasswordResetResponse(message="Password reset successfully.")
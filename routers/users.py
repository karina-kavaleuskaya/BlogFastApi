from fastapi import APIRouter, Depends, HTTPException, status
from configs.async_db import get_db
from sqlalchemy.future import select
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import models
import schemas


router = APIRouter(
    prefix='/users',
    tags=['Users']
)


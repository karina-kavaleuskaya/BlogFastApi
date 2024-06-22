import models
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  HTTPException, Depends, APIRouter
from configs.async_db import get_db
from sqlalchemy.future import select
from routers.auth import get_current_user
from fastapi import status


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)
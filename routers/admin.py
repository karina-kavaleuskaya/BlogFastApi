from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from typing import Tuple, List, Optional
import schemas
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from sqlalchemy.future import select
from services.auth import get_current_user
from sqlalchemy import desc


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)






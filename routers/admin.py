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


@router.patch('/{user_id}', status_code=status.HTTP_200_OK)
async def ban_user(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user),
):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if user_role.name not in ['superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role_id = role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user



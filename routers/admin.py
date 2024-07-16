from fastapi import APIRouter, HTTPException, status, Depends
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from services.auth import get_current_user
from services.admin import change_user_role


router = APIRouter(
    prefix='/admin',
    tags=['Admin']
)


@router.patch('/{user_id}', status_code=status.HTTP_200_OK)
async def change_role(
    user_id: int,
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user),
):
    user = await change_user_role(user_id, role_id, db, current_user)
    return user



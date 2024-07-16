from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from typing import Tuple, List, Optional
import schemas
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from sqlalchemy.future import select
from services.auth import get_current_user
from sqlalchemy import desc, update
from services.user import user_ban, get_all_users, search

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get('/all-users/', response_model=Tuple[List[schemas.users.UsersForAdmin], schemas.posts.PaginationInfo])
async def all_users(
        sex_id: int | None = None,
        country_id: int | None = None,
        name: str | None = None,
        order_by: str = 'created_at',
        sort_direction: str = None,
        page: int = 1,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)
):
    page_size = 10

    user_list = await get_all_users(sex_id, country_id, name, order_by, sort_direction, page, db, current_user)

    if user_list:
        first_post = user_list[0]
        last_post = user_list[-1]
        pagination_info = schemas.posts.PaginationInfo(
                last_viewed_at=last_post.created_at,
                next_page=f"?page={page + 1}" if len(user_list) == page_size else None,
                prev_page=f"?page={page - 1}" if page > 1 else None
        )
    else:
        pagination_info = schemas.posts.PaginationInfo(
                last_viewed_at=datetime.now(),
                next_page=None,
                prev_page=None
        )

    return user_list, pagination_info


@router.get('/search/', response_model=Tuple[List[schemas.users.UsersForAdmin], schemas.posts.PaginationInfo])
async def search_users(
        name: str | None = None,
        page: int = 1,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)
):
    user_list = await search(name, db)
    page_size = 10
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    users_to_return = user_list[start_index:end_index]

    if users_to_return:
            first_user = users_to_return[0]
            last_user = users_to_return[-1]
            pagination_info = schemas.posts.PaginationInfo(
                last_viewed_at=last_user.created_at,
                next_page=f"?page={page + 1}" if len(users_to_return) == page_size else None,
                prev_page=f"?page={page - 1}" if page > 1 else None
        )
    else:
        pagination_info = schemas.posts.PaginationInfo(
                last_viewed_at=datetime.now(),
                next_page=None,
                prev_page=None
        )

    return users_to_return, pagination_info


@router.patch('/ban/{user_id}', status_code=status.HTTP_200_OK)
async def ban_user(
    user_id: int,
    ban: bool,
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user),
):
    user = await user_ban(user_id, ban, db, current_user)
    return f'User {user_id} ban {ban}'
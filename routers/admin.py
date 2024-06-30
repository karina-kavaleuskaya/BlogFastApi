from fastapi import APIRouter, HTTPException, status, Depends
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


@router.get('/user-list/', response_model=Tuple[List[schemas.users.UsersForAdmin], schemas.posts.PaginationInfo])
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
    if current_user.role_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")

    page_size = 10

    async with db:
        query = select(models.User)

        if sex_id is not None:
            query = query.where(models.User.sex_id == sex_id)

        if country_id is not None:
            query = query.where(models.User.country_id == country_id)

        if name is not None:
            query = query.filter(
                models.User.first_name.ilike(f'%{name}%') |
                models.User.second_name.ilike(f'%{name}%') |
                models.User.email.ilike(f'%{name}%') |
                models.User.nickname.ilike(f'%{name}%')
            )

        if order_by == 'created_at':
            if sort_direction == 'new':
                query = query.order_by(desc(models.User.created_at))
            elif sort_direction == 'old':
                query = query.order_by(models.User.created_at)

        if page > 1:
            query = query.offset((page - 1) * page_size)
        query = query.limit(page_size)

        result = await db.execute(query)
        user_list = result.scalars().all()

        if not user_list:
            return [], schemas.posts.PaginationInfo(
                last_viewed_at=None,
                next_page=None,
                prev_page=None
            )

        first_post = user_list[0]
        last_post = user_list[-1]
        pagination_info = schemas.posts.PaginationInfo(
            last_viewed_at=last_post.created_at,
            next_page=f"?page={page + 1}" if len(user_list) == page_size else None,
            prev_page=f"?page={page - 1}" if page > 1 else None
        )

        return user_list, pagination_info


@router.post('/create-topic/', response_model=schemas.posts.TopicBase, status_code=status.HTTP_201_CREATED)
async def create_topic(topic: schemas.posts.TopicBase, db: AsyncSession = Depends(get_db),
                      current_user: schemas.users.User = Depends(get_current_user)):

    if current_user.role_id == 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")

    new_topic = models.Topics(**topic.dict())
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic
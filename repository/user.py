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


async def ban_user_db(user_id, ban, db, current_user):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if user_role.name not in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if ban and user.banned_is:
        raise HTTPException(status_code=400, detail="User is already banned")
    elif not ban and not user.banned_is:
        raise HTTPException(status_code=400, detail="User is not banned")

    user.banned_is = ban
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_all_users_db(sex_id, country_id, name, order_by, sort_direction, page, db, current_user):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

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

        user_list = [user for user in user_list if not user.banned_is]
        return user_list


async def search_users_db(name, db):
    async with db:
        query = select(models.User)

        if name is not None:
            query = query.filter(
                models.User.first_name.ilike(f'%{name}%') |
                models.User.second_name.ilike(f'%{name}%') |
                models.User.email.ilike(f'%{name}%') |
                models.User.nickname.ilike(f'%{name}%')
            )

        user_list = await db.execute(query)
        user_list = user_list.scalars().all()
        user_list = [user for user in user_list if not user.banned_is]

        return user_list

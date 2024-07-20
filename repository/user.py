import models
from sqlalchemy.future import select
from sqlalchemy import desc


async def ban_user_db(user, ban, db):
    user.banned_is = ban
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_all_users_db(sex_id, country_id, name, order_by, sort_direction, page, db):
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


async def get_user_role(db, current_user):
    user_role = await db.get(models.Roles, current_user.role_id)
    return user_role


async def get_user_by_id(db, user_id):
    admin = await db.get(models.User, user_id)
    return admin


async def get_user_by_email(db, email):
    result = await db.execute(select(models.User).filter(models.User.email == email))
    user = result.scalars().first()
    return user
import models
from datetime import datetime
from sqlalchemy.future import select


async def register_db(db, user, hashed_password):
    db_user = models.User(
        email=user.email,
        first_name=user.first_name,
        second_name=user.second_name,
        nickname=user.nickname,
        password_hash=hashed_password,
        sex_id=user.sex_id,
        country_id=user.country_id,
        created_at=datetime.now(),
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def reset_token_db(db, reset_token, expire, user):
    reset_token_obj = models.Tokens(
        reset_token=reset_token,
        reset_token_expire=expire,
        user_id=user.id
    )
    db.add(reset_token_obj)
    await db.commit()
    return reset_token_obj


async def get_token_db(db, request):
    token = await db.execute(
        select(models.Tokens).where(models.Tokens.reset_token == request.token)
    )
    token = token.scalar()
    return token


async def get_user_by_token_db(db, token):
    user = await db.get(models.User, token.user_id)
    return user


async def change_password_db(db, user, token):
    db.add(user)
    await db.commit()

    await db.delete(token)
    await db.commit()
    return user
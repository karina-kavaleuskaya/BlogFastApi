from repository.user import ban_user_db, get_all_users_db, search_users_db, get_user_role_db, get_user_by_id_db
from fastapi import status, HTTPException


async def user_ban(db, user_id, ban, current_user,):
    try:
        user_role = await get_user_role_db(db, current_user)

        if user_role.name not in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user = await get_user_by_id_db(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if ban and user.banned_is:
        raise HTTPException(status_code=400, detail="User is already banned")
    elif not ban and not user.banned_is:
        raise HTTPException(status_code=400, detail="User is not banned")

    user = await ban_user_db(db, user, ban)

    return user


async def get_all_users(db, sex_id, country_id, name, order_by, sort_direction, page, current_user):
    try:
        user_role = await get_user_role_db(db, current_user)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user_list = await get_all_users_db(db, sex_id, country_id, name, order_by, sort_direction, page)
    return user_list


async def search(db, name):
    user_list = await search_users_db(db, name)
    return user_list




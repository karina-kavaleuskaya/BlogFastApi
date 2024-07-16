from repository.user import ban_user_db, get_all_users_db, search_users_db


async def user_ban(user_id, ban, db, current_user,):
    user = await ban_user_db(user_id, ban, db, current_user)
    return user


async def get_all_users(sex_id, country_id, name, order_by, sort_direction, page, db, current_user):
    user_list = await get_all_users_db(sex_id, country_id, name, order_by, sort_direction, page, db, current_user)
    return user_list


async def search(name, db):
    user_list = await search_users_db(name, db)
    return user_list




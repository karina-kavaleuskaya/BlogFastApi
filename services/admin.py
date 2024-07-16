from repository.admin import change_role_db

async def change_user_role(user_id, role_id, db, current_user):
    user = await change_role_db(user_id, role_id, db, current_user)
    return user
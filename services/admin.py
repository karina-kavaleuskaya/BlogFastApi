from repository.admin import change_role_db
from fastapi import status, HTTPException
from repository.user import get_user_role, get_user_by_id


async def change_user_role(user_id, role_id, db, current_user):
    try:
        user_role = await get_user_role(db, current_user)

        if user_role.name not in ['superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user = await change_role_db(user, role_id, db)
    return user
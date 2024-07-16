from fastapi import HTTPException, status
import models


async def change_role_db(user_id, role_id, db, current_user):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if user_role.name not in ['superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    user = await db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role_id = role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
async def change_role_db(user, role_id, db):
    user.role_id = role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
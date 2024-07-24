async def change_role_db(db, user, role_id):
    user.role_id = role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
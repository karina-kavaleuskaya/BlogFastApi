from fastapi import HTTPException, status
import models
from sqlalchemy.future import select
from sqlalchemy import update


async def create_topic_db(topic, db, current_user):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    new_topic = models.Topics(**topic.dict())
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


async def update_topic_db(topic_id, title, db, user):
    topic = await db.execute(select(models.Topics).filter(models.Topics.id == topic_id))
    topic = topic.scalars().first()
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    try:
        user_role = await db.get(models.Roles, user.role_id)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    topic.title = title
    db.add(topic)
    await db.commit()
    await db.refresh(topic)

    return topic


async def delete_topic_db(topic_id, db, current_user):
    try:
        user_role = await db.get(models.Roles, current_user.role_id)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")

        topic = await db.get(models.Topics, topic_id)

        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found.")

        await db.execute(update(models.Post).where(models.Post.topic_id == topic_id).values(topic_id=None))

        await db.delete(topic)
        await db.commit()

        return {"message": "Topic deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_topics_db(db):
    result = await db.execute(select(models.Topics))
    topics = result.scalars().all()
    return topics
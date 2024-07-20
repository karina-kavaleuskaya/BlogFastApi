from repository.topic import create_topic_db, update_topic_db, delete_topic_db, get_topics_db, get_topic
from repository.user import get_user_role
from fastapi import status, HTTPException



async def create_new_topic(topic, db, current_user):
    try:
        user_role = await get_user_role(db, current_user)
        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    new_topic = await create_topic_db(topic, db)
    return new_topic


async def update_topic_serv(topic_id, title, db, current_user):
    topic = await get_topic(topic_id, db)
    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    try:
        user_role = await get_user_role(db, current_user)

        if not user_role.name in ['admin', 'superadmin']:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    topic = await update_topic_db(topic, title, db)
    return topic


async def delete_topic_serv(topic_id, db, current_user):
    user_role = await get_user_role(db, current_user)

    if not user_role.name in ['admin', 'superadmin']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admins can access this endpoint.")

    topic = await get_topic(topic_id, db)

    if not topic:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Topic not found.")

    topic = await delete_topic_db(topic, topic_id, db)
    return topic


async def get_topics(db):
    topics = await get_topics_db(db)
    return topics
from fastapi import HTTPException, status
import models
from sqlalchemy.future import select
from sqlalchemy import update


async def create_topic_db(db, topic):
    new_topic = models.Topics(
        title=topic.title
    )
    db.add(new_topic)
    await db.commit()
    await db.refresh(new_topic)
    return new_topic


async def update_topic_db(db, topic, title):
    topic.title = title
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


async def delete_topic_db(db, topic, topic_id):
    try:
        await db.execute(update(models.Post).where(models.Post.topic_id == topic_id).values(topic_id=None))
        await db.delete(topic)
        await db.commit()

        return topic

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_topics_db(db):
    result = await db.execute(select(models.Topics))
    topics = result.scalars().all()
    return topics


async def get_topic_db(db, topic_id):
    result = await db.execute(select(models.Topics).where(models.Topics.id == topic_id))
    topic = result.scalars().first()
    return topic


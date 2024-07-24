from fastapi import status, Depends, APIRouter
from schemas import topic, users
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from services.auth import get_current_user
from services.topic import create_new_topic, update_topic_serv, delete_topic_serv, get_topics


router = APIRouter(
    prefix='/topics',
    tags=['Topics']
)


@router.post('/', response_model=topic.TopicCreate, status_code=status.HTTP_201_CREATED)
async def create_topic(topic: topic.TopicCreate, db: AsyncSession = Depends(get_db),
                      current_user: users.User = Depends(get_current_user)):
    new_topic = await create_new_topic(db, topic, current_user)
    return new_topic


@router.put('/update/{topic_id}', response_model=topic.Topic, status_code=status.HTTP_201_CREATED)
async def update_topic(topic_id: int, title: str, db: AsyncSession = Depends(get_db),
                      user: models.User = Depends(get_current_user)):

    topic = await update_topic_serv(db, topic_id, title, user)
    return topic


@router.delete('/delete/{topic_id}')
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db),
                       current_user: users.User = Depends(get_current_user)):

    topic = await delete_topic_serv(db, topic_id, current_user)
    return f'You deleted the topic {topic.id}'


@router.get("/", response_model=list[topic.Topic])
async def all_topics(
        current_user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    topics = await get_topics(db)
    return topics

from fastapi import status, Depends, APIRouter
import schemas
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from services.auth import get_current_user
from services.topic import create_new_topic, update_topic_serv, delete_topic_serv, get_topics


router = APIRouter(
    prefix='/topics',
    tags=['Topics']
)


@router.post('/', response_model=schemas.posts.TopicBase, status_code=status.HTTP_201_CREATED)
async def create_topic(topic: schemas.posts.TopicBase, db: AsyncSession = Depends(get_db),
                      current_user: schemas.users.User = Depends(get_current_user)):
    new_topic = await create_new_topic(topic, db, current_user)
    return new_topic


@router.put('/update/{topic_id}', response_model=schemas.posts.Topic, status_code=status.HTTP_201_CREATED)
async def update_topic(topic_id: int, title: str, db: AsyncSession = Depends(get_db),
                      user: models.User = Depends(get_current_user)):

    topic = await update_topic_serv(topic_id, title, db, user)
    return topic


@router.delete('/delete/{topic_id}')
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db),
                       current_user: schemas.users.User = Depends(get_current_user)):

    topic = await delete_topic_serv(topic_id, db, current_user)


@router.get("/", response_model=list[schemas.posts.Topic])
async def all_topics(
        current_user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    topics = await get_topics(db)
    return topics

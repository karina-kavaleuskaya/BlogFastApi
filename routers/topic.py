from fastapi import HTTPException, status, Depends, APIRouter
import schemas
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from sqlalchemy.future import select
from services.auth import get_current_user
from sqlalchemy import update


router = APIRouter(
    prefix='/topics',
    tags=['Topics']
)


@router.post('/', response_model=schemas.posts.TopicBase, status_code=status.HTTP_201_CREATED)
async def create_topic(topic: schemas.posts.TopicBase, db: AsyncSession = Depends(get_db),
                      current_user: schemas.users.User = Depends(get_current_user)):
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


@router.put('/update/{topic_id}', response_model=schemas.posts.Topic, status_code=status.HTTP_201_CREATED)
async def update_topic(topic_id: int, title: str, db: AsyncSession = Depends(get_db),
                      user: models.User = Depends(get_current_user)):

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


@router.delete('/delete/{topic_id}')
async def delete_topic(topic_id: int, db: AsyncSession = Depends(get_db),
                       current_user: schemas.users.User = Depends(get_current_user)):
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


@router.get("/", response_model=list[schemas.posts.Topic])
async def get_topics(
        current_user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    async with db:
        result = await db.execute(select(models.Topics))
        topics = result.scalars().all()
        return topics

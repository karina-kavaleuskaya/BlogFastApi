from fastapi import HTTPException, status, Depends, APIRouter
import schemas
import models
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from sqlalchemy.future import select
from services.auth import get_current_user


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


@router.get("/", response_model=list[schemas.posts.Topic])
async def get_topics(
        current_user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    async with db:
        result = await db.execute(select(models.Topics))
        topics = result.scalars().all()
        return topics

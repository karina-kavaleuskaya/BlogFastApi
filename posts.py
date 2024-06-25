import models
import schemas
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  HTTPException, Depends, APIRouter
from async_db import get_db
from sqlalchemy.future import select
from users import get_current_user
from fastapi import status


router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=List[schemas.PostBase])
async def all_post(db: AsyncSession = Depends(get_db)):
    async with db:
        result = await db.execute(select(models.Post))
        posts = result.scalars().all()
        return posts


@router.post('/', response_model=schemas.PostBase, status_code=status.HTTP_201_CREATED)
async def create_post(post: schemas.PostBase, db: AsyncSession = Depends(get_db),
                      user: models.User = Depends(get_current_user)):
    new_post = models.Post(**post.dict(), user_id =user.id)
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    return new_post


@router.put('/{post_id}', response_model=schemas.PostBase)
async def update_post(
        post_id: int,
        update_post: schemas.PostBase,
        db: AsyncSession = Depends(get_db),
        user: models.User = Depends(get_current_user)
):
    post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to update this post')

    post.content = update_post.content
    post.title = update_post.title
    db.add(post)

    await db.commit()
    await db.refresh(post)

    return post

@router.delete('/{post_id}',)
async def delete_post(post_id:int, db: AsyncSession = Depends(get_db), user: models.User = Depends(get_current_user)):
    post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to update this post')

    await db.delete(post)
    await db.commit()


@router.get('/{post_id}', response_model=schemas.PostBase)
async def get_post_by_id(post_id: int, db: AsyncSession = Depends(get_db)):
    post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    return post

import models
from datetime import datetime
from schemas import posts, users
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from fastapi.encoders import jsonable_encoder
from sqlalchemy.future import select
from sqlalchemy import func
from fastapi import HTTPException, status, Depends, APIRouter, Form, UploadFile, File
from services.auth import get_current_user
from config import file_manager
from sqlalchemy.orm.exc import NoResultFound



router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get('/', response_model=Tuple[List[posts.PostResponse], posts.PaginationInfo])
async def all_posts(
    topic_ids: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    content: str | None = None,
    last_viewed_at: str | None = None,
    page: int = 1,
    db: AsyncSession = Depends(get_db),
        current_user: users.User = Depends(get_current_user)
):
    POSTS_PER_PAGE = 10

    async with db:
        current_user_db = await db.get(models.User, current_user.id)

        if current_user_db.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    async with db:
        topic_id_list = []
        if topic_ids:
            try:
                topic_id_list = [int(topic_id.strip()) for topic_id in topic_ids.split(',')]
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="topic_ids must contain only integer values"
                )

        query = select(models.Post)

        query = query.where(models.Post.user_id.not_in(
            select(models.User.id)
            .where(models.User.banned_is == True)
        ))

        if topic_id_list:
            query = query.where(models.Post.topic_id.in_(topic_id_list))

        if start_date is not None:
            try:
                start_datetime = datetime.fromisoformat(start_date)
                query = query.where(models.Post.created_at >= start_datetime)
            except ValueError:
                return [{"error": "Invalid start date format. Please use YYYY-MM-DDT00:00:00."}]

        if end_date is not None:
            try:
                end_datetime = datetime.fromisoformat(end_date)
                query = query.where(models.Post.created_at <= end_datetime)
            except ValueError:
                return [{"error": "Invalid end date format. Please use YYYY-MM-DDT00:00:00."}]

        if content:
            query = query.filter(
                models.Post.content.ilike(f'%{content}%') |
                models.Post.title.ilike(f'%{content}%')
            )

        # Add the last_viewed_at filter
        if last_viewed_at is not None:
            try:
                last_viewed_datetime = datetime.fromisoformat(last_viewed_at)
                query = query.where(models.Post.created_at > last_viewed_datetime)
            except ValueError:
                return [{"error": "Invalid last_viewed_at format. Please use YYYY-MM-DDT00:00:00."}]

        query = query.order_by(models.Post.created_at.desc())
        total_count = await db.execute(func.count(models.Post.id))
        total_count = total_count.scalar()

        total_pages = (total_count + POSTS_PER_PAGE - 1) // POSTS_PER_PAGE

        if page > total_pages:
            raise HTTPException(status_code=404, detail="Page not found")

        offset = (page - 1) * POSTS_PER_PAGE
        query = query.offset(offset)
        query = query.limit(POSTS_PER_PAGE)

        result = await db.execute(query)
        all_posts = result.scalars().all()

        posts_with_files = []
        for post in all_posts:
            post_response = posts.PostResponse(
                id=post.id,
                title=post.title,
                content=post.content,
                topic_id=post.topic_id or None,
                file_path=post.file_path,
                created_at=jsonable_encoder(post.created_at.date()),
            )
            posts_with_files.append(post_response)

        if posts_with_files:
            first_post = posts_with_files[0]
            last_post = posts_with_files[-1]
            pagination_info = posts.PaginationInfo(
                last_viewed_at=last_post.created_at,
                next_page=f"?page={page + 1}" if len(posts_with_files) == POSTS_PER_PAGE else None,
                prev_page=f"?page={page - 1}" if page > 1 else None
            )
        else:
            return [], posts.PaginationInfo(
                last_viewed_at=datetime.now(),
                next_page=None,
                prev_page=None
            )

        return posts_with_files, pagination_info


@router.post("/", response_model=posts.PostResponse)
async def create_post(
    title: str = Form(...),
    topic_id: Optional[int] = Form(None),
    content: str = Form(...),
    file: UploadFile = File(None),
    current_user: models.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    if current_user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    if len(title) > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Title must not exceed 300 characters'
        )
    if len(content) > 10000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Content must not exceed 10,000 characters'
        )

    file_path = None
    if file:
        file_path = f'static/posts/{file.filename}'
        await file_manager.save_file(file, file_path)

    db_post = models.Post(
        title=title,
        topic_id=topic_id,
        content=content,
        file_path=file_path,
        user_id=current_user.id,
        created_at=datetime.now()
    )
    db.add(db_post)
    await db.commit()
    await db.refresh(db_post)

    return db_post


@router.put('/{post_id}', response_model=posts.PostResponse)
async def update_post(
        post_id: int,
        title: str = Form(...),
        topic_id: Optional[int] = Form(None),
        content: str = Form(...),
        file: UploadFile = File(None),
        user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    if user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    post = post.scalars().first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to update this post')

    post.content = content
    post.title = title
    post.topic_id = topic_id

    if file:
        file_path = f'static/posts/{file.filename}'

        # Delete the previous file if it exists and is different from the new file
        if post.file_path and post.file_path != file_path:
            await file_manager.delete_file(post.file_path)

        await file_manager.save_file(file, file_path)
        post.file_path = file_path
    elif post.file_path:
        # If no new file is provided, but there was a previous file, delete the previous file
        await file_manager.delete_file(post.file_path)
        post.file_path = None

    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


@router.delete('/delete/{post_id}', response_model=posts.PostResponse, status_code=status.HTTP_200_OK)
async def delete_post(
        post_id: int,
        user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    try:
        post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
        post = post.scalars().first()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found: {str(e)}")

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to delete this post')

    try:
        topic = await db.execute(select(models.Topics).filter(models.Topics.id == post.topic_id))
        topic = topic.scalars().first()
        if topic:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail='Cannot delete a post that is associated with a topic')
    except NoResultFound:
        pass
    except Exception as e:
        if "module 'models' has no attribute 'Topic'" in str(e):
            pass
        else:
            raise e

    if post.file_path:
        try:
            await file_manager.delete_file(post.file_path)
        except Exception as e:
            raise e

    try:
        await db.delete(post)
        await db.commit()
    except Exception as e:
        raise e

    return post

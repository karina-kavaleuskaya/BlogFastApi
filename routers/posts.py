import models
from datetime import datetime
from schemas import posts, users
from typing import List, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from fastapi.encoders import jsonable_encoder
from fastapi import status, Depends, APIRouter, Form, UploadFile, File, BackgroundTasks
from services.auth import get_current_user
import logging
from services.post import delete_posts, update_post_serv, create_post_with_notification, get_all_posts


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


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

    posts_per_page = 10
    all_posts = await get_all_posts(topic_ids, start_date, end_date, content, last_viewed_at, page, db, current_user)
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
            next_page=f"?page={page + 1}" if len(posts_with_files) == posts_per_page else None,
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
    current_user: users.User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):

    db_post = await create_post_with_notification(title, topic_id, content, file, current_user, db)
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
    post = await update_post_serv(post_id, title, topic_id, content, file, user, db)
    return post


@router.delete('/delete/{post_id}', response_model=posts.PostResponse, status_code=status.HTTP_200_OK)
async def delete_post(
        post_id: int,
        user: models.User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    post = await delete_posts(post_id, user, db)
    return post





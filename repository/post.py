from sqlalchemy.future import select
from datetime import datetime
from sqlalchemy import func
from fastapi import status, HTTPException
import models


async def get_post(post_id, db):
    post = await db.execute(select(models.Post).filter(models.Post.id == post_id))
    post = post.scalars().first()
    return post


async def get_all_posts_db(topic_ids, start_date, end_date,content, last_viewed_at, page, db, current_user):

    posts_per_page = 10

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

        if last_viewed_at is not None:
            try:
                last_viewed_datetime = datetime.fromisoformat(last_viewed_at)
                query = query.where(models.Post.created_at > last_viewed_datetime)
            except ValueError:
                return [{"error": "Invalid last_viewed_at format. Please use YYYY-MM-DDT00:00:00."}]

        query = query.order_by(models.Post.created_at.desc())
        total_count = await db.execute(func.count(models.Post.id))
        total_count = total_count.scalar()

        total_pages = (total_count + posts_per_page - 1) // posts_per_page

        if page > total_pages:
            raise HTTPException(status_code=404, detail="Page not found")

        offset = (page - 1) * posts_per_page
        query = query.offset(offset)
        query = query.limit(posts_per_page)

        result = await db.execute(query)
        all_posts = result.scalars().all()

        return all_posts


async def update_post_db(post, db):
    db.add(post)
    await db.commit()
    await db.refresh(post)

    return post


async def create_post_db(title, topic_id, content, file_path, current_user, db):

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


async def delete_post(post, db):
    try:
        await db.delete(post)
        await db.commit()
    except Exception as e:
        raise e
    return post
from repository.post import get_post, delete_post, update_post_db, create_post_db, get_all_posts_db
from repository.topic import get_topic
from services.subscription import get_user_sub_in
from config import notification_service, file_manager
from fastapi import status, HTTPException


async def delete_posts(post_id, db, user):
    try:
        post = await get_post(post_id, db)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post not found: {str(e)}")

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to delete this post')

    if post.file_path:
        try:
            await file_manager.delete_file(post.file_path)
        except Exception as e:
            raise e

    post = await delete_post(post, db)
    return post


async def update_post_serv(post_id, title, topic_id, content, file, user, db):

    post = await get_post(post_id, db)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to update this post')

    topic_id = None
    if topic_id:
        topic = await get_topic(topic_id, db)
        if not topic:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Topic not found')

    post.content = content
    post.title = title
    post.topic_id = topic_id

    if file:
        file_path = f'static/posts/{file.filename}'

        if post.file_path and post.file_path != file_path:
            await file_manager.delete_file(post.file_path)

        await file_manager.save_file(file, file_path)
        post.file_path = file_path
    elif post.file_path:
        await file_manager.delete_file(post.file_path)
        post.file_path = None

    post = await update_post_db(post, db)

    return post


async def create_post_with_notification(title, topic_id, content, file, current_user, db):
    subscriptions = await get_user_sub_in(db, current_user)
    subscription_user_ids = [sub.subscriber_id for sub in subscriptions]
    await notification_service.send_new_post_notification(subscription_user_ids, current_user.id)
    file_path = None
    if file:
        file_path = f'static/posts/{file.filename}'
        await file_manager.save_file(file, file_path)
    post = await create_post_db(title, topic_id, content, file_path, current_user, db)
    return post


async def get_all_posts(topic_ids, start_date, end_date,content, last_viewed_at, page, db, current_user):
    all_posts = await get_all_posts_db(topic_ids, start_date, end_date,content, last_viewed_at, page, db, current_user)
    return all_posts
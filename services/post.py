from repository.post import get_post_db, delete_post_db, update_post_db, create_post_db, get_all_posts_db
from repository.topic import get_topic_db
from services.subscription import get_user_sub_in
from services.notification import notification_service
from services.files import file_manager
from fastapi import status, HTTPException


async def delete_posts(db, post_id, user):
    try:
        post = await get_post_db(db, post_id)
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

    post = await delete_post_db(db, post)
    return post


async def update_post_serv(db, post_id, title, topic_id, content, file, user):

    post = await get_post_db(db, post_id)

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Post does not exist')

    if post.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='You are not allowed to update this post')

    topic_id = None
    if topic_id:
        topic = await get_topic_db(db, topic_id)
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

    post = await update_post_db(db, post)

    return post


async def create_post_with_notification(db, title, topic_id, content, file, current_user):
    subscriptions = await get_user_sub_in(db, current_user)
    subscription_user_ids = [sub.subscriber_id for sub in subscriptions]
    await notification_service.send_new_post_notification(subscription_user_ids, current_user.id)
    file_path = None
    if file:
        file_path = f'static/posts/{file.filename}'
        await file_manager.save_file(file, file_path)
    post = await create_post_db(db, title, topic_id, content, file_path, current_user)
    return post


async def get_all_posts(db, topic_ids, start_date, end_date,content, last_viewed_at, page, current_user):
    all_posts = await get_all_posts_db(db, topic_ids, start_date, end_date,content, last_viewed_at, page, current_user)
    return all_posts
from repository.post import delete_post_db, update_post_db, create_post_db, get_all_posts_db
from services.subscription import search_subscription
from config import notification_service


async def delete_posts(post_id, user, db):
    post = await delete_post_db(post_id, user, db)
    return post


async def update_post_serv(post_id, title, topic_id, content, file, user, db):
    post = await update_post_db(post_id, title, topic_id, content, file, user, db)
    return post


async def create_post_with_notification(title, topic_id, content, file, current_user, db):
    subscriptions = await search_subscription(db, current_user.id)
    subscription_user_ids = [sub.subscriber_id for sub in subscriptions]
    await notification_service.send_new_post_notification(subscription_user_ids, current_user.id)
    post = await create_post_db(title, topic_id, content, file, current_user, db)
    return post


async def get_all_posts(topic_ids, start_date, end_date,content, last_viewed_at, page, db, current_user):
    all_posts = await get_all_posts_db(topic_ids, start_date, end_date,content, last_viewed_at, page, db, current_user)
    return all_posts
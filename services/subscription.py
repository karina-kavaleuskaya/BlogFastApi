from repository.subscription import (search_subscriptions, create_subscription_db, get_user_subscriptions_on_db,
                                     get_user_subscriptions_in_db, delete_subscription_db)


async def search_subscription(db, user_id):
    subscription = await search_subscriptions(db, user_id)
    return subscription


async def create_sub(db, current_user, subscription):
    new_subscription = await create_subscription_db(db, current_user, subscription)
    return new_subscription


async def get_user_sub_on(db, current_user):
    subscriptions = await get_user_subscriptions_on_db(db, current_user)
    return subscriptions


async def get_user_sub_in(db, current_user):
    subscriptions = await get_user_subscriptions_in_db(db, current_user)
    return subscriptions


async def delete_sub(subscribed_id, db, current_user):
    subscription = await delete_subscription_db(subscribed_id, db, current_user)
    return subscription
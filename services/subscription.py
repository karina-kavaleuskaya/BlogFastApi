from repository.subscription import (search_subscriptions_db,  get_user_subscriptions_on_db, delete_subscription_db,
                                     get_subscribed_db, check_existing_subscription_db, create_new_subscription_db,
                                     get_subscription_db)
from fastapi import status, HTTPException


async def get_user_sub_in(db, user_id):
    subscription = await search_subscriptions_db(db, user_id)
    return subscription


async def get_user_sub_on(db, current_user):
    subscriptions = await get_user_subscriptions_on_db(db, current_user)
    return subscriptions


async def create_sub(db, current_user, subscription):
    try:
        subscriber = current_user
        subscribed = await get_subscribed_db(db, subscription)
        if not subscribed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found.")

        if subscribed.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: You cannot subscribe to a banned user")

        if subscriber.id == subscription.subscribed_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You cannot subscribe to yourself.")

        existing_subscription = await check_existing_subscription_db(db, subscriber, subscription)
        if existing_subscription:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You are already subscribed to this user.")

        new_subscription = await create_new_subscription_db(db, subscriber, subscription)
        return new_subscription

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def delete_sub(db, subscribed_id, current_user):
    try:

        subscription = await get_subscription_db(db, subscribed_id, current_user)
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscription not found.")

        subscribed = await get_subscribed_db(db, subscription)
        if not subscribed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscribed user not found.")

        if subscribed.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: Cannot unsubscribe from a banned user")

        subscriptions = await delete_subscription_db(db, subscription)

        return subscriptions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

from sqlalchemy.future import select
from fastapi import status, HTTPException
import models


async def search_subscriptions(db, current_user_id):
    subscriptions = await db.execute(
        select(models.Subscription)
        .where(models.Subscription.subscribed_id == current_user_id)
        .where(~models.Subscription.subscriber.has(banned_is=True))
    )
    subscriptions = subscriptions.scalars().all()
    return subscriptions


async def create_subscription_db(db, current_user, subscription):
    try:
        subscriber = current_user

        if subscriber.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: Banned users cannot subscribe")

        subscribed = await db.get(models.User, subscription.subscribed_id)
        if not subscribed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found.")

        if subscribed.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: You cannot subscribe to a banned user")

        if subscriber.id == subscription.subscribed_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You cannot subscribe to yourself.")

        existing_subscription = await db.get(models.Subscription, (subscriber.id, subscription.subscribed_id))
        if existing_subscription:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail="You are already subscribed to this user.")

        new_subscription = models.Subscription(
            subscriber_id=subscriber.id,
            subscribed_id=subscription.subscribed_id
        )
        db.add(new_subscription)

        await db.commit()
        await db.refresh(new_subscription)

        return new_subscription

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_user_subscriptions_on_db(db, current_user):
    try:
        if current_user.banned_is == True:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        subscriptions = await db.execute(
            select(models.Subscription)
            .where(models.Subscription.subscriber_id == current_user.id)
            .where(~models.Subscription.subscribed.has(banned_is=True))
        )
        subscriptions = subscriptions.scalars().all()

        return subscriptions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def get_user_subscriptions_in_db(db, current_user):
    try:
        if current_user.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        subscriptions = await search_subscriptions(db, current_user.id)

        return subscriptions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


async def delete_subscription_db(subscribed_id, db, current_user):
    try:
        subscriber = current_user

        if subscriber.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: Banned users cannot unsubscribe")

        subscribed = await db.get(models.User, subscribed_id)
        if not subscribed:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscribed user not found.")

        if subscribed.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: Cannot unsubscribe from a banned user")

        subscription = await db.get(models.Subscription, {"subscriber_id": subscriber.id, "subscribed_id": subscribed_id})
        if not subscription:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Subscription not found.")

        if subscription.subscriber_id != subscriber.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Forbidden: You are not the subscriber of this subscription")

        await db.delete(subscription)
        await db.commit()

        return subscription

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
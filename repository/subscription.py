from sqlalchemy.future import select
import models


async def search_subscriptions(db, current_user):
    subscriptions = await db.execute(
        select(models.Subscription)
        .where(models.Subscription.subscribed_id == current_user.id)
        .where(~models.Subscription.subscriber.has(banned_is=True))
    )
    subscriptions = subscriptions.scalars().all()
    return subscriptions


async def get_user_subscriptions_on_db(db, current_user):

        subscriptions = await db.execute(
            select(models.Subscription)
            .where(models.Subscription.subscriber_id == current_user.id)
            .where(~models.Subscription.subscribed.has(banned_is=True))
        )
        subscriptions = subscriptions.scalars().all()

        return subscriptions


async def get_subscribed(db, subscription):
    subscribed = await db.get(models.User, subscription.subscribed_id)
    return subscribed


async def get_subscription(subscribed_id, current_user, db):
    subscription = await db.get(models.Subscription, {"subscriber_id": current_user.id, "subscribed_id": subscribed_id})
    return subscription


async def check_existing_subscription(db, subscriber, subscription):
    existing_subscription = await db.get(models.Subscription, (subscriber.id, subscription.subscribed_id))
    return existing_subscription


async def create_new_subscription(db, subscriber, subscription):
    new_subscription = models.Subscription(
        subscriber_id=subscriber.id,
        subscribed_id=subscription.subscribed_id
    )
    db.add(new_subscription)

    await db.commit()
    await db.refresh(new_subscription)

    return new_subscription


async def delete_subscription(db, subscription):
    try:
        await db.delete(subscription)
        await db.commit()
    except Exception as e:
        raise e
    return subscription
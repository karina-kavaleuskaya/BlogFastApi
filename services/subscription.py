from sqlalchemy.future import select
import models


async def search_subscriptions(db, current_user_id):
    subscriptions = await db.execute(
        select(models.Subscription)
        .where(models.Subscription.subscribed_id == current_user_id)
        .where(~models.Subscription.subscriber.has(banned_is=True))
    )
    return subscriptions.scalars().all()
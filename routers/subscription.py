import models
from schemas import posts
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from sqlalchemy.future import select
from fastapi import HTTPException, status, Depends, APIRouter
from services.auth import get_current_user
import schemas
from services.subscription import search_subscriptions

router = APIRouter(
    prefix='/subscriptions',
    tags=['Subscriptions']
)


@router.post("/", response_model=schemas.posts.SubscriptionCreate)
async def create_subscription(
        subscription: schemas.posts.SubscriptionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)):
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


@router.get('/outgoing/{user_id}', response_model=List[schemas.posts.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user)
):
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


@router.get('/incoming/{user_id}', response_model=List[schemas.posts.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user)
):
    try:

        if current_user.banned_is:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

        subscriptions = await search_subscriptions(db, current_user.id)

        return subscriptions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{subscribed_id}", response_model=schemas.posts.Subscription)
async def delete_subscription(
        subscribed_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)):
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
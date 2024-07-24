from schemas import subscription, users
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from fastapi import Depends, APIRouter, status, HTTPException
from services.auth import get_current_user
from services.subscription import create_sub, get_user_sub_on, delete_sub, get_user_sub_in
import models


router = APIRouter(
    prefix='/subscriptions',
    tags=['Subscriptions']
)


@router.post("/", response_model=subscription.SubscriptionCreate)
async def create_subscription(
        subscription: subscription.SubscriptionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: users.User = Depends(get_current_user)):

    if current_user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden: Banned users cannot subscribe")

    new_subscription = await create_sub(db, current_user, subscription)
    return new_subscription


@router.get('/outgoing/{user_id}', response_model=List[subscription.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: users.User = Depends(get_current_user)
):
    if current_user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    subscriptions = await get_user_sub_on(db, current_user)
    return subscriptions


@router.get('/incoming/{user_id}', response_model=List[subscription.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: users.User = Depends(get_current_user)
):
    if current_user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    subscriptions = await get_user_sub_in(db, current_user)
    return subscriptions


@router.delete("/{subscribed_id}", response_model=subscription.SubscriptionCreate)
async def delete_subscription(
        subscribed_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: users.User = Depends(get_current_user)):

    if current_user.banned_is:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Forbidden: Banned users cannot subscribe")

    subscriptions = await delete_sub(db, subscribed_id, current_user)
    return subscriptions

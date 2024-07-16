from schemas import posts
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from db.async_db import get_db
from fastapi import Depends, APIRouter
from services.auth import get_current_user
import schemas
from services.subscription import create_sub, get_user_sub_on, get_user_sub_in, delete_sub


router = APIRouter(
    prefix='/subscriptions',
    tags=['Subscriptions']
)


@router.post("/", response_model=schemas.posts.SubscriptionCreate)
async def create_subscription(
        subscription: schemas.posts.SubscriptionCreate,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)):

    new_subscription = await create_sub(db, current_user, subscription)
    return new_subscription


@router.get('/outgoing/{user_id}', response_model=List[schemas.posts.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user)
):
    subscriptions = await get_user_sub_on(db, current_user)
    return subscriptions


@router.get('/incoming/{user_id}', response_model=List[schemas.posts.Subscription])
async def get_user_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user: schemas.users.User = Depends(get_current_user)
):
    subscriptions = await get_user_sub_in(db, current_user)
    return subscriptions


@router.delete("/{subscribed_id}", response_model=schemas.posts.Subscription)
async def delete_subscription(
        subscribed_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: schemas.users.User = Depends(get_current_user)):

    subscription = await delete_sub(subscribed_id, db, current_user)
    return subscription

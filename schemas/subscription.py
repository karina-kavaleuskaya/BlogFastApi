from pydantic import BaseModel


class Subscription(BaseModel):
    subscriber_id: int
    subscribed_id: int


class SubscriptionCreate(BaseModel):
    subscribed_id: int

    class Config:
        from_attributes = True